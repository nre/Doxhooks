#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class FeatureContext(PreprocessorContext):
    child = "child node"
    parent = "parent of a ##child##"
    grandparent = "grandparent of a ##child## is a parent of a ##parent##"

    change_quote = "If you don't like something,"

    integer = 123
    float = 1.23

    the_earth_is_round = True
    the_earth_is_flat = False


class FeaturePreprocessedResource(PreprocessedResource):
    Context = FeatureContext


resource_configs = {
    "preprocessor_features": _(
        FeaturePreprocessedResource,
        input_filename="input/_root.txt",
        output_filename="output/preprocessed.txt",
    ),
    "warning_directive": _(
        FeaturePreprocessedResource,
        input_filename="input/_warning.txt",
        output_filename="output/warning.txt",
    ),
    "error_directive": _(
        FeaturePreprocessedResource,
        input_filename="input/_error.txt",
        output_filename="output/error.txt",
    ),
}


def update_preprocessor_features():
    Doxhooks(resource_configs).update("preprocessor_features")


def update_warning_directive():
    Doxhooks(resource_configs).update("warning_directive")


def update_error_directive():
    Doxhooks(resource_configs).update("error_directive")


def main():
    add_output_roots("output")
    update_preprocessor_features()
    update_warning_directive()
    update_error_directive()


if __name__ == "__main__":
    main()
