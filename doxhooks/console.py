"""
Format the information sent through the standard streams.

`~doxhooks.console` is the interface between Doxhooks and the standard
streams (stdout, stderr and stdin).

Exports
-------
info
    Write important information to stdout.
log
    Write general information to stdout.
pre
    Write preformatted information to stdout.
section
    Write a section heading or section break to stdout.
blank_line
    Write a blank line to stdout.
flush
    Flush stdout.
error
    Write error information to stderr.
error_trace
    Write the location and source of an error to stderr.
warning
    Write a warning message to stderr.
input
    Write a prompt to stderr and return the input from stdin.


.. testsetup::

    import doxhooks.console, sys
    sys.stderr = sys.stdout
"""


import builtins
import sys


__all__ = [
    "blank_line",
    "error",
    "error_trace",
    "flush",
    "info",
    "input",
    "log",
    "pre",
    "section",
    "warning",
]


def info(arg, *args):
    r"""
    Write important information to stdout.

    Parameters
    ----------
    arg
        Some information.
    \*args
        Some more information.

    Example
    -------
    >>> doxhooks.console.info("example", 1)
    example 1
    """
    print(arg, *args)


def log(arg, *args):
    r"""
    Write general information to stdout.

    Parameters
    ----------
    arg
        Some information.
    \*args
        Some more information.

    Example
    -------
    >>> doxhooks.console.log("example", 1)
        example 1
    """
    print("   ", arg, *args)


def pre(data):
    """
    Write preformatted information to stdout.

    Parameters
    ----------
    data
        The preformatted information.

    Example
    -------
    >>> doxhooks.console.pre(" example   1")
     example   1
    """
    print(data)


def section(heading=None):
    """
    Write a section heading or section break to stdout.

    Parameters
    ----------
    heading : optional
        A heading for the new section. Defaults to ``None``, which
        denotes no heading.

    Examples
    --------
    >>> doxhooks.console.section("example heading")
    <BLANKLINE>
    <BLANKLINE>
    ### example heading ###########################################################
    <BLANKLINE>
    >>> doxhooks.console.section()
    <BLANKLINE>
    <BLANKLINE>
    ###############################################################################
    <BLANKLINE>
    """
    if heading is None:
        section_break_heading = ""
    else:
        section_break_heading = "### {} ".format(heading)
    print("\n\n{:#<79}\n".format(section_break_heading))


def blank_line():
    """Write a blank line to stdout."""
    print()


def flush():
    """Flush stdout."""
    sys.stdout.flush()


def _print_stderr(*args, end="\n"):
    flush()
    print(*args, end=end, file=sys.stderr, flush=True)


def error(arg, *args):
    r"""
    Write error information to stderr.

    Parameters
    ----------
    arg
        Some information. If the object is an instance of
        `BaseException`, then both the class name and the error message
        are written.
    \*args
        Some more information.

    Examples
    --------
    >>> doxhooks.console.error("example", 1)
     ** Error! example 1
    >>> doxhooks.console.error(RuntimeError("example"), 2)
     ** RuntimeError! example 2
    """
    error_name = "Error"
    if isinstance(arg, BaseException):
        error_name = type(arg).__name__

    _print_stderr(" ** {}!".format(error_name), arg, *args)


def error_trace(location, source):
    r"""
    Write the location and source of an error to stderr.

    Parameters
    ----------
    location
        The location of the error.
    source
        The source of the error.

    Example
    -------
    >>> doxhooks.console.error_trace("example.py line 10", "y = 1 / x\n")
     ** Error trace! example.py line 10: y = 1 / x
    """
    _print_stderr(
        " ** Error trace! {}: {}".format(location, source.rstrip("\n")))


def warning(arg, *args):
    r"""
    Write a warning to stderr.

    Parameters
    ----------
    arg
        Some information.
    \*args
        Some more information.

    Example
    -------
    >>> doxhooks.console.warning("example", 1)
      * Warning! example 1
    """
    _print_stderr("  * Warning!", arg, *args)


def input(prompt=""):
    """
    Write a prompt to stderr and return the input from stdin.

    Parameters
    ----------
    prompt : optional
        The prompt. Defaults to the empty string.

    Returns
    -------
    str
        The input from stdin.

    Example
    -------
    >>> doxhooks.console.input("example? ")  # doctest: +SKIP
     >> example? 1
    '1'
    """
    _print_stderr(" >> {}".format(prompt), end="")
    return builtins.input()
