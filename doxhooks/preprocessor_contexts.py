"""
The preprocessor mini-languages.

Doxhooks `preprocessor directives <preprocessor directive>`:term: are
written in an extensible `preprocessor`:term: `mini-language`:term:.

Each mini-language is a context that defines the meanings of the
*keywords* in that mini-language (`BasePreprocessorContext`). The
context is also where the `preprocessor variables <preprocessor
node>`:term: are defined.

Exports
-------
PreprocessorContext
    The keywords and variables of a basic preprocessor mini-language.
BasePreprocessorContext
    Base class of a preprocessor mini-language.
lowercase_booleans
    Modify a context to allow lowercase boolean representations.
startcase_booleans
    Modify a context to allow start-case boolean representations.
"""


import ast

import doxhooks.console as console
from doxhooks.errors import (
    DoxhooksDataError, DoxhooksLookupError, DoxhooksTypeError)
from doxhooks.functions import findvalue


__all__ = [
    "BasePreprocessorContext",
    "PreprocessorContext",
    "lowercase_booleans",
    "startcase_booleans",
]


class BasePreprocessorContext:
    """
    Base class of a preprocessor mini-language.

    A subclass of `BasePreprocessorContext` defines a preprocessor
    mini-language:

    * An instance of the subclass is a runtime context of the
      mini-language.
    * The public instance variables and class variables are the
      variables in the mini-language.
    * The public methods are the *keywords* of the mini-language.
    * The private methods and variables provide implementation details
      of the mini-language.

    Private methods and variables are those with names that start with
    an underscore.

    Class Interface
    ---------------
    get
        Return the output representation of a variable.
    interpret
        Interpret tokens within the context of the mini-language.
    """

    def __init__(self, **variables):
        r"""
        Initialise the context with the names and values of variables.

        Parameters
        ----------
        \**variables
            These keyword parameters and their arguments define the
            names and values of variables in the mini-language. These
            variables are implemented as instance variables of the
            context.
        """
        vars(self).update(variables)

    def _get_token_value(self, object_token):
        # Apply the 'member' operator ('.') within a token.
        value = self
        for identifier in object_token.split("."):
            try:
                value = findvalue(value, identifier)
            except DoxhooksLookupError as error:
                # FIXME: Provide more useful info than repr.
                error.description = repr(value)
                raise
        return value

    def _convert_output_type_to_str(self, value, identifier):
        # Return a str, float or int (and perhaps bool) value as str.
        if isinstance(value, str):
            return value
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            return str(value)
        if isinstance(value, bool):
            try:
                return self._convert_bool_to_str(value)
            except AttributeError:
                pass
        output_types = "str, float or int ({}including bool)".format(
            "" if hasattr(self, "_convert_bool_to_str") else "not ")
        raise DoxhooksTypeError(value, identifier, output_types)

    def get(self, output_token, *, preprocessor=None):
        """
        Return the output representation of a variable.

        Parameters
        ----------
        output_token : str
            The name of the variable.
        preprocessor
            Unused. Defaults to ``None``.

        Returns
        -------
        str
            The output representation.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a value with that name is not found.
        ~doxhooks.errors.DoxhooksTypeError
            If the type of the variable is not `str`, `float` or `int`.
            (`bool` can also be an output type: See `startcase_booleans`
            and `lowercase_booleans`.)
        """
        value = self._get_token_value(output_token)
        return self._convert_output_type_to_str(value, output_token)

    def _get_local_value(self, identifier):
        try:
            return findvalue(self, identifier)
        except DoxhooksLookupError as error:
            error.description = "the preprocessor context"
            raise

    def interpret(self, keyword_token, *tokens, preprocessor=None):
        r"""
        Interpret tokens within the context of the mini-language.

        Parameters
        ----------
        keyword_token : str
            The name of a public method that defines a keyword in the
            mini-language.
        \*tokens : str
            Tokens to be passed to the keyword method.
        preprocessor : ~doxhooks.preprocessors.Preprocessor or None, optional
            Keyword-only. A preprocessor that may be required by the
            keyword method. Defaults to ``None``.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If the keyword is not found in this context.
        ~doxhooks.errors.DoxhooksTypeError
            If the type of the keyword is not a `callable` type.
        ~doxhooks.errors.DoxhooksDataError
            If the tokens do not conform to the mini-language syntax.
        """
        keyword = self._get_local_value(keyword_token)
        if not callable(keyword):
            raise DoxhooksTypeError(keyword, keyword_token, "callable")
        try:
            keyword(*tokens, preprocessor=preprocessor)
        except TypeError as error:
            error_message = str(error)
            if error_message.startswith(keyword.__name__ + "()"):
                raise DoxhooksDataError("Bad syntax:", keyword_token, tokens) \
                    from error
            raise


