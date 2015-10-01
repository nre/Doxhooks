"""
Factories that make information resources and their dependencies.

Exports
-------
ResourceFactory
    A factory that makes information resources.
PreprocessedResourceFactory
    A factory that makes preprocessed information resources.
"""


from collections import ChainMap

from doxhooks.errors import DoxhooksLookupError
from doxhooks.file_domains import InputFileDomain, OutputFileDomain
from doxhooks.filetrees import FileTree
from doxhooks.preprocessor_factories import PreprocessorFactory
from doxhooks.server_configs import ServerConfiguration


__all__ = [
    "PreprocessedResourceFactory",
    "ResourceFactory",
]


class ResourceFactory:
    """
    A factory that makes information resources.

    Class Interface
    ---------------
    make
        Make and return a new information resource.

    Subclass Interface
    ------------------
    _make_dependencies
        Return a `dict` of kwargs for the resource constructor.
    _get
        Return a named dependency.
    _make_input_filetree
        Return a new input-file tree for the resource.
    _make_input_file_domain
        Return a new input-file domain for the resource.
    _make_output_filetree
        Return a new output-file tree for the resource.
    _make_output_file_domain
        Return a new output-file domain for the resource.
    _make_url_filetree
        Return a new URL file tree for the resource.
    _make_server_config
        Return a new server configuration for the resource.
    """

    def __init__(self, resource_class, **kwargs):
        r"""
        Initialise the factory with configuration data.

        Parameters
        ----------
        resource_class : ~doxhooks.resources.Resource
            The type of information resource that the factory makes.
        \**kwargs
            Configuration data for the information resource and its
            dependencies.

        Attributes
        ----------
        _class : ~doxhooks.resources.Resource
            The argument of `resource_class`.
        """
        self._class = resource_class
        self._configuration = kwargs
        self._cache = {}

    def _get(self, name):
        """
        Return a named dependency.

        Named values are returned in the following order of preference:

        1. A configuration value with that name.
        2. A cached value with that name.
        3. The return value of a method with that name preceded by
           ``"_make_"``. This value is cached under the original name.

        Parameters
        ----------
        name : str
            The name of the dependency.

        Returns
        -------
        object
            The named dependency.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a dependency with that name is not found.
        """
        try:
            return self._configuration[name]
        except KeyError:
            pass
        try:
            return self._cache[name]
        except KeyError:
            pass
        try:
            factory_method = getattr(self, "_make_" + name)
        except AttributeError:
            pass
        else:
            value = self._cache[name] = factory_method()
            return value
        description = (
            "`{}` configuration, cache or factory methods"
            .format(type(self).__name__)
        )
        raise DoxhooksLookupError(name, self, description)

    def _make_input_filetree(self):
        """
        Return a new input-file tree for the resource.

        Returns
        -------
        ~doxhooks.filetrees.FileTree
            The input-file tree.
        """
        return FileTree(
            self._get("input_branches"),
            name="`input_branches`",
        )

    def _make_input_file_domain(self):
        """
        Return a new input-file domain for the resource.

        Returns
        -------
        ~doxhooks.file_domains.InputFileDomain
            The input-file domain.
        """
        return InputFileDomain(
            self._get("input_filetree"),
            self._class.input_branch,
            self._get("input_filename"),
            self._class.input_encoding,
        )

    def _make_output_filetree(self):
        """
        Return a new output-file tree for the resource.

        Returns
        -------
        ~doxhooks.filetrees.FileTree
            The output-file tree.
        """
        return FileTree(
            self._get("output_branches"),
            name="`output_branches`",
        )

    def _make_output_file_domain(self):
        """
        Return a new output-file domain for the resource.

        Returns
        -------
        ~doxhooks.file_domains.OutputFileDomain
            The output-file domain.
        """
        return OutputFileDomain(
            self._get("output_filetree"),
            self._class.output_branch,
            self._get("output_filename"),
            self._class.output_encoding,
            self._class.output_newline,
        )

    def _make_url_filetree(self):
        """
        Return a new URL file tree for the resource.

        Returns
        -------
        ~doxhooks.filetrees.FileTree
            The URL file tree.
        """
        return FileTree(
            ChainMap(
                self._get("url_branches"),
                self._get("output_branches"),
            ),
            name="`ChainMap(url_branches, output_branches)`",
        )

    def _make_server_config(self):
        """
        Return a new server configuration for the resource.

        Returns
        -------
        ~doxhooks.server_configs.ServerConfiguration
            The server configuration.
        """
        return ServerConfiguration(
            self._get("url_filetree"),
            self._class.server_protocol,
            self._class.server_hostname,
            self._class.server_root,
            self._class.server_rewrite,
        )

    def _make_dependencies(self):
        """
        Return a `dict` of kwargs for the resource constructor.

        Returns
        -------
        dict
            The keyword arguments for the resource constructor.
        """
        dependencies = self._configuration.copy()
        del dependencies["input_branches"]
        del dependencies["output_branches"]
        del dependencies["url_branches"]
        del dependencies["urls"]
        del dependencies["input_filename"]
        del dependencies["output_filename"]

        dependencies.update(
            input_file_domain=self._get("input_file_domain"),
            output_file_domain=self._get("output_file_domain"),
            server_config=self._get("server_config"),
            urls=self._get("urls"),
        )
        return dependencies

    def make(self):
        """
        Make and return a new information resource.

        Returns
        -------
        ~doxhooks.resources.Resource
            The new information resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource configuration data is invalid.
        """
        self._cache.clear()
        return self._class(**self._make_dependencies())


