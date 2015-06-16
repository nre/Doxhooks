"""
Trees with file-path branches.

A `file tree`:term: returns paths with the branch names replaced by
branch paths. Branches are chained by starting a branch with the name of
another branch.

Exports
-------
FileTree
    A tree with file-path branches.


.. testsetup::

    import doxhooks.filetrees, os, posixpath
    os_path = os.path
    os.path = posixpath

.. testcleanup::

    os.path = os_path
"""


import os
import re

from doxhooks.errors import DoxhooksDataError, DoxhooksLookupError


__all__ = [
    "FileTree",
]


class FileTree:
    """
    A tree with file-path branches.

    Class Interface
    ---------------
    path
        Substitute branch names with paths and return the computed path.
    """

    def __init__(self, branches, *, name="`branches`"):
        """
        Initialise the file tree with branches.

        Parameters
        ----------
        branches : dict
            The names and paths of the branches in the tree.
        name : str, optional
            Keyword-only. A name for the branches. The name only appears
            in error messages. Defaults to ``"`branches`"``.
        """
        self._branches = branches
        self._name = name

    _branch_notation = re.compile(r"^<(?P<branch_name>\w+)>(?P<twig>.*)")

    def _get_branch(self, match):
        # Recursively look up a branch name and return the branch value.
        branch_name, twig = match.group("branch_name", "twig")
        try:
            branch = self._branches[branch_name]
        except KeyError:
            raise DoxhooksLookupError(branch_name, self._branches, self._name)
        path = os.path.join(branch, twig)
        return self._branch_notation.sub(self._get_branch, path)

    def path(self, branch, leaf=None, *, rewrite=None):
        r"""
        Substitute branch names with paths and return the computed path.

        Branches are chained by starting a branch with the name of
        another branch.

        Parameters
        ----------
        branch : str
            A path.
        leaf : str or None, optional
            An additional path. The paths `branch` and `leaf` will be
            joined, unless `leaf` starts with a branch name, in which
            case `branch` is ignored. (This is analogous to the
            behaviour of `os.path.join` with absolute paths.)
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the path. Defaults to ``None``, which denotes that the
            path will not be rewritten.

        Returns
        -------
        str
            The computed path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a named branch cannot be found among the *branches* of
            this `FileTree`.
        ~doxhooks.errors.DoxhooksDataError
            If `rewrite` is not ``None`` and the path cannot be
            rewritten.

        Examples
        --------
        >>> ft = doxhooks.filetrees.FileTree(
        ...     {"src": "source", "html": "<src>html", "js": "<src>js"})
        >>> ft.path("source/html/films")
        'source/html/films'
        >>> ft.path("<html>films")
        'source/html/films'
        >>> ft.path("<html>films", "heat.html")
        'source/html/films/heat.html'
        >>> ft.path("<html>films", "heat{}.html", rewrite="-1995")
        'source/html/films/heat-1995.html'
        >>> ft.path("<html>films", "<js>inline.js")
        'source/js/inline.js'
        """
        if leaf and self._branch_notation.match(leaf):
            path = self._branch_notation.sub(self._get_branch, leaf)
        else:
            branch_path = self._branch_notation.sub(self._get_branch, branch)
            path = os.path.join(branch_path, leaf) if leaf else branch_path

        if rewrite is not None:
            try:
                path = path.format(rewrite)
            except (LookupError, ValueError) as error:
                raise DoxhooksDataError("Cannot rewrite path:", path) \
                    from error

        return os.path.normpath(path)
