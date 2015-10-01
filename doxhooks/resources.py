"""
The information resources.

An `information resource`:term: has an identity (`Resource.id`) and an
address (`Resource.url`). Its information is updated (`Resource.update`)
by reading its input files and writing its output files
(`Resource._write`).

Exports
-------
Resource
    An information resource.
PreprocessedResource
    A preprocessed information resource.

See Also
--------
doxhooks.resource_environments
    Environments in which the information resources are updated.
"""


import io
import os

import doxhooks.console as console
import doxhooks.fileio as fileio
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.preprocessors import Preprocessor
from doxhooks.resource_factories import (
    PreprocessedResourceFactory, ResourceFactory)


__all__ = [
    "PreprocessedResource",
    "Resource",
]


class Resource:
    """
    An information resource.

    Class Interface
    ---------------
    input_branch
        The path to the default directory for input files.
    input_encoding
        The encoding used when reading from input files.
    output_branch
        The path to the default directory for output files.
    output_encoding
        The encoding used when writing to output files.
    output_newline
        The *newline* argument used when writing to output files.
    server_protocol
        The protocol (*scheme*) in the default URL.
    server_hostname
        The host name (*domain name*) in the default URL.
    server_root
        The path on the server that the default-URL path is relative to.
    server_rewrite
        A value that is used to rewrite the path in the default URL.
    url
        The URL of the resource.
    update
        Update the output files and URL and return the input file paths.
    new
        Return a new resource made by `cls.Factory`.
    Factory
        The type of factory that makes a new instance of the resource.

    Subclass Interface
    ------------------
    _write
        Copy the input file to the output file path.

    Magic Methods
    -------------
    __repr__
        Override `object.__repr__` to feature the resource ID.

    See Also
    --------
    PreprocessedResource
        A preprocessed information resource.
    """

    Factory = ResourceFactory
    """
    The type of factory that makes a new instance of the resource.

    *doxhooks.resource_factories.ResourceFactory*

    `Resource.new` makes an instance of the factory, which makes an
    instance of the resource. Defaults to
    `~doxhooks.resource_factories.ResourceFactory`.
    """

    # The input_*, output_* and server_* class attributes below should
    # really be class attributes of InputFileDomain, OutputFileDomain
    # and ServerConfiguration, but are kept in the Resource namespace
    # for the convenience of the user, e.g.: A new class of resource
    # with new input and output branches can be defined by subclassing
    # only Resource, without having to subclass other classes too. The
    # downside is some code duplication and pseudo-namespacing (i.e.
    # "_" instead of ".").

    input_branch = os.curdir
    """
    The path to the default directory for input files.

    *str*

    The path can be relative or absolute. Defaults to the current
    directory.
    """

    output_branch = os.curdir
    """
    The path to the default directory for output files.

    *str*

    The path can be relative or absolute. Defaults to the current
    directory.
    """

    input_encoding = None
    """
    The encoding used when reading from input files.

    *str or None*

    The encoding of binary files is ``None``. Defaults to ``None``.
    """

    output_encoding = None
    """
    The encoding used when writing to output files.

    *str or None*

    The encoding of binary files is ``None``. Defaults to ``None``.
    """

    output_newline = None
    """
    The *newline* argument used when writing to output files.

    *str or None*

    See the *newline* parameter of `open` or `io.TextIOWrapper` for
    details. Should be ``None`` for binary files. Defaults to ``None``.

    Note
    ----
        Input files are always opened with `universal newlines`:term:.
    """

    server_protocol = None
    """
    The protocol (*scheme*) in the default URL.

    *str or None*

    See `~doxhooks.server_configs.ServerConfiguration` for details.
    Defaults to ``None``.
    """

    server_hostname = None
    """
    The host name (*domain name*) in the default URL.

    *str or None*

    See `~doxhooks.server_configs.ServerConfiguration` for details.
    Defaults to ``None``.
    """

    server_root = None
    """
    The path on the server that the default-URL path is relative to.

    *str or None*

    See `~doxhooks.server_configs.ServerConfiguration` for details.
    Defaults to ``None``.
    """

    server_rewrite = None
    """
    A value that is used to rewrite the path in the default URL.

    *object*

    See `~doxhooks.filetrees.FileTree.path` for details. Defaults to
    ``None``.
    """

    def __init__(
            self, *, id, input_file_domain, output_file_domain, server_config,
            urls):
        """
        Initialise the resource with an identity and configurations.

        A new resource is more conveniently obtained by calling the
        class method `Resource.new`.

        Parameters
        ----------
        id : ~collections.abc.Hashable
            Keyword-only. The identity of the resource.
        input_file_domain : ~doxhooks.file_domains.InputFileDomain
            Keyword-only. The input-file domain of the resource.
        output_file_domain : ~doxhooks.file_domains.OutputFileDomain
            Keyword-only. The output-file domain of the resource.
        server_config : ~doxhooks.server_configs.ServerConfiguration
            Keyword-only. A configuration for computing the default URL.
        urls : ~doxhooks.url_mappings.URLMapping
            Keyword-only. A mapping of resource identities to URLs.

        Attributes
        ----------
        id : ~collections.abc.Hashable
            The argument of `id`.
        """
        self.id = id  # A parameter, not the built-in function.
        self._input = input_file_domain
        self._output = output_file_domain
        self._server_config = server_config
        self._urls = urls

    def __repr__(self):
        """
        Return a string featuring the class name and resource ID.

        Overrides `object.__repr__`.

        Returns
        -------
        str
            A representation of the resource.
        """
        return "<{} object id={!r}>".format(type(self).__name__, self.id)

    @classmethod
    def new(cls, **kwargs):
        r"""
        Return a new resource made by `cls.Factory`.

        Extend `Resource.new` to modify the keyword arguments before
        they configure a new instance of `cls.Factory`, or to handle the
        new resource before it is returned to the caller.

        Parameters
        ----------
        \**kwargs
            The configuration of `cls.Factory`.

        Returns
        -------
        Resource
            The new resource.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource configuration data is invalid.
        """
        return cls.Factory(cls, **kwargs).make()

    @property
    def url(self):
        """
        The URL of the resource.

        The default URL of a resource depends on the *output file* path
        and the *server configuration*.

        The default URL can be overridden by:

        * Overriding `Resource.url` in a subclass.
        * Assigning a value to `self.url` before `self.url` has been
          accessed.

        A value of ``None`` denotes that the resource does not have a
        URL.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource URL data is invalid.
        """
        try:
            url = self._urls[self.id]
        except KeyError:
            url = self._server_config.url_for_file(
                self._output.branch, self._output.filename
            )
            self._urls[self.id] = url
        return url

    @url.setter
    def url(self, url):
        """The URL of the resource."""
        self._urls[self.id] = url

    def _fingerprint_files(self, rewrites=(None,)):
        # Mangle the output filename with a fingerprint of the input
        # file.
        paths = [self._input.path(rewrite=rewrite) for rewrite in rewrites]
        self._output.fingerprint_files(*paths)

    def _copy(self, rewrites=(None,)):
        # Copy the input file to the output file path.
        for rewrite in rewrites:
            fileio.copy(
                self._input.path(rewrite=rewrite),
                self._output.path(rewrite=rewrite))

    def _write(self):
        """
        Copy the input file to the output file path.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be copied.
        """
        self._copy()

    def update(self):
        """
        Update the output files and URL and return the input file paths.

        Returns
        -------
        set
            The paths to the input files that the resource depends on.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource data is invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        console.blank_line()
        console.info(self.id)
        self._write()
        url = self.url
        self._urls[self.id] = url
        if url is not None:
            console.log("URL:", url)
        return self._input.paths


class PreprocessedResource(Resource):
    """
    A preprocessed information resource.

    `PreprocessedResource` extends `Resource`.

    Class Interface
    ---------------
    Context
        The type of preprocessor mini-language that the resource uses.
    Preprocessor
        The type of preprocessor that the resource uses.
    Factory
        Override `Resource.Factory` with a factory for this resource.
    input_encoding
        Override `Resource.input_encoding`.
    output_encoding
        Override `Resource.output_encoding`.

    Subclass Interface
    ------------------
    _write
        Override `Resource.write` to preprocess the input file.
    """

    Context = PreprocessorContext
    """
    The type of preprocessor mini-language that the resource uses.

    *doxhooks.preprocessor_contexts.BasePreprocessorContext*

    Defaults to `~doxhooks.preprocessor_contexts.PreprocessorContext`.
    """

    Preprocessor = Preprocessor
    """
    The type of preprocessor that the resource uses.

    *doxhooks.preprocessors.Preprocessor*

    Defaults to `~doxhooks.preprocessors.Preprocessor`.
    """

    Factory = PreprocessedResourceFactory
    """
    The type of factory that makes a new instance of the resource.

    *doxhooks.resource_factories.PreprocessedResourceFactory*

    Overrides `Resource.Factory`. Defaults to
    `~doxhooks.resource_factories.PreprocessedResourceFactory`.
    """

    input_encoding = "utf-8"
    """
    The encoding used when reading from input files.

    *str or None*

    Overrides `Resource.input_encoding`. Defaults to ``"utf-8"``.
    """

    output_encoding = "utf-8"
    """
    The encoding used when writing to output files.

    *str or None*

    Overrides `Resource.output_encoding`. Defaults to ``"utf-8"``.
    """

    def __init__(self, *, preprocessor_factory, **kwargs):
        """
        Initialise the resource with a preprocessor factory.

        The `PreprocessedResource` constructor extends the `Resource`
        constructor by adding a `preprocessor_factory` parameter.

        Parameters
        ----------
        preprocessor_factory : ~doxhooks.preprocessor_factories.PreprocessorFactory
            Keyword-only. A factory that makes preprocessors customised
            for the resource.
        """
        super().__init__(**kwargs)
        self._preprocessor_factory = preprocessor_factory

    def _preprocess(self, **context_vars):
        # Preprocess the input file and return the output string.
        with io.StringIO() as output:
            preprocessor = self._preprocessor_factory.make(
                output, **context_vars)
            preprocessor.insert_file(self._input.filename, idempotent=True)
            return output.getvalue()

    def _write(self):
        """
        Preprocess the input file and write the output file.

        Overrides `Resource._write`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource data is invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or the output file cannot
            be written.
        """
        with self._output.open() as output:
            preprocessor = self._preprocessor_factory.make(output)
            preprocessor.insert_file(self._input.filename, idempotent=True)
