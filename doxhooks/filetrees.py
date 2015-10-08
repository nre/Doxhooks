"""
File trees with named root paths.

A `file tree`:term: computes paths with optional *root names* replaced
by root paths. Roots are chained by starting a root with the name of
another root.

A `normalised path <normalise_path>` is an absolute path or an
explicitly relative path.

Exports
-------
FileTree
    A file tree with named root paths.
normalise_path
    Return a path as a normalised absolute or explicitly relative path.


.. testsetup::

    import doxhooks.filetrees, os, posixpath
    os_path = os.path
    os.path = posixpath
    os.sep = os.path.sep
    os.curdir = os.path.curdir

.. testcleanup::

    os.path = os_path
    os.sep = os.path.sep
    os.curdir = os.path.curdir
"""


import os
import re

from doxhooks.errors import DoxhooksDataError, DoxhooksLookupError


__all__ = [
    "FileTree",
    "normalise_path",
]


_starts_with_sep = re.compile(r"[\\/]" if os.name == "nt" else "/").match

_is_explicit_relative_path = re.compile(
    r"\.$|\.[\\/]" if os.name == "nt" else r"\.$|\./"
).match


def normalise_path(path):
    """
    Return a path as a normalised absolute or explicitly relative path.

    `normalise_path` extends `os.path.normpath` by returning an
    implicitly relative path as an explicitly relative path.

    Parameters
    ----------
    path : str
        A path.

    Returns
    -------
    str
        The normalised path. The path is either absolute or explicitly
        relative.

    Examples
    --------
    >>> doxhooks.filetrees.normalise_path("films/heat.html")
    './films/heat.html'
    >>> doxhooks.filetrees.normalise_path("./films/heat.html")
    './films/heat.html'
    >>> doxhooks.filetrees.normalise_path("/films/heat.html")
    '/films/heat.html'
    """
    os_norm_path = os.path.normpath(path)

    if os.path.isabs(os_norm_path) or _is_explicit_relative_path(os_norm_path):
        return os_norm_path
    else:
        return "{}{}{}".format(os.curdir, os.sep, os_norm_path)


class FileTree:
    """
    A file tree with named root paths.

    Class Interface
    ---------------
    path
        Replace root names with paths and return the computed path.
    """

    def __init__(self, roots, *, name="`FileTree`"):
        """
        Initialise the file tree with named root paths.

        Roots are chained by starting a root path with the name of
        another root.

        Parameters
        ----------
        roots : dict
            Named root paths in the tree.
        name : str, optional
            Keyword-only. A name for the file tree. The name only
            appears in error messages. Defaults to ``"`FileTree`"``.
        """
        self._roots = roots
        self._name = name

    _root_notation = re.compile(r"^<(\w+)>(.*)")

    def _resolve_roots(self, match):
        # Return a path after recursively resolving root names.
        root_name, rel_path = match.groups()
        try:
            root = self._roots[root_name]
        except KeyError:
            raise DoxhooksLookupError(root_name, self._roots, self._name)

        if not rel_path:
            path = root
        elif _starts_with_sep(rel_path):
            path = root + rel_path
        else:
            path = os.path.join(root, rel_path)

        return self._root_notation.sub(self._resolve_roots, path)

    def path(self, dir_path, filename=None, *, rewrite=None):
        r"""
        Replace root names with paths and return the computed path.

        The paths `dir_path` and `filename` will be joined, unless
        `dir_path` is overridden because:

        * `filename` is an absolute path.
        * `filename` is an explicit relative path, e.g. ``"./file.txt"``.
        * `filename` starts with a root name, e.g. ``"<html>file.txt"``.

        Parameters
        ----------
        dir_path : str
            A path to a directory (or, unusually, a file). The path may
            be absolute, explicitly or implicitly relative, or start
            with a root name.
        filename : str or None, optional
            A path to a file (or, unusally, a directory). The path may
            be absolute, explicitly or implicitly relative, or start
            with a root name.
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the computed path. Defaults to ``None``, which denotes
            that the path will not be rewritten.

        Returns
        -------
        str
            The computed, normalised path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a named root cannot be found among the *roots* of this
            `FileTree`.
        ~doxhooks.errors.DoxhooksDataError
            If `rewrite` is not ``None`` and the path cannot be
            rewritten.

        Examples
        --------
        >>> ft = doxhooks.filetrees.FileTree(
        ...     {"src": "source", "html": "<src>html", "js": "<src>js"})
        >>> ft.path("source/html/films")
        './source/html/films'
        >>> dir_path = "<html>films"
        >>> ft.path(dir_path)
        './source/html/films'
        >>> ft.path(dir_path, "heat.html")
        './source/html/films/heat.html'
        >>> ft.path(dir_path, "heat{}.html", rewrite="-1995")
        './source/html/films/heat-1995.html'
        >>> ft.path(dir_path, "<js>inline.js")
        './source/js/inline.js'
        >>> ft.path(dir_path, "./relative/path")
        './relative/path'
        >>> ft.path(dir_path, "/absolute/path")
        '/absolute/path'
        """
        if (filename and (os.path.isabs(filename) or
                _is_explicit_relative_path(filename))):
            path = filename
        elif filename and self._root_notation.match(filename):
            path = self._root_notation.sub(self._resolve_roots, filename)
        else:
            full_dir_path = self._root_notation.sub(
                self._resolve_roots, dir_path)
            path = (
                full_dir_path if filename is None else
                os.path.join(full_dir_path, filename)
            )

        if rewrite is not None:
            try:
                path = path.format(rewrite)
            except (LookupError, ValueError) as error:
                raise DoxhooksDataError("Cannot rewrite path:", path) \
                    from error

        return normalise_path(path)
