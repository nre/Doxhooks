#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


# Organise the preprocessor variables that are common to all my HTML
# resources into a shared context:
class MyHTMLContext(PreprocessorContext):

    # Define 'author' to mean 'Alan Smithee' in this context:
    author = "Alan Smithee"

    lang = "en"
    charset = "UTF-8"

    # Define a variable 'title' with a value that depends on the
    # variables 'film_title' and 'author':
    title = "##film_title## | ##author##'s Film Blog"

    # NB: The value of 'title' can depend on the values of 'film_title'
    # and 'author' because Doxhooks preprocesses these values in the
    # same way that it preprocesses input files.
    #
    # See 'preprocessor node' in the glossary for more details.

    description = "Facts about '##film_title##'."


# Organise my preprocessed HTML resources into a class of resources:
class MyHTMLResource(PreprocessedResource):

    # Link my HTML resources to their shared preprocessor context:
    Context = MyHTMLContext


my_resource_configs = [
    _(
        MyHTMLResource,
        input_filename="src/_film.html",
        output_filename="www/caligari.html",

        # Define the values of some variables in the context of this
        # resource:
        context_vars={
            "film_title": "The Cabinet of Dr. Caligari",
            "release_year": "1920",
        },
    ),
    _(
        MyHTMLResource,
        input_filename="src/_film.html",
        output_filename="www/placesun.html",

        context_vars={

            # Override the value of 'description' in the shared context
            # (MyHTMLContext) with a different value in the context of
            # this resource:
            "description": "Info on '##film_title##'.",

            "film_title": "A Place in the Sun",
            "release_year": "1951",
        },
    ),
]


def main():
    add_output_roots("www")

    Doxhooks(my_resource_configs).update_all()
    # Doxhooks will:
    # - Make the output directory 'www'.
    # - Read src/_film.html and write www/caligari.html.
    # - Read src/_film.html and write www/placesun.html.


if __name__ == "__main__":
    main()
