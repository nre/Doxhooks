"""
Mangle a filename with a fingerprint of some relevant data.

Resources that are not preprocessed (images, fonts, etc) can be
`fingerprinted <fingerprint>`:term: with `filename_for_files`.

Preprocessed resources (scripts, stylesheets, etc) are more conveniently
fingerprinted with `filename_for_strings` before the output files are
saved.

`filename_for_files` and `filename_for_strings` accept more than one
file or string because a URL can map to more than one file on the server
(because of rewrite rules, content negotiation, etc).

Exports
-------
filename_for_files
    Mangle a filename with the fingerprint of one or more files.
filename_for_strings
    Mangle a filename with the fingerprint of one or more strings.
max_length
    The maximum length of the fingerprint in a mangled filename.
separator
    The substring that separates a fingerprint from the filename stem.
algorithm
    The algorithm that computes the fingerprints.
algorithms
    The fingerprinting algorithms that are available.

See Also
--------
doxhooks.file_domains.OutputFileDomain.fingerprint_files
    Mangle the output filename with the fingerprint of some files.
doxhooks.file_domains.OutputFileDomain.fingerprint_strings
    Mangle the output filename with the fingerprint of some strings.


.. testsetup:: *

    import doxhooks.fingerprint
    algorithm = doxhooks.fingerprint.algorithm
    separator = doxhooks.fingerprint.separator
    max_length = doxhooks.fingerprint.max_length
"""


import hashlib
import os

import doxhooks.fileio as fileio
from doxhooks.errors import DoxhooksTypeError, DoxhooksValueError


__all__ = [
    "algorithm",
    "algorithms",
    "filename_for_files",
    "filename_for_strings",
    "max_length",
    "separator",
]


algorithm = "md5"
"""
The algorithm that computes the fingerprints.

*str*

An algorithm can be selected from the set of available algorithms
(`algorithms`). Defaults to ``"md5"``.

Example
-------
.. doctest:: algorithm

    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-c1285a470f0fc8f14f54851c5d8eb32f.css'
    >>> doxhooks.fingerprint.algorithm = "sha1"
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-2989ab24b9e79f729d27649f39b4109a30226b1a.css'


.. testcleanup:: algorithm

    doxhooks.fingerprint.algorithm = algorithm
"""

algorithms = hashlib.algorithms_guaranteed
"""
The fingerprinting algorithms that are available.

The availability of algorithms is platform dependent. `algorithms` is a
convenient alias for `hashlib.algorithms_guaranteed`.
"""

max_length = None
"""
The maximum length of the fingerprint in a mangled filename.

*int or None*

``None`` denotes that there is no maximum length. Defaults to ``None``.

Example
-------
.. doctest:: max_length

    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-c1285a470f0fc8f14f54851c5d8eb32f.css'
    >>> doxhooks.fingerprint.max_length = 10
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-c1285a470f.css'


.. testcleanup:: max_length

    doxhooks.fingerprint.max_length = max_length
"""

separator = "-"
"""
The substring that separates a fingerprint from the filename stem.

*str*

The substring can be zero, one or more characters. Defaults to ``"-"``.

Example
-------
.. doctest:: separator

    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-c1285a470f0fc8f14f54851c5d8eb32f.css'
    >>> doxhooks.fingerprint.separator = "."
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile.c1285a470f0fc8f14f54851c5d8eb32f.css'


.. testcleanup:: separator

    doxhooks.fingerprint.separator = separator
"""


def _filename_for_bytestrings(filename, bytestrings):
    # Return a filename mangled with the fingerprint of some bytes.
    try:
        hash_object = hashlib.new(algorithm)
    except ValueError as error:
        raise DoxhooksValueError(algorithm, "doxhooks.fingerprint.algorithm") \
            from error
    except TypeError:
        raise DoxhooksTypeError(
            algorithm, "doxhooks.fingerprint.algorithm", "str")

    for bytes_ in bytestrings:
        hash_object.update(bytes_)
    hash_ = hash_object.hexdigest()

    try:
        truncated_hash = hash_[:max_length]
    except TypeError:
        raise DoxhooksTypeError(
            max_length, "doxhooks.fingerprint.max_length", "int or None")

    base, extension = os.path.splitext(filename)
    if not extension and base.endswith("{}"):
        base, extension, __ = base.rpartition("{}")

    try:
        return "".join((base, separator, truncated_hash, extension))
    except TypeError:
        if not isinstance(separator, str):
            raise DoxhooksTypeError(
                separator, "doxhooks.fingerprint.separator", "str")
        raise


def _bytestrings_from_files(*paths):
    # Yield contents of files as chunks of bytes.
    chunk_size = 8192
    for path in paths:
        with fileio.open_input(path, encoding=None) as input_:
            while True:
                bytes_ = input_.read(chunk_size)
                if bytes_:
                    yield bytes_
                else:
                    break


def filename_for_files(filename, path, *paths):
    r"""
    Mangle a filename with the fingerprint of one or more files.

    The fingerprint is of the contents of the files. The fingerprint of
    multiple file arguments is the same as the fingerprint of one file
    made by concatenating the contents of those files in the order that
    their path arguments are passed.

    Parameters
    ----------
    filename : str
        The filename to be mangled.
    path : str
        The path to a file to be fingerprinted.
    \*paths : str
        The paths to more files to be fingerprinted.

    Returns
    -------
    str
        The mangled filename.

    Raises
    ------
    ~doxhooks.errors.DoxhooksFileError
        If a file cannot be read.

    See Also
    --------
    doxhooks.file_domains.OutputFileDomain.fingerprint_files
        Mangle the output filename with the fingerprint of some files.
    """
    bytestrings = _bytestrings_from_files(path, *paths)
    return _filename_for_bytestrings(filename, bytestrings)


def _bytestrings_from_strings(*strings, encoding):
    # Yield encoded strings.
    for string in strings:
        yield string.encode(encoding)


def filename_for_strings(filename, string, *strings, encoding):
    r"""
    Mangle a filename with the fingerprint of one or more strings.

    The fingerprint of multiple string arguments is the same as the
    fingerprint of one string made by concatenating those strings in the
    order that they are passed.

    Parameters
    ----------
    filename : str
        The filename to be mangled.
    string : str
        A string to be fingerprinted.
    \*strings : str
        More strings to be fingerprinted.
    encoding : str
        Keyword-only. The encoding of the strings.

    Returns
    -------
    str
        The mangled filename.

    Examples
    --------
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example1", encoding="ascii")
    'myfile-c1285a470f0fc8f14f54851c5d8eb32f.css'
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "exam", "ple1", encoding="ascii")
    'myfile-c1285a470f0fc8f14f54851c5d8eb32f.css'
    >>> doxhooks.fingerprint.filename_for_strings(
    ...     "myfile.css", "example2", encoding="ascii")
    'myfile-66b375b08fc869632935c9e6a9c7f8da.css'

    See Also
    --------
    doxhooks.file_domains.OutputFileDomain.fingerprint_strings
        Mangle the output filename with the fingerprint of some strings.
    """
    bytestrings = _bytestrings_from_strings(
        string, *strings, encoding=encoding)
    return _filename_for_bytestrings(filename, bytestrings)
