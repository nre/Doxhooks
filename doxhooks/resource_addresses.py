# TODO: A DefaultURL class can be refactored out of ResourceAddress.
"""
Address (URL) fields for information resources.

The address field of a resource can be accessed
(`ResourceAddress.access`) and defined (`ResourceAddress.define`), but
not mutated. The default address of the resource can be obtained without
setting the field (`ResourceAddress.leak_default`).

Exports
-------
ResourceAddress
    The immutable address (URL) field of a resource.
"""


import os

from doxhooks.errors import DoxhooksDataError


__all__ = [
    "ResourceAddress",
]


class ResourceAddress:
    """
    The immutable address (URL) field of a resource.

    Class Interface
    ---------------
    access
        Return the address (URL) of the resource.
    define
        Set the address (URL) of the resource.
    leak_default
        Compute and return the default URL without setting the address.
    """

    def __init__(
            self, resource_id, urls, output_filetree, prefix, root, rewrite):
        """
        Initialise the address field with data about the resource.

        Parameters
        ----------
        resource_id : ~collections.Hashable
            The identity of the resource.
        urls : dict
            A dictionary of resource identities and URLs.
        filetree : ~doxhooks.filetrees.OutputFileTree
            The output-file tree of the resource.
        prefix : str
            The domain name (and optionally the scheme name and port
            number) that the default URL starts with.
        root : str or None
            The path to a server root directory. The absolute path in
            the default URL derives from the output-file path relative
            to this path.
        rewrite
            A value that replaces a substring ``"{}"`` in the filename
            in the default URL. ``None`` denotes that the filename will
            not be rewritten.
        """
        self._resource_id = resource_id
        self._urls = urls
        self._filetree = output_filetree
        self._prefix = prefix
        self._root = root
        self._rewrite = rewrite

    def _compute_default(self):
        # Compute and return the default, absolute URL.
        path = self._filetree.url_path(rewrite=self._rewrite)
        if self._root is not None:
            path = os.path.normpath(os.path.relpath(path, self._root))
        if path.startswith(os.pardir):
            raise DoxhooksDataError(
                "Resource {!r} URL path starts with {!r}: {!r}"
                .format(self._resource_id, os.pardir, path))
        slash_path = path.replace(os.sep, "/")
        return "{}/{}".format(self._prefix, slash_path.lstrip("/"))

    def leak_default(self):
        """
        Compute and return the default URL without setting the address.

        Returns
        -------
        str
            The default URL of the resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the URL cannot be computed.
        """
        return self._compute_default()

    def access(self):
        """
        Return the address (URL) of the resource.

        URLs are returned in the following order of preference:

        1. A URL that was stored in the field by `self.define`.
        2. A URL that is defined for this resource in the *dictionary of
           URLs* of this `ResourceAddress`. A side effect of accessing
           this URL is that it is stored in this field.
        3. The default URL for this resource. The side effects of
           accessing this URL are that it is added to the *dictionary of
           URLs* of this `ResourceAddress` and that it is stored in this
           field.

        Returns
        -------
        str
            The URL of the resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the URL cannot be returned.
        """
        try:
            protected_url = self._url
        except AttributeError:
            try:
                protected_url = self._urls[self._resource_id]
            except KeyError:
                protected_url = self._compute_default()
                self._urls[self._resource_id] = protected_url
            self._url = protected_url
        return protected_url

    def _update_dict(self, url):
        # Update the URL dictionary.
        try:
            dict_url = self._urls[self._resource_id]
        except KeyError:
            self._urls[self._resource_id] = url
        else:
            if dict_url != url:
                raise RuntimeError(
                    "Resource {!r} URL changed from {!r} to {!r}."
                    .format(self._resource_id, dict_url, url))

    def define(self, url):
        """
        Set the address (URL) of the resource.

        A side effect of defining the URL is that this URL is added to
        the *dictionary of URLs* of this `ResourceAddress`.

        Parameters
        ----------
        url : str
            The URL of the resource.

        Raises
        ------
        RuntimeError
            If a different URL has already been defined by
            `self.define`, or accessed by `self.access` or defined in
            the *dictionary of URLs* of this `ResourceAddress`.
        """
        try:
            protected_url = self._url
        except AttributeError:
            self._update_dict(url)
            self._url = url
        else:
            if url != protected_url:
                raise RuntimeError(
                    "Resource {!r} URL changed from {!r} to {!r}."
                    .format(self._resource_id, protected_url, url))
