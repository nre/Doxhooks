"""
High-level file operations and data.

An input-file domain returns the paths (`InputFileDomain.path`) and file
objects (`InputFileDomain.open`) of input files. The paths to these
files are remembered (`InputFileDomain.paths`).

An output-file domain returns the paths (`OutputFileDomain.path`) and
file objects (`OutputFileDomain.open`) of output files. The contents of
an output file can be saved (`OutputFileDomain.save`). The output
filename can be mangled with the fingerprint of some data
(`OutputFileDomain.fingerprint_files`,
`OutputFileDomain.fingerprint_strings`).

Exports
-------
InputFileDomain
    High-level input-file operations and data.
OutputFileDomain
    High-level output-file operations and data.
"""


import doxhooks.console as console
import doxhooks.fileio as fileio
import doxhooks.fingerprint as fingerprint


__all__ = [
    "InputFileDomain",
    "OutputFileDomain",
]


class InputFileDomain:
    """
    High-level input-file operations and data.

    Class Interface
    ---------------
    path
        Return the path to an input file.
    open
        Open an input file in reading mode and return the file object.
    """

    def __init__(self, filetree, branch, filename, encoding):
        """
        Initialise the file domain with a file tree and file data.

        Parameters
        ----------
        filetree : ~doxhooks.filetrees.FileTree
            A tree with input-file-path branches.
        branch : str
            The path to the default directory for input files.
        filename : str
            The name of the default input file.
        encoding : str or None
            The encoding of the input files. The encoding of a binary
            file is ``None``.

        Attributes
        ----------
        branch : str
            The argument of `branch`.
        filename : str
            The argument of `filename`.
        encoding : str or None
            The argument of `encoding`.
        paths : set
            All the file paths that have been handled by `self.path` and
            `self.open`.
        """
        self._filetree = filetree
        self.branch = branch
        self.filename = filename
        self.encoding = encoding
        self.paths = set()

    def path(self, filename=None, *, rewrite=None):
        """
        Return the path to an input file.

        The path is added to `self.paths`.

        Parameters
        ----------
        filename : str or None, optional
            A filename to use instead of `self.filename`. Defaults to
            ``None``.
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the path. Defaults to ``None``, which denotes that the
            path will not be rewritten.

        Returns
        -------
        str
            The file path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the path cannot be determined.
        """
        target = self.filename if filename is None else filename
        path = self._filetree.path(self.branch, target, rewrite=rewrite)
        self.paths.add(path)
        return path

    def open(self, filename=None):
        """
        Open an input file in reading mode and return the file object.

        The path is added to `self.paths`.

        Parameters
        ----------
        filename : str or None, optional
            A filename to use instead of `self.filename`. Defaults to
            ``None``.

        Returns
        -------
        BinaryIO or TextIO
            A binary file (if `self.encoding` is ``None``) or a text
            file (if `self.encoding` is not ``None``).

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the file-domain data is invalid.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be opened.
        """
        return fileio.open_input(self.path(filename), self.encoding)


class OutputFileDomain:
    """
    High-level output-file operations and data.

    Class Interface
    ---------------
    path
        Return the path to an output file.
    open
        Open an output file in writing mode and return the file object.
    save
        Write the contents of an output file and close the file.
    fingerprint_files
        Mangle the output filename with the fingerprint of some files.
    fingerprint_strings
        Mangle the output filename with the fingerprint of some strings.
    """

    def __init__(self, filetree, branch, filename, encoding, newline):
        """
        Initialise the file domain with a file tree and file data.

        Parameters
        ----------
        filetree : ~doxhooks.filetrees.FileTree
            A tree with output-file-path branches.
        branch : str
            The path to the directory for output files.
        filename : str
            The name of the output file.
        encoding : str or None
            The encoding of the output files. The encoding of a binary
            file is ``None``.
        newline : str or None
            See the *newline* parameter of `open` or `io.TextIOWrapper`
            for details. Should be ``None`` for binary files.

        Attributes
        ----------
        branch : str
            The argument of `branch`.
        filename : str
            The argument of `filename`.
        encoding : str or None
            The argument of `encoding`.
        newline : str or None
            The argument of `newline`.
        """
        self._filetree = filetree
        self.branch = branch
        self.filename = self._initial_filename = filename
        self.encoding = encoding
        self.newline = newline

    def path(self, *, rewrite=None):
        """
        Return the path to an output file.

        Parameters
        ----------
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the path. Defaults to ``None``, which denotes that the
            path will not be rewritten.

        Returns
        -------
        str
            The file path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the path cannot be determined.
        """
        path = self._filetree.path(self.branch, self.filename, rewrite=rewrite)
        console.log("Output:", path)
        return path

    def open(self, *, rewrite=None):
        """
        Open an output file in writing mode and return the file object.

        Note
        ----
            If a file already exists at the path, it will be
            overwritten.

        Parameters
        ----------
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the path. Defaults to ``None``, which denotes that the
            path will not be rewritten.

        Returns
        -------
        BinaryIO or TextIO
            A binary file (if `self.encoding` is ``None``) or a text
            file (if `self.encoding` is not ``None``).

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the file-domain data is invalid.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be opened.
        """
        return fileio.open_output(
            self.path(rewrite=rewrite), self.encoding, self.newline)

    def save(self, data, *, rewrite=None):
        """
        Write the contents of an output file and close the file.

        Note
        ----
            If a file already exists at the path, it will be
            overwritten.

        Parameters
        ----------
        data : bytes or str
            The data to be saved. Binary data is `bytes` and text data
            is `str`.
        rewrite : optional
            Keyword-only. A value that will replace a substring ``"{}"``
            in the path. Defaults to ``None``, which denotes that the
            path will not be rewritten.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the file-domain data is invalid.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be saved.
        """
        fileio.save(
            self.path(rewrite=rewrite), data, self.encoding, self.newline)

    def fingerprint_files(self, path, *paths):
        r"""
        Mangle the output filename with the fingerprint of some files.

        The fingerprint is of the contents of the files. The fingerprint
        of multiple file arguments is the same as the fingerprint of one
        file made by concatenating the contents of those files in the
        order that they are passed.

        Parameters
        ----------
        path : str
            The path to a file to be fingerprinted.
        \*paths : str, optional
            The paths to more files to be fingerprinted.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If a file cannot be read.
        """
        self.filename = fingerprint.filename_for_files(
            self._initial_filename, path, *paths)

    def fingerprint_strings(self, string, *strings):
        r"""
        Mangle the output filename with the fingerprint of some strings.

        The fingerprint of multiple string arguments is the same as the
        fingerprint of one string made by concatenating those strings in
        the order that they are passed.

        Parameters
        ----------
        string : str
            A string to be fingerprinted.
        \*strings : str, optional
            More strings to be fingerprinted.
        """
        self.filename = fingerprint.filename_for_strings(
            self._initial_filename, string, *strings, encoding=self.encoding)
