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
from doxhooks.resource_addresses import ResourceAddress


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
        Make and return a new resource.

    Subclass Interface
    ------------------
    _make_dependencies
        Make the dependencies of the resource and return them as kwargs.
    _get_config
        Return the named configuration value.
    _input_filetree
        The input-file tree of the resource.
    _input_file_domain
        The input-file domain of the resource.
    _output_filetree
        The output-file tree of the resource.
    _output_file_domain
        The output-file domain of the resource.
    _url_filetree
        The URL file tree of the resource.
    _address
        The address (URL) field of the resource.
    """

    def __init__(self, resource_class, **kwargs):
        r"""
        Initialise the factory with configuration data.

        Parameters
        ----------
        resource_class : ~doxhooks.resources.Resource
            The type of resource that the factory makes.
        \**kwargs
            Configuration data for the resources made by the factory.

        Attributes
        ----------
        _class : ~doxhooks.resources.Resource
            The argument of `resource_class`.
        """
        self._class = resource_class
        self._config_data = kwargs

    def _get_config(self, name):
        """
        Return the named configuration value.

        Parameters
        ----------
        name : str
            The name of the configuration value.

        Returns
        -------
        object
            The configuration value.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If the named value is not found in the *configuration data*
            of the `ResourceFactory`.
        """
        try:
            return self._config_data[name]
        except KeyError:
            raise DoxhooksLookupError(
                name, self._config_data, "the configuration data")

    @property
    def _input_filetree(self):
        """
        The input-file tree of the resource.

        *doxhooks.filetrees.FileTree*
        """
        try:
            tree = self._lazy_input_filetree
        except AttributeError:  # pragma: no branch
            tree = FileTree(
                self._get_config("input_branches"),
                name="`input_branches`"
            )
            self._lazy_input_filetree = tree
        return tree

    @property
    def _input_file_domain(self):
        """
        The input-file domain of the resource.

        *doxhooks.file_domains.InputFileDomain*
        """
        try:
            domain = self._lazy_input_file_domain
        except AttributeError:  # pragma: no branch
            domain = InputFileDomain(
                self._input_filetree,
                self._class.input_branch,
                self._get_config("input_filename"),
                self._class.input_encoding,
            )
            self._lazy_input_file_domain = domain
        return domain

    @property
    def _output_filetree(self):
        """
        The output-file tree of the resource.

        *doxhooks.filetrees.FileTree*
        """
        try:
            tree = self._lazy_output_filetree
        except AttributeError:  # pragma: no branch
            tree = FileTree(
                self._get_config("output_branches"),
                name="`output_branches`"
            )
            self._lazy_output_filetree = tree
        return tree

    @property
    def _output_file_domain(self):
        """
        The output-file domain of the resource.

        *doxhooks.file_domains.OutputFileDomain*
        """
        try:
            domain = self._lazy_output_file_domain
        except AttributeError:  # pragma: no branch
            domain = OutputFileDomain(
                self._output_filetree,
                self._class.output_branch,
                self._get_config("output_filename"),
                self._class.output_encoding,
                self._class.output_newline,
            )
            self._lazy_output_file_domain = domain
        return domain

    @property
    def _url_filetree(self):
        """
        The URL file tree of the resource.

        *doxhooks.filetrees.FileTree*
        """
        try:
            tree = self._lazy_url_filetree
        except AttributeError:  # pragma: no branch
            tree = FileTree(
                ChainMap(
                    self._get_config("url_branches"),
                    self._get_config("output_branches"),
                ),
                name="`ChainMap(url_branches, output_branches)`"
            )
            self._lazy_url_filetree = tree
        return tree

    @property
    def _address(self):
        """
        The address (URL) field of the resource.

        *doxhooks.resource_addresses.ResourceAddress*
        """
        try:
            address = self._lazy_address
        except AttributeError:  # pragma: no branch
            address = ResourceAddress(
                self._get_config("id"),
                self._output_file_domain,
                self._url_filetree,
                self._class.url_rewrite,
                self._class.url_root,
                self._class.url_prefix,
                self._get_config("urls"),
            )
            self._lazy_address = address
        return address

    def _make_dependencies(self):
        """
        Make the dependencies of the resource and return them as kwargs.

        Returns
        -------
        dict
            The keyword arguments for the resource constructor.
        """
        return {
            "address": self._address,
            "id": self._get_config("id"),
            "input_file_domain": self._input_file_domain,
            "output_file_domain": self._output_file_domain,
        }

    def make(self):
        """
        Make and return a new resource.

        Returns
        -------
        ~doxhooks.resources.Resource
            The new resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource configuration data is invalid.
        """
        dependencies = self._make_dependencies()
        return self._class(**dependencies)


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
    _preprocessor_factory
        The preprocessor factory of the resource.
    """

    @property
    def _preprocessor_factory(self):
        """
        The preprocessor factory of the resource.

        *doxhooks.preprocessor_factories.PreprocessorFactory*
        """
        try:
            factory = self._lazy_preprocessor_factory
        except AttributeError:  # pragma: no branch
            factory = PreprocessorFactory(
                self._class.Preprocessor,
                self._class.Context,
                self._get_config("context_vars"),
                self._input_file_domain,
            )
            self._lazy_preprocessor_factory = factory
        return factory

    def _make_dependencies(self):
        """
        Make the dependencies of the resource and return them as kwargs.

        Extends `ResourceFactory._make_dependencies` to make a
        preprocessor factory.

        Returns
        -------
        dict
            The keyword arguments for the preprocessed-resource
            constructor.
        """
        dependencies = super()._make_dependencies()
        dependencies["preprocessor_factory"] = self._preprocessor_factory
        return dependencies

    def make(self):
        """
        Make and return a new preprocessed resource.

        Extends `ResourceFactory.make` to add the following to the
        preprocessor-context variables:

        * *resource* is a reference to the preprocessed resource made by
          the factory.
        * *encoding* is the *output encoding* of the type of resource
          made by the factory.
        * *urls* is a dictionary of resource identities and URLs.

        Returns
        -------
        ~doxhooks.resources.PreprocessedResource
            The new preprocessed resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource configuration data is invalid.
        """
        try:
            context_vars = self._config_data["context_vars"]
        except KeyError:
            context_vars = {}
            self._config_data["context_vars"] = context_vars

        preprocessed_resource = super().make()
        context_vars.setdefault("resource", preprocessed_resource)
        context_vars.setdefault("encoding", self._class.output_encoding)
        context_vars.setdefault("urls", self._get_config("urls"))
        return preprocessed_resource
