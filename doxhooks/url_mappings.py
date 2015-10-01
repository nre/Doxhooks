"""
Mappings of resource identities to URLs.

The URL of a resource can be set (`URLMapping.__setitem__`) but cannot
be changed or deleted (`URLMapping.__delitem__`).

A mapping can be loaded and saved (`URLMapping.load`,
`URLMapping.save`).

Exports
-------
URLMapping
    A mapping of resource identities to URLs.
"""


import collections

import doxhooks.dataio as dataio
from doxhooks.errors import DoxhooksDataFileError


__all__ = [
    "URLMapping",
]


class URLMapping(collections.abc.MutableMapping):
    """
    A mapping of resource identities to URLs.

    `URLMapping` extends `~collections.abc.MutableMapping`.

    The URL of a resource cannot be changed after it has been set.

    Example
    -------
    >>> from doxhooks.url_mappings import URLMapping
    >>> urls = URLMapping()
    >>> urls["example_id"] = "http://example.com/"
    >>> urls["example_id"] = "http://example.com/"
    >>> urls["example_id"] = "http://example.com/different"
    Traceback (most recent call last):
        ...
    RuntimeError: Resource 'example_id' URL cannot be changed from 'http://example.com/' to 'http://example.com/different'.
    >>> urls
    {'example_id': 'http://example.com/'}

    Class Interface
    ---------------
    load
        Replace the data with data read from a file.
    save
        Write the data to a file.

    Magic Methods
    -------------
    __setitem__
        Override `MutableMapping.__setitem__` to prevent changing a URL.
    __delitem__
        Override `MutableMapping.__delitem__` to prevent deleting a URL.
    __getitem__
        Override `MutableMapping.__getitem__` to return a URL.
    __repr__
        Override `MutableMapping.__repr__` to return a `dict`-literal
        represention.
    __iter__
        Override `MutableMapping.__iter__` to return an iterable.
    __len__
        Override `MutableMapping.__len__` to return the number of
        resource identities.
    """

    def __init__(self, *args, **kwargs):
        r"""
        Initialise the mapping.

        The `URLMapping` constructor overrides the
        `~collections.abc.MutableMapping` constructor to extend the
        `dict` constructor.

        Parameters
        ----------
        \*args
            See the `dict` constructor for details.
        \**kwargs
            See the `dict` constructor for details.
        """
        self._urls = dict(*args, **kwargs)

    def __repr__(self):
        """
        Return a representation of the mapping as a `dict` literal.

        Overrides `MutableMapping.__repr__`.

        Returns
        -------
        str
            A `dict`-literal representation of the mapping.
        """
        return repr(self._urls)

    def __iter__(self):  # pragma: no cover
        """
        Return an iterable for the mapping.

        Overrides `MutableMapping.__iter__`.

        Returns
        -------
        ~collections.abc.Iterable
            An iterable for the mapping.
        """
        return iter(self._urls)

    def __len__(self):  # pragma: no cover
        """
        Return the number of resource identities in the mapping.

        Overrides `MutableMapping.__len__`.

        Returns
        -------
        int
            The number of resource identities in the mapping.
        """
        return len(self._urls)

    def __getitem__(self, resource_id):
        """
        Return the URL for a given resource.

        Overrides `MutableMapping.__getitem__`.

        Parameters
        ----------
        resource_id : ~collections.Hashable
            The resource identity.

        Returns
        -------
        str
            The resource URL.

        Raises
        ------
        KeyError
            If the resource identity is not in the mapping.
        """
        return self._urls[resource_id]

    def __setitem__(self, resource_id, url):
        """
        Set the URL for a given resource.

        Overrides `MutableMapping.__setitem__`.

        The URL of a resource cannot be changed after it has been set.
        Setting the URL to the same value again is not an error.

        Parameters
        ----------
        resource_id : ~collections.Hashable
            The resource identity.
        url : str or None
            The resource URL.

        Raises
        ------
        RuntimeError
            If the URL of a resource is changed after it has been set.
        """
        try:
            previous_url = self._urls[resource_id]
        except KeyError:
            self._urls[resource_id] = url
            return
        if url != previous_url:
            raise RuntimeError(
                "Resource {!r} URL cannot be changed from {!r} to {!r}."
                .format(resource_id, previous_url, url))

    def __delitem__(self, resource_id):
        """
        Raise `RuntimeError` instead of deleting a resource URL.

        Overrides `MutableMapping.__delitem__`.

        Raises
        ------
        RuntimeError
            Unconditionally.
        """
        raise RuntimeError(
            "Resource {!r} URL cannot be deleted.".format(resource_id))

    def load(self, path):
        """
        Replace the data with data read from a file.

        Parameters
        ----------
        path : str
            The path to the file.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If the data file cannot be read.
        ~doxhooks.errors.DoxhooksDataFileError
            If the data file does not contain valid data.
        """
        data = dataio.load_literals(path)
        if not isinstance(data, dict):
            raise DoxhooksDataFileError("Bad URL-data file:", path)
        self._urls = dict(data)

    def save(self, path):
        """
        Write the data to a file.

        The data can be saved if the resource identity and URL values in
        the mapping are Python-literal types. The recommended
        resource-identity types are `str`, `int` and `tuple`.  (The
        other types that can be saved are `bytes`, `bool`, `float`,
        `complex` and ``None``). The recommended URL types are `str` and
        ``None``.

        Parameters
        ----------
        path : str
            The path to the file.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the types of values in the mapping are not Python-literal
            types.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be saved.
        """
        dataio.save_literals(path, self._urls)
