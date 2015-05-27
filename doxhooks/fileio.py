"""
Read, write and copy files.

`~doxhooks.fileio` is the interface between Doxhooks and the file system.

Exports
-------
add_output_roots
    Declare the paths to directories where overwriting files is ok.
copy
    Copy a file.
load
    Read the contents of a file.
save
    Write the contents of a file.
open_input
    Open a file in reading mode and return the file object.
open_output
    Open a file in writing mode and return the file object.

See Also
--------
doxhooks.dataio
    For working with files of Python literal data.
"""


import os
import shutil

from doxhooks.errors import (
    DoxhooksFileSystemError, DoxhooksOutputPathError, DoxhooksValueError)


__all__ = [
    "add_output_roots",
    "copy",
    "load",
    "open_input",
    "open_output",
    "save",
]


_output_roots = set()


def add_output_roots(root_path, *root_paths):
    r"""
    Declare the paths to directories where overwriting files is ok.

    The paths are either absolute or relative to the current working
    directory.

    Parameters
    ----------
    root_path : str
        The path to a output root directory.
    \*root_paths : str
        The paths to more output root directories.
    """
    roots = (root_path,) + root_paths
    for root in roots:
        _output_roots.add(os.path.abspath(root))


def _check_output_path(path):
    # Raise an error if the path does not branch off an output root.
    for root in _output_roots:
        rel_path = os.path.relpath(os.path.abspath(path), root)
        if not rel_path.startswith(os.pardir):
            return
    raise DoxhooksOutputPathError(
        "Bad output path (see doxhooks.fileio.add_output_roots):", path)


def _makedirs(path):
    # Make directories if they do not exist.
    directory_path = os.path.dirname(path)
    if not directory_path:
        return
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as error:
        raise DoxhooksFileSystemError("Cannot make directory:", path) \
            from error


def copy(input_path, output_path):
    """
    Copy a file.

    Note
    ----
        If a file already exists at the output path, it will be
        overwritten.

    The output path directories are created if they do not exist.

    Parameters
    ----------
    input_path : str
        The path to the file.
    output_path : str
        The path that the file is copied to.

    Raises
    ------
    ~doxhooks.errors.DoxhooksOutputPathError
        If the output path does not branch off any of the output roots
        declared with `add_output_roots`.
    ~doxhooks.errors.DoxhooksFileSystemError
        If the file cannot be found or copied.

    See Also
    --------
    doxhooks.resources.Resource._write
        Copy the input file to the output file path.
    """
    _check_output_path(output_path)
    _makedirs(output_path)
    try:
        shutil.copy2(input_path, output_path)
    except FileNotFoundError:
        raise DoxhooksFileSystemError("Cannot find file:", input_path)
    except OSError as error:
        raise DoxhooksFileSystemError(
            "Cannot copy file from {!r} to {!r}."
            .format(input_path, output_path)) from error


def _open(path, mode, encoding, newline):
    # Return an open file object. This is a wrapper for builtins.open.
    if encoding is None:
        mode = "b" + mode
        if newline is not None:
            raise DoxhooksValueError(
                newline, "newline", "None when encoding is None")
    try:
        return open(path, mode, encoding=encoding, newline=newline)
    except FileNotFoundError:
        raise DoxhooksFileSystemError("Cannot find file:", path)
    except OSError as error:
        raise DoxhooksFileSystemError("Cannot open file:", path) from error


def open_input(path, encoding, newline=None):
    """
    Open a file in reading mode and return the file object.

    Parameters
    ----------
    path : str
        The path to the file.
    encoding : str or None
        The encoding of the file. The encoding of a binary file is
        ``None``.
    newline : str or None, optional
        See the *newline* parameter of `open` or `io.TextIOWrapper` for
        details. Should be ``None`` for binary files. Defaults to
        ``None``.

    Returns
    -------
    BinaryIO or TextIO
        A binary file (if `encoding` is ``None``) or a text file (if
        `encoding` is not ``None``).

    Raises
    ------
    ~doxhooks.errors.DoxhooksValueError
        If `encoding` is ``None`` and `newline` is not ``None``.
    ~doxhooks.errors.DoxhooksFileSystemError
        If the file cannot be found or opened.

    See Also
    --------
    load
        Return the contents of a file.
    doxhooks.file_domains.InputFileDomain.open
        Open an input file in reading mode and return the file object.
    """
    return _open(path, "r", encoding, newline)


