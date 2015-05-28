#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class ControlResource(PreprocessedResource):
    class Context(PreprocessorContext):
        test = "pass"


class DependentResource(PreprocessedResource):
    class Context(PreprocessorContext):
        test = "fail"


resource_configs = {
    "control": _(
        ControlResource,
        input_filename="input/_control.txt",
        output_filename="output/control.txt",
    ),
    "dependent": _(
        DependentResource,
        input_filename="input/_dependent.txt",
        output_filename="output/dependent.txt",
    ),
}


def main():
    add_output_roots("output")
    doxhooks = Doxhooks(resource_configs)

    doxhooks.update_all()

    ControlResource.Context.test = "fail"
    DependentResource.Context.test = "pass"

    doxhooks.update_dependents("input/_dependent.txt")


if __name__ == "__main__":
    main()
