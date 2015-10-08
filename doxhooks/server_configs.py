"""
Configurations for mapping URLs to files on servers.

A server is configured to map URLs to information resources, especially
files on the server. A URL may comprise a protocol
(`ServerConfiguration.protocol`), a host name
(`ServerConfiguration.hostname`) and an absolute path. The server
interprets this absolute path as a path relative to a directory on the
server (`ServerConfiguration.root`).

The inverse of this mapping gives the URL for a file on the server
(`ServerConfiguration.url_for_file`). The server may rewrite the URL
(`ServerConfiguration.rewrite`, see `doxhooks.filetrees.FileTree.path`
for details).

Exports
-------
ServerConfiguration
    A configuration for mapping URLs to files on a server.
"""


import os

from doxhooks.errors import DoxhooksDataError


__all__ = [
    "ServerConfiguration",
]


class ServerConfiguration:
    """
    A configuration for mapping URLs to files on a server.

    Class Interface
    ---------------
    url_for_file
        Return the URL for a file.
    """

    def __init__(
            self, filetree, protocol=None, hostname=None, root=None,
            rewrite=None):
        """
        Initialise the server configuration.

        Parameters
        ----------
        filetree : ~doxhooks.filetrees.FileTree
            A file tree with named output/URL-root paths.
        protocol : str or None, optional
            The protocol (*scheme*, e.g. ``"http://"``, ``"//"``) in the
            URLs. ``None`` denotes the empty string. Defaults to
            ``None``.
        hostname : str or None, optional
            The host name (*domain name*) in the URLs. ``None`` denotes
            root-relative URLs. Defaults to ``None``.
        root : str or None, optional
            The path on the server that the URL path is relative to.
            ``None`` denotes the root directory on the server. Defaults
            to ``None``.
        rewrite : optional
            A value that replaces a substring ``"{}"`` in the file path.
            ``None`` denotes that the path will not be rewritten.
            Defaults to ``None``.

        Attributes
        ----------
        protocol : str or None
            The argument of `protocol`.
        hostname : str or None
            The argument of `hostname`.
        root : str or None
            The argument of `root`.
        rewrite : str or None
            The argument of `rewrite`.
        """
        self._filetree = filetree
        self.protocol = protocol
        self.hostname = hostname
        self.root = root
        self.rewrite = rewrite

    def url_for_file(self, dir_path, filename=None):
        """
        Return the URL for a file.

        Parameters
        ----------
        dir_path : str
            See `doxhooks.filetrees.FileTree.path` for details.
        filename : str or None, optional
            See `doxhooks.filetrees.FileTree.path` for details.

        Returns
        -------
        str
            The URL for the file.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the URL cannot be computed.
        """
        path = self._filetree.path(dir_path, filename, rewrite=self.rewrite)

        if self.root is not None:
            root_path = self._filetree.path(self.root)
            path = os.path.relpath(path, root_path)

        norm_path = os.path.normpath(os.path.splitdrive(path)[1])

        if norm_path.startswith(os.pardir):
            raise DoxhooksDataError(
                "URL path starts with {!r}: {!r}".format(os.pardir, norm_path))

        slash_path = norm_path.replace(os.sep, "/")

        return "{}{}/{}".format(
            self.protocol if self.protocol is not None else "",
            self.hostname if self.hostname is not None else "",
            "" if slash_path == os.curdir else slash_path.lstrip("/"),
        )