class PreprocessorContext(BasePreprocessorContext):
    """
    The keywords and variables of a basic preprocessor mini-language.

    `PreprocessorContext` extends `BasePreprocessorContext`.

    Class Interface
    ---------------
    set
        Set the value of a variable.
    if_
        Interpret additional tokens if a condition is true.
    insert
        Preprocess the contents of one or more files.
    include
        Preprocess a file if it has not already been preprocessed.
    write
        Preprocess a line of text.
    error
        Raise a `~doxhooks.errors.DoxhooksDataError`.
    warning
        Write a warning message to stderr.
    """

    def set(self, identifier, value_token, *, preprocessor=None):
        """
        Set the value of a variable.

        The variable will be defined in the runtime context of the
        preprocessor mini-language.

        The value is either the result of safely evaluating the value
        token with `ast.literal_eval`, or the token itself if it cannot
        be evaluated.

        Parameters
        ----------
        identifier : str
            The name of the variable.
        value_token : str
            A token representing the value to be set.
        preprocessor
            Unused. Defaults to ``None``.
        """
        try:
            value = ast.literal_eval(value_token)
        except (SyntaxError, ValueError):
            value = value_token
        setattr(self, identifier, value)

    def if_(self, condition_token, keyword_token, *tokens, preprocessor=None):
        r"""
        Interpret additional tokens if a condition is true.

        Note
        ----
            This keyword can be written as ``if`` (instead of ``if_``)
            in the preprocessor directives.

        Parameters
        ----------
        condition_token : str
            The name of a variable that defines the condition.
        keyword_token : str
            A token to be interpreted (within the context of the
            mini-language) if the condition is true.
        \*tokens : str
            More tokens to be interpreted if the condition is true.
        preprocessor : ~doxhooks.preprocessors.Preprocessor or None, optional
            Keyword-only. A preprocessor that may be required if the
            additional tokens are interpreted. Defaults to ``None``.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If the condition is not found.
        ~doxhooks.errors.DoxhooksTypeError
            If the type of the condition is not `bool`.
        """
        condition = self._get_token_value(condition_token)
        if not isinstance(condition, bool):
            raise DoxhooksTypeError(condition, condition_token, "bool")
        if condition:
            self.interpret(keyword_token, *tokens, preprocessor=preprocessor)

    def _get_filename(self, file_token):
        # Evaluate a filename token and return the value.
        try:
            value = self._get_token_value(file_token)
        except DoxhooksDataError:
            value = file_token
        if not (isinstance(value, str) or value is None):
            raise DoxhooksTypeError(value, file_token, "str or None")
        return value

    def insert(self, file_token, *file_tokens, preprocessor):
        r"""
        Preprocess the contents of one or more files.

        Parameters
        ----------
        file_token : str
            A filename or the name of a variable that defines a
            filename.
        \*file_tokens : str
            More filenames or variable names. The order of the arguments
            determines the order that the files are inserted.
        preprocessor : ~doxhooks.preprocessors.Preprocessor
            The preprocessor that will preprocess the files.

        Raises
        ------
        ~doxhooks.errors.DoxhooksTypeError
            If the type of the filename is not `str` or ``None``.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be read.
        """
        tokens = (file_token,) + file_tokens
        for token in tokens:
            preprocessor.insert_file(self._get_filename(token))

    def include(self, file_token, *file_tokens, preprocessor):
        r"""
        Preprocess a file if it has not already been preprocessed.

        Parameters
        ----------
        file_token : str
            A filename or the name of a variable that defines a
            filename.
        \*file_tokens : str
            More filenames or variable names. The order of the arguments
            determines the order that the files are included.
        preprocessor : ~doxhooks.preprocessors.Preprocessor
            The preprocessor that will preprocess the files.

        Raises
        ------
        ~doxhooks.errors.DoxhooksTypeError
            If the type of the filename is not `str` or ``None``.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be read.
        """
        tokens = (file_token,) + file_tokens
        for token in tokens:
            filename = self._get_filename(token)
            preprocessor.insert_file(filename, idempotent=True)

    def write(self, line, *, preprocessor):
        """
        Preprocess a line of text.

        Parameters
        ----------
        line : str
            The line of text.
        preprocessor : ~doxhooks.preprocessors.Preprocessor
            The preprocessor that will preprocess the line.
        """
        preprocessor.insert_lines((line + "\n",))

    def error(self, message, *, preprocessor=None):
        """
        Raise a `~doxhooks.errors.DoxhooksDataError`.

        Parameters
        ----------
        message : str
            The error message.
        preprocessor
            Unused. Defaults to ``None``.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            Unconditionally.
        """
        raise DoxhooksDataError(message)

    def warning(self, message, *, preprocessor=None):
        """
        Write a warning message to stderr.

        Parameters
        ----------
        message : str
            The warning message.
        preprocessor
            Unused. Defaults to ``None``.
        """
        console.warning(message)


def _convert_to_lowercase_str(self, value):
    return str(value).lower()


def lowercase_booleans(context_class):
    """
    Modify a context to allow lowercase boolean representations.

    This decorator modifies a subclass of `BasePreprocessorContext`:

    * `BasePreprocessorContext.get` can return representations of
      `bool` values.
    * The representations are written in lowercase: ``true`` and
      ``false``.

    Lowercase is the correct case for representing boolean literals in
    most programming languages.

    Parameters
    ----------
    context_class : type
        The subclass of `BasePreprocessorContext` to be modified.

    Returns
    -------
    type
        The modified subclass of `BasePreprocessorContext`.
    """
    context_class._convert_bool_to_str = _convert_to_lowercase_str
    return context_class


def _convert_to_str(self, value):
    return str(value)


def startcase_booleans(context_class):
    """
    Modify a context to allow start-case boolean representations.

    This decorator modifies a subclass of `BasePreprocessorContext`:

    * `BasePreprocessorContext.get` can return representations of
      `bool` values.
    * The representations are written in start case: ``True`` and
      ``False``.

    Start case is the correct case for representing boolean literals in
    the Python language.

    Parameters
    ----------
    context_class : type
        The subclass of `BasePreprocessorContext` to be modified.

    Returns
    -------
    type
        The modified subclass of `BasePreprocessorContext`.
    """
    context_class._convert_bool_to_str = _convert_to_str
    return context_class