def open_output(path, encoding, newline=None):
    """
    Open a file in writing mode and return the file object.

    Note
    ----
        If a file already exists at the path, it will be overwritten.

    The path directories are created if they do not exist.

    Parameters
    ----------
    path : str
        The path to the file.
    encoding : str or None
        The encoding of the file. The encoding of a binary file is
        ``None``.
    newline : str or None, optional
        See the *newline* parameter of `open` or `io.TextIOWrapper` for
        details. Should be ``None`` for binary files. Defaults to
        ``None``.

    Returns
    -------
    BinaryIO or TextIO
        A binary file (if `encoding` is ``None``) or a text file (if
        `encoding` is not ``None``).

    Raises
    ------
    ~doxhooks.errors.DoxhooksOutputPathError
        If the path does not branch off any of the output roots declared
        with `add_output_roots`.
    ~doxhooks.errors.DoxhooksValueError
        If `encoding` is ``None`` and `newline` is not ``None``.
    ~doxhooks.errors.DoxhooksFileSystemError
        If the file cannot be opened.

    See Also
    --------
    save
        Write the contents of a file and close the file.
    doxhooks.file_domains.OutputFileDomain.open
        Open an output file in writing mode and return the file object.
    """
    _check_output_path(path)
    _makedirs(path)
    return _open(path, "w", encoding, newline)


def load(path, encoding, newline=None):
    """
    Return the contents of a file.

    This function is a convenience wrapper for `open_input`.

    Parameters
    ----------
    path : str
        The path to the file.
    encoding : str or None
        The encoding of the data. The encoding of binary data is
        ``None``.
    newline : str or None, optional
        See the *newline* parameter of `open` or `io.TextIOWrapper` for
        details. Should be ``None`` for binary data. Defaults to
        ``None``.

    Returns
    -------
    bytes or str
        Binary data (if `encoding` is ``None``) or text data (if
        `encoding` is not ``None``).

    Raises
    ------
    ~doxhooks.errors.DoxhooksValueError
        If `encoding` is ``None`` and `newline` is not ``None``.
    ~doxhooks.errors.DoxhooksFileSystemError
        If the file cannot be found or read.

    See Also
    --------
    doxhooks.dataio.load_literals
        Read a file of Python literal data and return the data value.
    """
    with open_input(path, encoding, newline) as input_:
        return input_.read()


def save(path, data, encoding, newline=None):
    """
    Write the contents of a file and close the file.

    Note
    ----
        If a file already exists at the path, it will be overwritten.

    This function is a convenience wrapper for `open_output`. The path
    directories are created if they do not exist.

    Parameters
    ----------
    path : str
        The path to the file.
    data : bytes or str
        The data to be saved. Binary data is `bytes` and text data is
        `str`.
    encoding : str or None
        The encoding of the data. The encoding of binary data is
        ``None``.
    newline : str or None, optional
        See the *newline* parameter of `open` or `io.TextIOWrapper` for
        details. Should be ``None`` for binary data. Defaults to
        ``None``.

    Raises
    ------
    ~doxhooks.errors.DoxhooksOutputPathError
        If the path does not branch off any of the output roots declared
        with `add_output_roots`.
    ~doxhooks.errors.DoxhooksValueError
        If `encoding` is ``None`` and `newline` is not ``None``.
    ~doxhooks.errors.DoxhooksFileSystemError
        If the file cannot be saved.

    See Also
    --------
    doxhooks.file_domains.OutputFileDomain.save
        Write the contents of an output file and close the file.
    doxhooks.dataio.save_literals
        Write Python literal data to a file and close the file.
    """
    with open_output(path, encoding, newline) as output:
        output.write(data)
