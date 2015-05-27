"""
Load and save files of Python-literal data.

Python-literal data that is successfully saved by `save_literals` is
guaranteed to be restorable with `load_literals`.

See the description of `ast.literal_eval` for the list of supported
Python literals.

Exports
-------
load_literals
    Read a file of Python-literal data.
save_literals
    Write a file of Python-literal data.

See Also
--------
doxhooks.fileio
    For general file operations.
"""


import ast

import doxhooks.fileio as fileio
from doxhooks.errors import DoxhooksDataError, DoxhooksDataFileError


__all__ = [
    "load_literals",
    "save_literals",
]


def load_literals(path):
    """
    Read a file of Python-literal data and return the data value.

    The data file is read as ASCII-encoded text. The data is safely
    evaluated with `ast.literal_eval`.

    Parameters
    ----------
    path : str
        The path to the data file.

    Returns
    -------
    object
        The evaluated Python-literal data.

    Raises
    ------
    ~doxhooks.errors.DoxhooksFileError
        If the data file cannot be read.
    ~doxhooks.errors.DoxhooksDataFileError
        If the data in the file are not Python literals.
    """
    string = fileio.load(path, "ascii")
    try:
        return ast.literal_eval(string)
    except (SyntaxError, ValueError) as error:
        raise DoxhooksDataFileError("Bad literal-data file:", path) from error


def save_literals(path, data):
    """
    Write Python-literal data to a file and close the file.

    An `ascii` representation of the literals is saved.

    Parameters
    ----------
    path : str
        The path to the data file.
    data
        The Python-literal data to be saved.

    Raises
    ------
    ~doxhooks.errors.DoxhooksDataError
        If the data is not restorable with `load_literals`.
    ~doxhooks.errors.DoxhooksFileError
        If the data file cannot be saved.
    """
    string = ascii(data)
    try:
        evaluated_data = ast.literal_eval(string)
    except (SyntaxError, ValueError) as error:
        raise DoxhooksDataError("Data is not valid Python-literal data.") \
            from error
    if evaluated_data != data:
        raise DoxhooksDataError(
            "Data does not have a restorable representation.")
    fileio.save(path, string, "ascii")