class PreprocessedResourceFactory(ResourceFactory):
    """
    A factory that makes preprocessed information resources.

    `PreprocessedResourceFactory` extends `ResourceFactory`.

    Class Interface
    ---------------
    make
        Extend `ResourceFactory.make` to add to the context variables.

    Subclass Interface
    ------------------
    _make_dependencies
        Extend `ResourceFactory._make_dependencies` to make a
        preprocessor factory.
    _make_preprocessor_factory
        Return a new preprocessor factory for the resource.
    """

    def _make_preprocessor_factory(self):
        """
        Return a new preprocessor factory for the resource.

        Returns
        -------
        ~doxhooks.preprocessor_factories.PreprocessorFactory
            The preprocessor factory.
        """
        return PreprocessorFactory(
            self._class.Preprocessor,
            self._class.Context,
            self._get("context_vars"),
            self._get("input_file_domain"),
        )

    def _make_dependencies(self):
        """
        Return a `dict` of kwargs for the resource constructor.

        Extends `ResourceFactory._make_dependencies` to make a
        preprocessor factory.

        Returns
        -------
        dict
            The keyword arguments for the preprocessed-resource
            constructor.
        """
        dependencies = super()._make_dependencies()
        del dependencies["context_vars"]

        dependencies.update(
            preprocessor_factory=self._get("preprocessor_factory"),
        )
        return dependencies

    def make(self):
        """
        Make and return a new preprocessed information resource.

        Extends `ResourceFactory.make` to add the following to the
        preprocessor-context variables:

        * *resource* is a reference to the preprocessed information
          resource.
        * *encoding* is the *output encoding* of the preprocessed
          information resource.
        * *urls* is a dictionary of resource identities and URLs.

        Returns
        -------
        ~doxhooks.resources.PreprocessedResource
            The new preprocessed information resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource configuration data is invalid.
        """
        context_vars = self._configuration.setdefault("context_vars", {})

        context_vars.setdefault("encoding", self._class.output_encoding)
        context_vars.setdefault("urls", self._get("urls"))

        preprocessed_resource = super().make()
        context_vars.setdefault("resource", preprocessed_resource)
        return preprocessed_resource
