#!/usr/bin/env python3
from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessor_contexts import PreprocessorContext
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class MyHTMLContext(PreprocessorContext):
    lang = "en"
    charset = "UTF-8"
    author = "Alan Smithee"
    title = "##film_title## | ##author##'s Film Blog"
    description = "Facts about '##film_title##'."

    # Define a filename variable that can be used in an 'insert'
    # directive:
    body = "src/_body.html"

    # In this context, the 'insert' directive '##insert body' is the
    # same as '##insert src/_body.html'.
    #
    # The directives are highlighted in the example file _html.html
    # further down this page.


class MyHTMLResource(PreprocessedResource):
    Context = MyHTMLContext


my_resource_configs = [
    _(
        MyHTMLResource,
        input_filename="src/_html.html",
        output_filename="www/celinejulie.html",
        context_vars={
            "film_title": "Celine and Julie Go Boating",

            # Define a filename variable that can be used in an 'insert'
            # directive:
            "main": "src/content/_celinejulie.html",
        },
    ),
    _(
        MyHTMLResource,
        input_filename="src/_html.html",
        output_filename="www/daywrath.html",
        context_vars={
            "film_title": "Day of Wrath",
            "main": "src/content/_daywrath.html",
        },
    ),
]


def main():
    add_output_roots("www")
    Doxhooks(my_resource_configs).update_all()


if __name__ == "__main__":
    main()
