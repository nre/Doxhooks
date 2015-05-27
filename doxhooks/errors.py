"""
The hierarchy of Doxhooks exceptions.

All Doxhooks exceptions derive from `DoxhooksError`, which derives from
`Exception`. Exceptional conditions can arise when Doxhooks is handling
input data (`DoxhooksDataError`) or files (`DoxhooksFileError`).

Doxhooks Exception Hierarchy
****************************

* `Exception`
    * `DoxhooksError`
        * `DoxhooksDataError`
            * `DoxhooksImportError`
            * `DoxhooksLookupError`
                * `DoxhooksForbiddenLookupError`
            * `DoxhooksTypeError`
            * `DoxhooksValueError`
        * `DoxhooksFileError`
            * `DoxhooksDataFileError`
            * `DoxhooksFileSystemError`
            * `DoxhooksOutputPathError`


Exports
-------
DoxhooksError
    All Doxhooks exceptions derive from this exception.
DoxhooksDataError
    All input-data exceptions derive from this exception.
DoxhooksImportError
    A module is not imported because it cannot be found.
DoxhooksLookupError
    An index or key is not found in the specified container.
DoxhooksForbiddenLookupError
    An index or key is private.
DoxhooksTypeError
    An argument or value is not of the specified type.
DoxhooksValueError
    An argument or value is a bad value but of the specified type.
DoxhooksFileError
    All file exceptions derive from this exception.
DoxhooksDataFileError
    The contents of a data file are not valid data.
DoxhooksFileSystemError
    A file or directory is missing, private or unavailable.
DoxhooksOutputPathError
    An output path does not branch off any of the output roots.
"""


__all__ = [
    "DoxhooksError",
    "DoxhooksDataError",
    "DoxhooksDataFileError",
    "DoxhooksFileError",
    "DoxhooksFileSystemError",
    "DoxhooksForbiddenLookupError",
    "DoxhooksImportError",
    "DoxhooksLookupError",
    "DoxhooksTypeError",
    "DoxhooksValueError",
]


class DoxhooksError(Exception):
    """
    All Doxhooks exceptions derive from this exception.

    `DoxhooksError` extends `Exception`.

    Magic Methods
    -------------
    __str__
        Override `Exception.__str__` to compose a message.
    """

    def __str__(self):
        """
        Return an error message composed from the constructor arguments.

        Overrides `Exception.__str__`.

        Returns
        -------
        str
            The error message.

        Example
        -------
        >>> from doxhooks.errors import DoxhooksError
        >>> str(DoxhooksError("example", 1, 2, 3))
        'example 1 2 3'
        """
        return " ".join(map(str, self.args))


class DoxhooksDataError(DoxhooksError):
    """
    All input-data exceptions derive from this exception.

    `DoxhooksDataError` extends `DoxhooksError`.
    """


class DoxhooksImportError(DoxhooksDataError):
    """
    A module is not imported because it cannot be found.

    `DoxhooksImportError` extends `DoxhooksDataError`.
    """


class DoxhooksLookupError(DoxhooksDataError):
    """
    An index or key is not found in the specified container.

    `DoxhooksLookupError` extends `DoxhooksDataError`.

    Magic Methods
    -------------
    __str__
        Override `DoxhooksDataError.__str__` to compose a message.
    """

    def __init__(self, key, container, description):
        """
        Initialise the error with parameters of the error message.

        The `DoxhooksLookupError` constructor overrides the
        `DoxhooksDataError` constructor with parameters of the error
        message.

        Parameters
        ----------
        key : ~collections.abc.Hashable
            The index or key that was not found.
        container : ~collections.abc.Container
            The container that the index or key was not found in.
        description : str
            A description of the container for the user.

        Attributes
        ----------
        key : ~collections.abc.Hashable
            The argument of `key`.
        container : ~collections.abc.Container
            The argument of `container`.
        description : str
            The argument of `description`.
        """
        self.key = key
        self.container = container
        self.description = description

    def __str__(self):
        """
        Return an error message composed from the error attributes.

        Overrides `DoxhooksDataError.__str__`.

        Returns
        -------
        str
            The error message.

        Example
        -------
        >>> from doxhooks.errors import DoxhooksLookupError
        >>> str(DoxhooksLookupError(0, [], "`my_list`"))
        'Cannot find 0 in `my_list`.'
        >>> str(DoxhooksLookupError("my_key", {}, "`my_dict`"))
        "Cannot find 'my_key' in `my_dict`."
        """
        return "Cannot find {!r} in {}.".format(self.key, self.description)


class DoxhooksForbiddenLookupError(DoxhooksLookupError):
    """
    An index or key is private.

    `DoxhooksForbiddenLookupError` extends `DoxhooksLookupError`.

    Magic Methods
    -------------
    __str__
        Override `DoxhooksLookupError.__str__` to compose a message.
    """

    def __str__(self):
        """
        Return an error message composed from the error attributes.

        Overrides `DoxhooksLookupError.__str__`.

        Returns
        -------
        str
            The error message.

        Example
        -------
        >>> from doxhooks.errors import DoxhooksForbiddenLookupError
        >>> str(DoxhooksForbiddenLookupError("_private_key", {}, "`my_dict`"))
        "Forbidden to look up '_private_key' in `my_dict`."
        """
        return "Forbidden to look up {!r} in {}.".format(
            self.key, self.description)


