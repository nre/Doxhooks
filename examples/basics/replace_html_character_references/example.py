#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.preprocessors import HTMLPreprocessor
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class MyHTMLContext(PreprocessorContext):
    author = "Alan Smithee"
    lang = "en"
    charset = "UTF-8"
    title = "##film_title## | ##author##'s Film Blog"
    description = "Facts about '##film_title##'."

    # Use an HTML character reference in a preprocessor variable:
    copyright = "<small>&copyright; 2015 ##author##</small>"


# Configure an HTML preprocessor:
class MyHTMLPreprocessor(HTMLPreprocessor):

    # Make a dictionary of HTML character references and their
    # replacement values:
    character_references = {

        # Define '&copyright;' as an alias for the HTML4 entity
        # '&copy;':
        "copyright": "&copy;",

        # Replace the HTML5 entity '&dash;' with its decimal character
        # reference:
        "dash": "&#8208;",
        # Replace the HTML4 hexadecimal character reference '&#x2010;'
        # with its decimal character reference:
        "x2010": "&#8208;",

        # Replace character references with characters:
        "aacute": "á",
        # "eacute": "é",
        "iacute": "í",
        "oacute": "ó",
        "uacute": "ú",
    }

    # Suppress stderr warnings about unknown character references:
    #
    # suppress_character_reference_warnings = True


class MyHTMLResource(PreprocessedResource):
    Context = MyHTMLContext

    # Link my HTML resources to my HTML preprocessor:
    Preprocessor = MyHTMLPreprocessor


my_resource_configs = [
    _(
        MyHTMLResource,
        input_filename="src/_html.html",
        output_filename="www/satantango.html",
        context_vars={
            "film_title": "Sátántangó",
            "content": "src/_satantango.html",
        },
    ),
]


def main():
    add_output_roots("www")
    Doxhooks(my_resource_configs).update_all()


if __name__ == "__main__":
    main()
