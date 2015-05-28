#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import Resource


resource_configs = [
    _(
        Resource,
        input_filename="input/copy.txt",
        output_filename="output/copy.txt",
    ),
    _(
        Resource,
        input_filename="input/rename_me.txt",
        output_filename="output/renamed.txt",
    ),
]


def main():
    add_output_roots("output")
    Doxhooks(resource_configs).update_all()


if __name__ == "__main__":
    main()
