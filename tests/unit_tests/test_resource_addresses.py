import os

from doxhooks.errors import DoxhooksDataError
from doxhooks.resource_addresses import ResourceAddress
from pytest import fail, mark

from doxhooks_pytest import withraises


class FakeOutputFileDomain:
    filename = None

    def __init__(self, branch):
        self.branch = branch


class FakeFileTree:
    def path(self, branch, *args, **kwargs):
        return branch


class BaseTestResourceAddress:
    id = "test_id"
    fake_filetree = FakeFileTree()

    prefix = ""
    path = "test/default.dat"
    root = None
    default_url = "/" + path
    defined_url = "example.com/defined"
    predefined_url = "example.com/predefined"

    def given_the_url_field_of_a_resource(
            self, *, prefix=None, path=None, root=None):
        self.urls = {}
        self.address = ResourceAddress(
            self.id,
            FakeOutputFileDomain(
                self.path if path is None else path),
            self.fake_filetree,
            "dummy_rewrite",
            self.root if root is None else root,
            self.prefix if prefix is None else prefix,
            self.urls,
        )

    given_the_uninitialised_url_field_of_a_resource = \
        given_the_url_field_of_a_resource

    def and_a_url_is_not_predefined_for_that_resource(self):
        assert self.id not in self.urls

    def and_a_predefined_url_for_that_resource(self):
        self.urls[self.id] = self.predefined_url

    def when_accessing_the_value_of_the_url(self):
        self.url = self.address.access()

    and_the_url_has_been_accessed = when_accessing_the_value_of_the_url

    @withraises
    def when_defining_the_value_of_the_url(self, url):
        self.address.define(url)

    and_the_url_has_been_defined = when_defining_the_value_of_the_url

    def when_defining_the_value_of_the_url_then_an_error_is_not_raised(
            self, url):
        try:
            self.address.define(url)
        except RuntimeError:
            fail("Saving the database should not raise an error.")

    @withraises
    def when_computing_the_default_url(self):
        self.url = self.address.leak_default()


class TestUndefinedURL(BaseTestResourceAddress):
    def given_the_undefined_url_field_of_a_resource(self):
        self.given_the_uninitialised_url_field_of_a_resource()
        self.and_a_url_is_not_predefined_for_that_resource()

    def test_accessing_an_undefined_url_field_adds_the_default_url_to_the_dict(
            self):
        self.given_the_undefined_url_field_of_a_resource()

        self.when_accessing_the_value_of_the_url()

        # then the default URL is added to the URL dictionary.
        assert self.urls[self.id] == self.default_url

    def test_accessing_an_undefined_url_field_returns_the_default_url(self):
        self.given_the_undefined_url_field_of_a_resource()

        self.when_accessing_the_value_of_the_url()

        # then the default URL is returned.
        assert self.url == self.default_url

    def test_redefining_a_default_url_with_a_different_url_is_an_error(self):
        self.given_the_undefined_url_field_of_a_resource()
        self.and_the_url_has_been_accessed()

        self.when_defining_the_value_of_the_url(
            self.defined_url, raises=RuntimeError)

        assert self.error

    def test_redefining_a_default_url_with_the_same_url_is_not_an_error(self):
        self.given_the_undefined_url_field_of_a_resource()
        self.and_the_url_has_been_accessed()

        self.when_defining_the_value_of_the_url_then_an_error_is_not_raised(
            self.default_url)


class TestDefinedURL(BaseTestResourceAddress):
    def given_the_defined_url_field_of_a_resource(self):
        self.given_the_uninitialised_url_field_of_a_resource()
        self.and_a_url_is_not_predefined_for_that_resource()
        self.and_the_url_has_been_defined(self.defined_url)

    def test_defining_a_url_field_adds_the_defined_url_to_the_dictionary(self):
        self.given_the_uninitialised_url_field_of_a_resource()
        self.and_a_url_is_not_predefined_for_that_resource()

        self.when_defining_the_value_of_the_url(self.defined_url)

        # then the defined URL is added to the URL dictionary.
        assert self.urls[self.id] == self.defined_url

    def test_accessing_a_defined_url_field_returns_the_defined_url(self):
        self.given_the_defined_url_field_of_a_resource()

        self.when_accessing_the_value_of_the_url()

        # then the defined URL is returned.
        assert self.url == self.defined_url

    def test_redefining_a_defined_url_with_a_different_url_is_an_error(self):
        self.given_the_defined_url_field_of_a_resource()

        self.when_defining_the_value_of_the_url(
            "a_different_url", raises=RuntimeError)

        assert self.error

    def test_redefining_a_defined_url_with_the_same_url_is_not_an_error(self):
        self.given_the_defined_url_field_of_a_resource()

        self.when_defining_the_value_of_the_url_then_an_error_is_not_raised(
            self.defined_url)


class TestPredefinedURL(BaseTestResourceAddress):
    def given_the_predefined_url_field_of_a_resource(self):
        self.given_the_uninitialised_url_field_of_a_resource()
        self.and_a_predefined_url_for_that_resource()

    def test_accessing_an_predefined_url_field_returns_the_predefined_url(
            self):
        self.given_the_predefined_url_field_of_a_resource()

        self.when_accessing_the_value_of_the_url()

        # then the predefined URL is returned.
        assert self.url == self.predefined_url

    def test_redefining_a_predefined_url_with_a_different_url_is_an_error(
            self):
        self.given_the_predefined_url_field_of_a_resource()

        self.when_defining_the_value_of_the_url(
            self.defined_url, raises=RuntimeError)

        assert self.error

    def test_redefining_a_predefined_url_with_the_same_url_is_not_an_error(
            self):
        self.given_the_predefined_url_field_of_a_resource()

        self.when_defining_the_value_of_the_url_then_an_error_is_not_raised(
            self.predefined_url)


class TestDefaultURL(BaseTestResourceAddress):
    @mark.parametrize(
        "prefix, path, url", [
            ("", "one/test.dat", "/one/test.dat"),
            ("example.com", "one/test.dat", "example.com/one/test.dat"),
        ])
    def test_the_default_url_starts_with_an_optional_domain_name(
            self, prefix, path, url):
        self.given_the_url_field_of_a_resource(prefix=prefix, path=path)

        self.when_computing_the_default_url()

        # then the default URL starts with the domain name.
        assert self.url == url

    @mark.parametrize(
        "path, server_root, url", [
            ("/one/test.dat", None, "/one/test.dat"),
            ("one/test.dat", None, "/one/test.dat"),
            (mark.skipif(os.sep != "\\", reason="Windows backslash separator")
                (("one\\test.dat", None, "/one/test.dat"))),
            ("one/test.dat", "", "/one/test.dat"),
            ("one/test.dat", os.curdir, "/one/test.dat"),
            ("one/test.dat", "one", "/test.dat"),
        ])
    def test_the_absolute_path_in_the_default_url_is_relative_to_a_server_root(
            self, path, server_root, url):
        self.given_the_url_field_of_a_resource(path=path, root=server_root)

        self.when_computing_the_default_url()

        # then the default (absolute) URL derives from the output-file
        # path relative to the server root.
        assert self.url == url

    @mark.parametrize(
        "path, root", [
            ("../test.dat", None),
            ("one/test.dat", "one/two"),
            ("test.dat", "one"),
        ])
    def test_a_relative_path_in_the_default_url_is_an_error(self, path, root):
        self.given_the_url_field_of_a_resource(path=path, root=root)

        self.when_computing_the_default_url(raises=DoxhooksDataError)

        assert self.error
