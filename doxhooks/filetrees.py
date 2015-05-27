"""
Directory trees that produce file paths.

A `file tree`:term: produces file paths by joining a directory branch to
a filename (`FileTree.path`). The file tree has a default filename, a
default `branch`:term: and a collection of named branches. The default
branch is overridden by starting the filename with the name of a branch,
e.g. ``"<my_branch>my_file.src"``, ``"<my_branch>my_dir/my_file.src"``.
Branches are chained by starting a branch with the name of another
branch.

Exports
-------
InputFileTree
    A directory tree that produces paths to input files.
OutputFileTree
    A directory tree that produces paths to output files.
FileTree
    A directory tree that produces file paths.


.. testsetup::

    import doxhooks.filetrees, os, posixpath
    os_path = os.path
    os.path = posixpath

.. testcleanup::

    os.path = os_path
"""


import os
import re

from doxhooks.errors import DoxhooksLookupError, DoxhooksValueError


__all__ = [
    "FileTree",
    "InputFileTree",
    "OutputFileTree",
]


class FileTree:
    """
    A directory tree that produces file paths.

    Class Interface
    ---------------
    path
        Join a filename to a directory branch and return the path.
    """

    _branches_name = "`branches`"

    def __init__(self, default_branch, default_filename, branches):
        """
        Initialise the file tree with branches and a default path.

        Parameters
        ----------
        default_branch : str
            The branch to use when the filename does not start with the
            name of a branch.
        default_filename : str
            The filename to use when the caller does not provide a
            filename.
        branches : dict
            The names and paths of directories in the tree.

        Attributes
        ----------
        default_filename : str
            The argument of `default_filename`.
        """
        self._default_branch = default_branch
        self.default_filename = default_filename
        self._branches = branches

    _branch_notation = re.compile(
        r"^<(?P<branch_name>\w+)>(?P<subpath>.*)")

    def _get_branch(self, match):
        # Recursively look up branch name and return the branch value.
        branch_name, subpath = match.group("branch_name", "subpath")
        try:
            branch = self._branches[branch_name]
        except KeyError:
            raise DoxhooksLookupError(
                branch_name, self._branches, self._branches_name)
        path = os.path.join(branch, subpath)
        return self._branch_notation.sub(self._get_branch, path)

    def path(self, filename=None, *, rewrite=None):
        r"""
        Join a filename to a directory branch and return the path.

        If the filename starts with a branch name, then the filename is
        joined to the named branch. Otherwise the *default branch* of
        this `FileTree` is used. Branches are chained by starting a
        branch with the name of another branch.

        Parameters
        ----------
        filename : str or None, optional
            A filename to use instead of the *default filename* of this
            `FileTree`. Defaults to ``None``.
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the filename. Defaults to ``None``, which denotes that
            the filename will not be rewritten.

        Returns
        -------
        str
            The file path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a branch name cannot be found in the *branch dictionary*
            of this `FileTree`.
        ~doxhooks.errors.DoxhooksValueError
            If `rewrite` is not ``None`` and the filename cannot be
            rewritten.

        Examples
        --------
        >>> filetree = doxhooks.filetrees.FileTree(
        ...     "img/png", "picture.png", {"svg": "img/svg"})
        >>> filetree.path()
        'img/png/picture.png'
        >>> filetree.path("image{}.png", rewrite="_1")
        'img/png/image_1.png'
        >>> filetree.path("<svg>drawing.svg")
        'img/svg/drawing.svg'
        >>> filetree.path("<jpeg>photo.jpg")
        Traceback (most recent call last):
            ...
        doxhooks.errors.DoxhooksLookupError: Cannot find 'jpeg' in `branches`.
        """
        if filename is None:
            target_filename = self.default_filename
        else:
            target_filename = filename

        if rewrite is not None:
            try:
                target_filename = target_filename.format(rewrite)
            except LookupError as error:
                raise DoxhooksValueError(
                    target_filename, "filename", "a rewritable filename") \
                    from error

        if self._branch_notation.match(target_filename):
            path = target_filename
        else:
            branch_notation = self._branch_notation.match(self._default_branch)
            if branch_notation and not branch_notation.group("subpath"):
                path = self._default_branch + target_filename
            else:
                path = os.path.join(self._default_branch, target_filename)

        return os.path.normpath(
            self._branch_notation.sub(self._get_branch, path))


class InputFileTree(FileTree):
    """
    A directory tree that produces paths to input files.

    `InputFileTree` extends `FileTree`.
    """

    _branches_name = "`input_branches`"


class OutputFileTree(FileTree):
    """
    A directory tree that produces paths to output files.

    `OutputFileTree` extends `FileTree`.

    Class Interface
    ---------------
    path
        Extend `FileTree.path` by returning the path to an output file.
    url_path
        Extend `FileTree.path` by returning the file path in the URL.
    """

    def __init__(self, *args, output_branches, url_branches):
        """
        Initialise the file tree with branches and a default path.

        The `OutputFileTree` constructor extends the `FileTree`
        constructor by replacing the *branches* parameter with
        `output_branches` and `url_branches`.

        Parameters
        ----------
        output_branches : dict
            The names and paths of the output directories.
        url_branches : dict
            The names and paths of directories in URLs.
        """
        super().__init__(*args, branches=None)
        self._output_branches = output_branches
        self._url_branches = url_branches

    def path(self, *, rewrite=None):
        # FIXME: args are different from super().path args.
        """
        Return the path to an output file.

        Extends `FileTree.path`.
        """
        self._branches = self._output_branches
        self._branches_name = "`output_branches`"
        return super().path(rewrite=rewrite)

    def url_path(self, *, rewrite=None):
        """
        Return the file path in the default URL.

        Extends `FileTree.path`.
        """
        self._branches = self._url_branches
        self._branches_name = "`url_branches`"
        return super().path(rewrite=rewrite)
