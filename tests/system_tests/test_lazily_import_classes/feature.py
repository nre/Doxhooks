from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.resource_configs import ResourceConfiguration as _


resource_configs = [
    _(
        "doxhooks.resources.Resource",
        input_filename="input/copy.txt",
        output_filename="output/copy.txt",
    ),
]


def main():
    add_output_roots("output")
    Doxhooks(resource_configs).update_all()


if __name__ == "__main__":
    main()
