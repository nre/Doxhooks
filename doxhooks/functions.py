"""
Functions that extend the built-in function `getattr`.

Exports
-------
findvalue
    Return the named attribute or contained value of an object.
importattr
    Import a module and return an attribute from that module.


.. testsetup::

    import doxhooks.functions
"""


import importlib
import re

from doxhooks.errors import (
    DoxhooksForbiddenLookupError, DoxhooksImportError, DoxhooksLookupError,
    DoxhooksValueError)


__all__ = [
    "findvalue",
    "importattr",
]


def findvalue(object, name):
    """
    Return the named attribute or contained value of an object.

    Named values are returned in the following order of preference:

    1. An attribute with that name.
    2. An attribute with that name but mangled with a trailing
       underscore.
    3. A contained value.

    Parameters
    ----------
    object
        The object whose named data is to be returned.
    name : str
        The name of the value.

    Returns
    -------
    object
        The named attribute or contained value of the object.

    Raises
    ------
    ~doxhooks.errors.DoxhooksLookupError
        If a value with that name is not found.
    ~doxhooks.errors.DoxhooksForbiddenLookupError
        If the name is private (i.e. it starts with an underscore).

    Examples
    --------
    >>> from doxhooks.functions import findvalue
    >>> class MyClass(dict):
    ...     one = 1
    ...     two_ = 2
    ...     _four = 4
    ...
    >>> my_object = MyClass()
    >>> my_object["three"] = 3
    >>> findvalue(my_object, "one")
    1
    >>> findvalue(my_object, "two")
    2
    >>> findvalue(my_object, "three")
    3
    >>> findvalue(my_object, "_four")
    Traceback (most recent call last):
        ...
    doxhooks.errors.DoxhooksForbiddenLookupError: Forbidden to look up '_four' in object.
    >>> findvalue(my_object, "five")
    Traceback (most recent call last):
        ...
    doxhooks.errors.DoxhooksLookupError: Cannot find 'five' in object.
    """
    object_ = object  # A parameter, not the built-in function.

    if name.startswith("_"):
        raise DoxhooksForbiddenLookupError(name, object_, "object")
    try:
        return getattr(object_, name)
    except AttributeError:
        try:
            return getattr(object_, name + "_")
        except AttributeError:
            try:
                return object_[name]
            except (KeyError, TypeError):
                raise DoxhooksLookupError(name, object_, "object")


def importattr(import_name):
    """
    Import a module and return an attribute from that module.

    Parameters
    ----------
    import_name : str
        The module and attribute names in dotted notation.

    Returns
    -------
    object
        The attribute value.

    Raises
    ------
    ~doxhooks.errors.DoxhooksValueError
        If `import_name` is not in valid dotted notation.
    ~doxhooks.errors.DoxhooksImportError
        If the module to be imported cannot be found.
    ~doxhooks.errors.DoxhooksLookupError
        If the imported module does not have that attribute.

    Example
    -------
    >>> doxhooks.functions.importattr("collections.OrderedDict")
    <class 'collections.OrderedDict'>
    >>> doxhooks.functions.importattr("collections.Love")
    Traceback (most recent call last):
        ...
    doxhooks.errors.DoxhooksLookupError: Cannot find 'Love' in collections.
    """
    import_pattern = r"(?P<module_name>(?:\w+\.)*\w+)\.(?P<attr_name>\w+)$"
    match = re.match(import_pattern, import_name)

    if not match:
        raise DoxhooksValueError(
            import_name, "import_name",
            "dotted notation, e.g. 'module_name.attr_name'")

    module_name, attr_name = match.group("module_name", "attr_name")

    try:
        module = importlib.import_module(module_name)
    except ImportError as error:
        if error.name == module_name:
            raise DoxhooksImportError("Cannot find module:", module_name)
        raise
    try:
        return getattr(module, attr_name)
    except AttributeError:
        raise DoxhooksLookupError(attr_name, module, module_name)
