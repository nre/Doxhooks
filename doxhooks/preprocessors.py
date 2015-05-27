# TODO: Subclass interface.
"""
General-purpose and HTML lexical preprocessors.

The `preprocessors <preprocessor>`:term: accept lines of text
(`Preprocessor.insert_lines`) and files (`Preprocessor.insert_file`). A
preprocessor starts by reading the root input file
(`Preprocessor.start`), and remembers all the input files that it opens
(`Preprocessor.input_files`).

Preprocessor `directives <preprocessor directive>`:term: and variables
(also known as `nodes <preprocessor node>`:term:) are distinguished from
the source text by customisable delimiters (`directive_delimiter`,
`node_delimiters`, `code_nodes`).

The HTML preprocessor recognises character references (also known as
character entities) and can replace them with characters, other
character references, etc (`HTMLPreprocessor.character_references`).
Warnings about unknown character references can be suppressed
(`HTMLPreprocessor.suppress_character_reference_warnings`).

Exports
-------
Preprocessor
    A general-purpose lexical preprocessor.
HTMLPreprocessor
    A lexical preprocessor for HTML.
directive_delimiter
    Customise the opening delimiter of the preprocessor directives.
node_delimiters
    Customise the delimiters of the preprocessor *nodes*.
code_nodes
    Modify a preprocessor to use code-syntax-friendly *node* delimiters.
"""


import inspect
import re
import shlex

import doxhooks.console as console


__all__ = [
    "HTMLPreprocessor",
    "Preprocessor",
    "code_nodes",
    "directive_delimiter",
    "node_delimiters",
]


def _compile_match_directive(opening_delimiter):
    # Return a regex match method for a preprocessor directive pattern.
    #
    # A directive can be distinguished from a node. The keyword of a
    # directive is immediately followed by whitespace, whereas
    # whitespace is not allowed inside a node.
    directive_pattern = "".join((
        r"(?P<indentation>[ \t]*)", opening_delimiter,
        r"[ \t]*(?P<keyword>\w+)(?:[ \t]+(?P<block>.+))?[ \t]*\n"))

    # fullmatch is new in Python 3.4.
    # return re.compile(directive_pattern).fullmatch
    return re.compile(directive_pattern + "$").match


def _compile_replace_nodes(opening_delimiter, closing_delimiter=None):
    # Return a regex substitution method for a 'node' pattern.
    if closing_delimiter is None:
        closing_delimiter = opening_delimiter

    node_pattern = "".join((
        opening_delimiter, r"(?P<identifier>(?:\w+\.)*\w+)",
        closing_delimiter))

    return re.compile(node_pattern).sub


