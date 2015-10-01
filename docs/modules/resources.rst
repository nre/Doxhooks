resources
#########

.. automodule:: doxhooks.resources

.. autoclass:: doxhooks.resources.Resource

    .. autoattribute:: doxhooks.resources.Resource.Factory
        :annotation: = doxhooks.resource_factories.ResourceFactory

    .. automethod:: doxhooks.resources.Resource.__repr__
    .. automethod:: doxhooks.resources.Resource._write
    .. autoattribute:: doxhooks.resources.Resource.input_branch
    .. autoattribute:: doxhooks.resources.Resource.input_encoding
    .. automethod:: doxhooks.resources.Resource.new
    .. autoattribute:: doxhooks.resources.Resource.output_branch
    .. autoattribute:: doxhooks.resources.Resource.output_encoding
    .. autoattribute:: doxhooks.resources.Resource.output_newline
    .. autoattribute:: doxhooks.resources.Resource.server_hostname
    .. autoattribute:: doxhooks.resources.Resource.server_protocol
    .. autoattribute:: doxhooks.resources.Resource.server_rewrite
    .. autoattribute:: doxhooks.resources.Resource.server_root
    .. automethod:: doxhooks.resources.Resource.update
    .. autoattribute:: doxhooks.resources.Resource.url

.. autoclass:: doxhooks.resources.PreprocessedResource

    .. autoattribute:: doxhooks.resources.PreprocessedResource.Context
        :annotation: = doxhooks.preprocessor_contexts.PreprocessorContext

    .. autoattribute:: doxhooks.resources.PreprocessedResource.Preprocessor
        :annotation: = doxhooks.preprocessors.Preprocessor

    .. autoattribute:: doxhooks.resources.PreprocessedResource.Factory
        :annotation: = doxhooks.resource_factories.PreprocessedResourceFactory

    .. automethod:: doxhooks.resources.PreprocessedResource._write
    .. autoattribute:: doxhooks.resources.PreprocessedResource.input_encoding
    .. autoattribute:: doxhooks.resources.PreprocessedResource.output_encoding
