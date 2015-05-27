from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.preprocessors import (
    Preprocessor, directive_delimiter, node_delimiters)
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class FeaturePreprocessedResource(PreprocessedResource):
    class Context(PreprocessorContext):
        test = "Passes test."


class DirectiveDelimiterResource(FeaturePreprocessedResource):
    @directive_delimiter("__open_directive__")
    class Preprocessor(Preprocessor):
        pass


class SymmetricNodeDelimitersResource(FeaturePreprocessedResource):
    @node_delimiters("__node__")
    class Preprocessor(Preprocessor):
        pass


class AsymmetricNodeDelimitersResource(FeaturePreprocessedResource):
    @node_delimiters("__open_node__", "__close_node__")
    class Preprocessor(Preprocessor):
        pass


resource_configs = {
    "directive_delimiter": _(
        DirectiveDelimiterResource,
        input_filename="input/_directive_delimiter.txt",
        output_filename="output/directive_delimiter.txt",
    ),
    "symmetric_node_delimiters": _(
        SymmetricNodeDelimitersResource,
        input_filename="input/_symmetric_node_delimiters.txt",
        output_filename="output/symmetric_node_delimiters.txt",
    ),
    "asymmetric_node_delimiters": _(
        AsymmetricNodeDelimitersResource,
        input_filename="input/_asymmetric_node_delimiters.txt",
        output_filename="output/asymmetric_node_delimiters.txt",
    ),
}


def main():
    add_output_roots("output")
    Doxhooks(resource_configs).update_all()


if __name__ == "__main__":
    main()