class Preprocessor:
    """
    A general-purpose lexical preprocessor.

    The default opening delimiter for a preprocessor directive is
    ``##``. This delimiter can be customised with the
    `directive_delimiter` class decorator. The closing delimiter is the
    end of the line.

    The default opening and closing delimiters for a preprocessor *node*
    are both ``##``. These delimiters can be replaced with the
    code-syntax-friendly `code_nodes` class decorator or customised with
    the `node_delimiters` class decorator.

    The `~doxhooks.preprocessor_factories.PreprocessorFactory` not only
    hides the construction of a preprocessor from the caller, but also
    parameterises the types of preprocessor and preprocessor context
    that the caller receives.

    Class Interface
    ---------------
    start
        Preprocess the root input file.
    insert_file
        Push the contents of a file onto the preprocessor stack.
    insert_lines
        Push some lines of text onto the preprocessor stack.
    """

    def __init__(
            self, context, input_file_domain, root_input_filename,
            output_file):
        """
        Initialise the preprocessor with a context and files.

        Parameters
        ----------
        context : ~doxhooks.preprocessor_contexts.BasePreprocessorContext
            A context that defines and interprets the preprocessor
            directives and variables in the input files.
        input_file_domain : ~doxhooks.file_domains.InputFileDomain
            The input-file domain.
        root_input_filename : str
            The name of the file that is opened by `Preprocessor.start`.
        output_file : TextIO
            An open file object that the preprocessor writes its output
            to.

        Attributes
        ----------
        input_files : set
            The filename of each input file that has been preprocessed.
        """
        self._context = context
        self._input = input_file_domain
        self._root_input_filename = root_input_filename
        self._output = output_file

        self._indentation = ""
        self.input_files = set()

    _match_directive = _compile_match_directive("##")

    def _eval_directive(self, indentation, directive):
        # Tokenise a directive and interpret the tokens in the context.
        self._indentation = indentation + directive.group("indentation")

        keyword_token, block = directive.group("keyword", "block")
        tokens = shlex.split(block, comments=True) if block is not None else ()
        self._context.interpret(keyword_token, *tokens, preprocessor=self)

    _replace_nodes = _compile_replace_nodes("##")

    def _flatten_node(self, node):
        # Recursively flatten a 'node' and return the output text.
        identifier = node.group("identifier")
        node_value = self._context.get(identifier)
        try:
            return self._replace_nodes(self._flatten_node, node_value)
        except Exception:
            console.error_trace("Node `{}`".format(identifier), node_value)
            raise

    def _eval_line(self, line):
        # Evaluate a line of input text and return the output text.
        return self._replace_nodes(self._flatten_node, line)

    def insert_lines(self, lines, name=None):
        """
        Push some lines of text onto the preprocessor stack.

        Parameters
        ----------
        lines : Iterable[str]
            The lines of text.
        name : str or None, optional
            A name for the lines. The name is only used when tracing the
            source of an error. If a name is not provided, the name of
            the function that called `insert_lines` is used. Defaults to
            ``None``.
        """
        indentation = self._indentation

        # Silently fix a deceptive user error:
        # lines should be Iterable[str], but not str[str].
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)

        for line_no, line in enumerate(lines, start=1):
            directive = self._match_directive(line)
            try:
                if directive:
                    self._eval_directive(indentation, directive)
                    continue
                output_line = self._eval_line(line)
            except Exception:
                # inspect.stack()[1][3] references the name
                # of the function that called insert_lines:
                name = name or inspect.stack()[1][3]
                console.error_trace(
                    "{!r}\n    >> line {:3}".format(name, line_no), line)
                raise

            if output_line == "\n":
                # Do not write indentation without content.
                self._output.write("\n")
            elif output_line:
                self._output.write(indentation + output_line)

    def insert_file(self, filename, *, idempotent=False):
        """
        Push the contents of a file onto the preprocessor stack.

        The filename is added to the set of *input files* opened by this
        `Preprocessor`.

        Parameters
        ----------
        filename : str or None
            The name of the file.
        idempotent : bool, optional
            Keyword-only. Whether to silently ignore the file if it has
            already been preprocessed and written to the output file.
            Defaults to ``False``.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be opened.
        """
        if not filename:
            return

        if idempotent and filename in self.input_files:
            return

        # TODO: self.input_files.add(self._input.path(filename)) ?
        # Because the paths are unique (ignoring symbolic links) whereas
        # filenames can refer to the same file (depending on their
        # branches).

        self.input_files.add(filename)
        with self._input.open(filename) as lines:
            self.insert_lines(lines, filename)

    def start(self):
        """
        Preprocess the root input file.

        This method is idempotent, so it has no effect if the *root
        input file* of this `Preprocessor` has already been
        preprocessed.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be opened.
        """
        self.insert_file(self._root_input_filename, idempotent=True)


class HTMLPreprocessor(Preprocessor):
    """
    A lexical preprocessor for HTML.

    The base class is `Preprocessor`.

    Class Interface
    ---------------
    character_references
        A dictionary of character names and their replacement string
        values.
    suppress_character_reference_warnings
        Suppress warning messages about unknown HTML character
        references.
    """

    character_references = {}
    """
    A dictionary of character names and their replacement string values.

    *dict*

    Each dictionary item is a character name (also known as a character
    'entity') paired with a replacement string value. The name does not
    include the ``&`` and ``;`` delimiters.

    The character name can also be a decimal or hexadecimal code point.
    The code point does not include the preceding ``#``, but a
    hexadecimal code point does require the ``x`` prefix.

    Defaults to an empty dictionary.
    """

    suppress_character_reference_warnings = False
    """
    Suppress warning messages about unknown HTML character references.

    *bool*

    A warning message is written to stderr each time that an unknown
    character reference (i.e. a reference that is not in
    `self.character_references`) is written to the output file. These
    warnings can be suppressed by setting
    `self.suppress_character_reference_warnings` to ``True`` (or another
    'truthy' value). Defaults to ``False``.
    """

    _replace_character_references = re.compile(r"&#?(?P<reference>\w+);").sub

    def _get_character(self, character_reference):
        reference = character_reference.group("reference")
        try:
            character = self.character_references[reference]
        except KeyError:
            if not self.suppress_character_reference_warnings:
                console.warning(
                    "Unknown HTML character reference:", reference)
            character = character_reference.group()
        return character

    def _eval_line(self, line):
        preprocessed_line = super()._eval_line(line)
        return self._replace_character_references(
            self._get_character, preprocessed_line)


