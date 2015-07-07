"""
Factories that make preprocessors customised for resources.

Exports
-------
PreprocessorFactory
    A factory that makes preprocessors customised for a resource.
"""


__all__ = [
    "PreprocessorFactory",
]


class PreprocessorFactory:
    """
    A factory that makes preprocessors customised for a resource.

    Class Interface
    ---------------
    make
        Return a new preprocessor that is customised for the resource.
    """

    def __init__(
            self, preprocessor_class, preprocessor_context_class, context_vars,
            input_file_domain):
        """
        Initialise the factory with preprocessor prerequisites.

        Preprocessing a resource requires:

        * The input files of that resource.
        * A preprocessor that is compatible with the syntax of those
          input files.
        * The preprocessor mini-language that is used in those input
          files.
        * The preprocessor variables that are used in those input files.

        Parameters
        ----------
        preprocessor_class : ~collections.abc.Callable
            `~doxhooks.preprocessors.Preprocessor` or a subclass (or other
            callable) that takes the same parameters and returns a
            preprocessor.
        preprocessor_context_class : ~collections.abc.Callable
            `~doxhooks.preprocessor_contexts.BasePreprocessorContext` or a
            subclass (or other callable) that takes the same parameters
            and returns a preprocessor context.
        context_vars : dict
            Some preprocessor variables. More variables can be added
            when calling `PreprocessorFactory.make`.
        input_file_domain : ~doxhooks.file_domains.InputFileDomain
            The input-file domain.
        """
        self._preprocessor_class = preprocessor_class
        self._preprocessor_context_class = preprocessor_context_class
        self._context_vars = context_vars
        self._input_file_domain = input_file_domain

    def make(self, output_file, **context_vars):
        r"""
        Return a new preprocessor that is customised for a resource.

        Parameters
        ----------
        output_file : TextIO
            An open file object that the preprocessor writes its output
            to.
        \**context_vars
            These keyword parameters and their arguments define the
            names and values of additional preprocessor variables.

        Returns
        -------
        ~doxhooks.preprocessors.Preprocessor
            An instance of the *preprocessor class* that this
            `PreprocessorFactory` is parameterised with.
        """
        if context_vars:
            variables = self._context_vars.copy()
            variables.update(context_vars)
        else:
            variables = self._context_vars

        return self._preprocessor_class(
            self._preprocessor_context_class(**variables),
            self._input_file_domain, output_file)
