from collections import OrderedDict

from doxhooks.metaclasses import OrderedDictFromClass


class TestOrderedDictFromClass:
    def when_using_a_class_definition_to_make_an_ordered_dictionary(self):
        class ClassName(metaclass=OrderedDictFromClass):
            a = 1
            b = 2
            _c = 3
            d = 4

        self.class_name = ClassName

    def test_the_class_name_is_bound_to_a_new_ordered_dict(self):
        self.when_using_a_class_definition_to_make_an_ordered_dictionary()

        # then the class name is bound to a new ordered dictionary.
        assert isinstance(self.class_name, OrderedDict)

    def test_the_ordered_dict_keys_are_the_class_public_attribute_names(self):
        self.when_using_a_class_definition_to_make_an_ordered_dictionary()

        # then the keys are the class attribute names that don't start
        # with an underscore.
        keys = set(self.class_name.keys())
        assert keys == {"a", "b", "d"}

    def test_the_ordered_dict_values_are_the_class_public_attr_values(self):
        self.when_using_a_class_definition_to_make_an_ordered_dictionary()

        # then each value is the corresponding class attribute value.
        assert self.class_name["a"] == 1
        assert self.class_name["b"] == 2
        assert self.class_name["d"] == 4

    def test_the_dict_items_are_ordered_in_the_class_statement_order(self):
        self.when_using_a_class_definition_to_make_an_ordered_dictionary()

        # then the key order is the statement order of the class
        # attributes.
        keys = list(self.class_name.keys())
        assert keys == ["a", "b", "d"]
