import os

from doxhooks.errors import (
    DoxhooksImportError, DoxhooksForbiddenLookupError, DoxhooksLookupError,
    DoxhooksValueError)
from doxhooks.functions import findvalue, importattr
from pytest import mark

from doxhooks_pytest import withraises


class ExampleGetNamedValue(dict):
    pass


class BaseTestFindValue:
    name = "test_name"
    mangled_name = name + "_"
    attr_value = "test_attr_value"
    mangled_attr_value = "test_mangled_attr_value"
    item_value = "test_item_value"

    def given_an_object_and_a_name(self):
        self.object = ExampleGetNamedValue()

    def and_that_object_has_an_attribute(self, name, value):
        setattr(self.object, name, value)

    def and_that_object_has_an_item(self, name, value):
        self.object[name] = value

    @withraises
    def when_finding_a_value_with_that_name(self):
        self.value = findvalue(self.object, self.name)


class TestFindValue(BaseTestFindValue):
    def test_returns_an_attribute_with_that_name(self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(self.name, self.attr_value)

        self.when_finding_a_value_with_that_name()

        # then the value of that attribute is returned.
        assert self.value == self.attr_value

    def test_returns_an_attribute_with_a_mangled_version_of_that_name(self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(
            self.mangled_name, self.mangled_attr_value)

        self.when_finding_a_value_with_that_name()

        # then the value of that mangled attribute is returned.
        assert self.value == self.mangled_attr_value

    def test_returns_a_contained_value_with_that_name(self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_item(self.name, self.item_value)

        self.when_finding_a_value_with_that_name()

        # then the value of that item is returned.
        assert self.value == self.item_value


class TestFindValueOrderOfPreference(BaseTestFindValue):
    def test_prefers_an_exact_attribute_name_over_a_mangled_attribute_name(
            self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(self.name, self.attr_value)
        self.and_that_object_has_an_attribute(
            self.mangled_name, self.mangled_attr_value)

        self.when_finding_a_value_with_that_name()

        # then the value of the attribute with that name is returned.
        assert self.value == self.attr_value

    def test_prefers_an_attribute_over_a_contained_value_with_the_same_name(
            self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(self.name, self.attr_value)
        self.and_that_object_has_an_item(self.name, self.item_value)

        self.when_finding_a_value_with_that_name()

        # then the value of the attribute is returned.
        assert self.value == self.attr_value

    def test_prefers_a_mangled_attribute_over_a_contained_value_with_that_name(
            self):
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(
            self.mangled_name, self.mangled_attr_value)
        self.and_that_object_has_an_item(self.name, self.item_value)

        self.when_finding_a_value_with_that_name()

        # then the value of the mangled attribute is returned.
        assert self.value == self.mangled_attr_value


class TestFindValueError(BaseTestFindValue):
    def test_seeking_a_value_with_a_private_name_is_an_error(self):
        self.name = "_private_name"
        self.given_an_object_and_a_name()
        self.and_that_object_has_an_attribute(self.name, self.attr_value)

        self.when_finding_a_value_with_that_name(
            raises=DoxhooksForbiddenLookupError)

        assert self.error.key == self.name

    def test_failure_to_find_a_named_value_is_an_error(self):
        self.given_an_object_and_a_name()

        self.when_finding_a_value_with_that_name(raises=DoxhooksLookupError)

        assert self.error.key == self.name


class TestImportingAModuleAttribute:
    @withraises
    def when_importing_a_module_attribute(self, import_name):
        self.returned_attr = importattr(import_name)

    @mark.parametrize(
        "import_name, attribute", [
            ("os.sep", os.sep),
            ("os.path.sep", os.path.sep),
        ])
    def test_importing_a_module_attribute_returns_that_attribute(
            self, import_name, attribute):
        self.when_importing_a_module_attribute(import_name)

        # then the attribute value is returned.
        assert self.returned_attr == attribute

    @mark.parametrize(
        "bad_import_name", [
            "os",
            ".os", "os.",
            "..os", ".os.", "os..",
            "...os", "..os.", ".os..", "os...",
            ".os.sep", "os..sep", "os.sep.",
            "..os.sep", ".os..sep", ".os.sep.",
            "os...sep", "os..sep.", "os.sep..",
        ])
    def test_a_bad_import_name_is_an_error(self, bad_import_name):
        self.when_importing_a_module_attribute(
            bad_import_name, raises=DoxhooksValueError)

        assert self.error.value == bad_import_name

    def test_importing_a_missing_module_is_an_error(self):
        missing_module_name = "not_a_module.attr_name"
        self.when_importing_a_module_attribute(
            missing_module_name, raises=DoxhooksImportError)

        assert self.error

    def test_importing_a_missing_module_attr_is_an_error(self):
        missing_module_attr_name = "os.not_an_attr"
        self.when_importing_a_module_attribute(
            missing_module_attr_name, raises=DoxhooksLookupError)

        assert self.error.key == "not_an_attr"
