"""
Make an ordered dictionary from attributes in a class definition.

Exports
-------
OrderedDictFromClass
    Make an ordered dictionary from attributes in a class definition.


.. testsetup::

    import collections
"""


from collections import OrderedDict


__all__ = [
    "OrderedDictFromClass",
]


class OrderedDictFromClass(type):
    """
    Make an ordered dictionary from attributes in a class definition.

    `OrderedDictFromClass` extends `type`.

    The name used in the class definition is bound to a new instance of
    `collections.OrderedDict`. The dictionary keys are the class
    attribute names that do not start with an underscore. The order of
    the keys is the same as the statement order of the attributes in the
    class definition. The dictionary values are the corresponding class
    attribute values.

    Example
    -------
    >>> from doxhooks.metaclasses import OrderedDictFromClass
    >>> class my_ordered_dict(metaclass=OrderedDictFromClass):
    ...     one = "value one"
    ...     two = "value two"
    ...     _three = "an omitted value"
    ...     four = "value four"
    ...
    >>> isinstance(my_ordered_dict, collections.OrderedDict)
    True
    >>> for key, value in my_ordered_dict.items():
    ...     key, value
    ('one', 'value one')
    ('two', 'value two')
    ('four', 'value four')

    Magic Methods
    -------------
    __prepare__
        Override `type.__prepare__` by returning an ordered dictionary.
    __new__
        Override `type.__new__` by returning the ordered dictionary.
    """

    def __prepare__(name, bases):
        """
        Return a new instance of `~collections.OrderedDict`.

        Overrides `type.__prepare__`.

        Returns
        -------
        ~collections.OrderedDict
            A new ordered dictionary.
        """
        return OrderedDict()

    def __new__(mcls, name, bases, ordered_dict):
        """
        Return an ordered dictionary of public attributes of the class.

        Overrides `type.__new__`.

        Returns
        -------
        ~collections.OrderedDict
            The ordered dictionary.
        """
        private_keys = [key for key in ordered_dict if key.startswith("_")]
        for private_key in private_keys:
            del ordered_dict[private_key]

        return ordered_dict
