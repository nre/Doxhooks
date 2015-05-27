from doxhooks.main import Doxhooks, add_output_roots
# Rename ResourceConfiguration as `_` because it is used a lot:
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import Resource


# Make a list of the resources in my project:
my_resource_configs = [

    # The first resource is a copy of source/image.png. The copy will be
    # www/logo.png:

    _(  # NB: `_` is the name we gave to ResourceConfiguration.
        Resource,
        input_filename="source/image.png",
        output_filename="www/logo.png",
    ),

    # The second resource is a copy of source/robots.txt:
    _(
        Resource,
        input_filename="source/robots.txt",
        output_filename="www/robots.txt",
    ),
]


def main():
    # Tell Doxhooks that it is ok to write (and overwrite) files in the
    # directory 'www' (and its subdirectories) but nowhere else:
    add_output_roots("www")
    # (This is a safeguard against accidentally overwriting the input
    # files because of a typo or blunder.)

    # Tell Doxhooks to update the resources in my project:
    Doxhooks(my_resource_configs).update_all()
    # Doxhooks will:
    # - Make the output directory 'www'.
    # - Copy source/image.png to www/logo.png.
    # - Copy source/robots.txt to www/robots.txt.


if __name__ == "__main__":
    main()