class DoxhooksTypeError(DoxhooksDataError):
    """
    An argument or value is not of the specified type.

    `DoxhooksTypeError` extends `DoxhooksDataError`.

    Magic Methods
    -------------
    __str__
        Override `DoxhooksDataError.__str__` to compose a message.
    """

    def __init__(self, value, identifier, hint):
        """
        Initialise the error with parameters of the error message.

        The `DoxhooksTypeError` constructor overrides the
        `DoxhooksDataError` constructor with parameters of the error
        message.

        Parameters
        ----------
        value
            The value that caused the error.
        identifier : str
            An identifier that the user associates with the value.
        hint : str, type or Tuple[type, ...]
            A hint as to the expected type.

        Attributes
        ----------
        value
            The argument of `value`.
        identifier : str
            The argument of `identifier`.
        hint : str, type or Tuple[type, ...]
            The argument of `hint`.
        """
        self.value = value
        self.identifier = identifier
        self.hint = hint

    def __str__(self):
        """
        Return an error message composed from the error attributes.

        Overrides `DoxhooksDataError.__str__`.

        Returns
        -------
        str
            The error message.

        Examples
        --------
        >>> from doxhooks.errors import DoxhooksTypeError
        >>> str(DoxhooksTypeError(1, "my_arg", str))
        'Bad type for `my_arg`: int. (Should be str.)'
        >>> str(DoxhooksTypeError(1, "my_arg", (str, type(None))))
        'Bad type for `my_arg`: int. (Should be str, NoneType.)'
        >>> str(DoxhooksTypeError(1, "my_arg", "str or None"))
        'Bad type for `my_arg`: int. (Should be str or None.)'
        """
        hint = self.hint
        if isinstance(hint, type):
            type_hint = hint.__name__
        elif hint == ():
            type_hint = "'no type'"
        elif isinstance(hint, tuple):
            type_hint = ", ".join([type_.__name__ for type_ in hint])
        else:
            type_hint = hint

        bad_type_name = type(self.value).__name__

        return ("Bad type for `{}`: {}. (Should be {}.)"
                .format(self.identifier, bad_type_name, type_hint))


class DoxhooksValueError(DoxhooksDataError):
    """
    An argument or value is a bad value but of the specified type.

    `DoxhooksValueError` extends `DoxhooksDataError`.

    Magic Methods
    -------------
    __str__
        Override `DoxhooksDataError.__str__` to compose a message.
    """

    def __init__(self, value, identifier, hint=None):
        """
        Initialise the error with parameters of the error message.

        The `DoxhooksValueError` constructor overrides the
        `DoxhooksDataError` constructor with parameters of the error
        message.

        Parameters
        ----------
        value
            The value that caused the error.
        identifier : str
            An identifier that the user associates with the value.
        hint : optional
            A hint as to the expected value. Defaults to ``None``, which
            denotes that a hint is not applicable.

        Attributes
        ----------
        value
            The argument of `value`.
        identifier : str
            The argument of `identifier`.
        hint
            The argument of `hint`.
        """
        self.value = value
        self.identifier = identifier
        self.hint = hint

    def __str__(self):
        """
        Return an error message composed from the error attributes.

        Overrides `DoxhooksDataError.__str__`.

        Returns
        -------
        str
            The error message.

        Examples
        --------
        >>> from doxhooks.errors import DoxhooksValueError
        >>> str(DoxhooksValueError(0, "my_arg"))
        'Bad value for `my_arg`: 0.'
        >>> str(DoxhooksValueError(0, "my_arg", "greater than zero"))
        'Bad value for `my_arg`: 0. (Should be greater than zero.)'
        """
        return ("Bad value for `{}`: {!r}.{}".format(
            self.identifier, self.value,
            "" if self.hint is None else
            " (Should be {}.)".format(self.hint)))


class DoxhooksFileError(DoxhooksError):
    """
    All file exceptions derive from this exception.

    `DoxhooksFileError` extends `DoxhooksError`.
    """


class DoxhooksDataFileError(DoxhooksFileError):
    """
    The contents of a data file are not valid data.

    `DoxhooksDataFileError` extends `DoxhooksFileError`.
    """


class DoxhooksFileSystemError(DoxhooksFileError):
    """
    A file or directory is missing, private or unavailable.

    `DoxhooksFileSystemError` extends `DoxhooksFileError`.
    """


class DoxhooksOutputPathError(DoxhooksFileError):
    """
    An output path does not branch off any of the output roots.

    `DoxhooksOutputPathError` extends `DoxhooksFileError`.
    """
