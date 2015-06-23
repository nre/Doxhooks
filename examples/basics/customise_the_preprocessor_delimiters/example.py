#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.preprocessors import (
    Preprocessor, directive_delimiter, node_delimiters)
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


# 'Nested' classes:
#
#     class A:
#         class B:
#             [...]
#
# are sometimes more convenient to type than:
#
#     class X:
#         [...]
#
#     class A:
#         B = X


class MyHTMLContext(PreprocessorContext):
    author = "Alan Smithee"
    lang = "en"
    charset = "UTF-8"

    # Use the percent sign '%' to delimit the preprocessor variables
    # (instead of the default double hash '##'):
    title = "%film_title% | %author%'s Film Blog"
    description = "Facts about '%film_title%'."


class MyHTMLResource(PreprocessedResource):
    Context = MyHTMLContext

    # Customise the delimiters of my HTML preprocessor:
    @directive_delimiter("%")  # %directive
    @node_delimiters("%")  # %node%
    class Preprocessor(Preprocessor):
        pass

    # The delimiters can be any valid regular expressions. The
    # characters '.^$*+?\|()[]{}' have special significance in regular
    # expressions and must be escaped with a backslash `\`.
    #
    # Some suggestions:
    #
    # @directive_delimiter("#")         # #directive
    # @directive_delimiter("##")        # ##directive (the default)
    # @directive_delimiter("\$")        # $directive
    # @node_delimiters("#")             # #node#
    # @node_delimiters("##")            # ##node## (the default)
    # @node_delimiters("\$")            # $node$
    # @node_delimiters("\|")            # |node|
    # @node_delimiters("\[\[", "\]\]")  # [[node]]
    # @node_delimiters("\{\{", "\}\}")  # {{node}}
    # class Preprocessor(Preprocessor):
    #     pass


my_resource_configs = [
    _(
        MyHTMLResource,
        input_filename="src/_html.html",
        output_filename="www/rearwindow.html",
        context_vars={
            "content": "src/_release.html",
            "film_title": "Rear Window",
            "release_year": "1954",
        },
    ),
]


def main():
    add_output_roots("www")
    Doxhooks(my_resource_configs).update_all()


if __name__ == "__main__":
    main()
