from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import (
    PreprocessorContext, lowercase_booleans, startcase_booleans)
from doxhooks.preprocessors import Preprocessor, code_nodes
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class FeatureContext(PreprocessorContext):
    my_var = "x"
    my_str = "abc"
    my_num = 1.23
    my_bool = True


class CodeNodesPreprocessedResource(PreprocessedResource):
    @code_nodes
    class Preprocessor(Preprocessor):
        pass


class LowercaseBooleanPreprocessedResource(CodeNodesPreprocessedResource):
    @lowercase_booleans
    class Context(FeatureContext):
        my_str_bool = "true"


class StartCaseBooleanPreprocessedResource(CodeNodesPreprocessedResource):
    @startcase_booleans
    class Context(FeatureContext):
        my_str_bool = "True"


resource_configs = {
    "lowercase_boolean_code_nodes": _(
        LowercaseBooleanPreprocessedResource,
        input_filename="input/_code_nodes.js",
        output_filename="output/code_nodes.js",
    ),
    "startcase_boolean_code_nodes": _(
        StartCaseBooleanPreprocessedResource,
        input_filename="input/_code_nodes.py",
        output_filename="output/code_nodes.py",
    ),
}


def main():
    add_output_roots("output")
    Doxhooks(resource_configs).update_all()


if __name__ == "__main__":
    main()