def directive_delimiter(opening_delimiter):
    """
    Customise the opening delimiter of the preprocessor directives.

    It is usually desirable for the opening delimiter to start with the
    line-comment delimiter of a particular language (often ``#`` or
    ``//``), followed by additional characters to distinguish the
    directives from comments.

    The closing delimiter is the end of the line.

    The delimiters must be valid regular-expression patterns.

    Parameters
    ----------
    opening_delimiter : str
        The opening-delimiter pattern.

    Returns
    -------
    ~collections.abc.Callable
        A decorator for modifying a subclass of `Preprocessor`.
    """
    def decorator(preprocessor_class):
        preprocessor_class._match_directive = _compile_match_directive(
            opening_delimiter)
        return preprocessor_class
    return decorator


def node_delimiters(opening_delimiter, closing_delimiter=None):
    """
    Customise the delimiters of the preprocessor *nodes*.

    The delimiters must be valid regular-expression patterns.

    Parameters
    ----------
    opening_delimiter : str
        The opening-delimiter pattern.
    closing_delimiter : str or None, optional
        The closing-delimiter pattern. The pattern is the same as
        `opening_delimiter` if the argument is ``None`` or not provided.
        Defaults to ``None``.

    Returns
    -------
    ~collections.abc.Callable
        A decorator for modifying a subclass of `Preprocessor`.
    """
    def decorator(preprocessor_class):
        preprocessor_class._replace_nodes = _compile_replace_nodes(
            opening_delimiter, closing_delimiter)
        return preprocessor_class
    return decorator


_replace_code_nodes = _compile_replace_nodes(
    r"(?:(##|\$\$)|(['\"])\+\+)", r"(?:\1|\+\+\2)")


def code_nodes(preprocessor_class):
    """
    Modify a preprocessor to use code-syntax-friendly *node* delimiters.

    These delimiters do not break the syntax of programming languages
    for which ``$`` is a valid character in identifiers. (``#`` is
    usually not a valid character in identifiers.)

    =====================  ======================  ===================
    Preprocessor variable    Preprocessor input    Preprocessor output
    =====================  ======================  ===================
    ``my_var = "x"``       ``$$my_var$$ = 0``      ``x = 0``

                           ``obj.$$my_var$$ = 0``  ``obj.x = 0``

    ``my_str = "abc"``     ``s = '##my_str##'``    ``s = 'abc'``

                           ``s = "##my_str##"``    ``s = "abc"``

    ``my_num = 1.23``      ``i = '++my_num++'``    ``i = 1.23``

                           ``i = "++my_num++"``    ``i = 1.23``

    ``my_bool = "true"``   ``ok = '++my_bool++'``  ``ok = true``

                           ``ok = "++my_bool++"``  ``ok = true``

    ``my_bool = True``     ``ok = "++my_bool++"``  ``ok = true`` [1]_

                           ``ok = "++my_bool++"``  ``ok = True`` [2]_
    =====================  ======================  ===================

    .. [1] With `doxhooks.preprocessor_contexts.lowercase_booleans`.
    .. [2] With `doxhooks.preprocessor_contexts.startcase_booleans`.

    Parameters
    ----------
    preprocessor_class : type
        The subclass of `Preprocessor` to be modified.

    Returns
    -------
    type
        The modified subclass of `Preprocessor`.
    """
    preprocessor_class._replace_nodes = _replace_code_nodes
    return preprocessor_class
