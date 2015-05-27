from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.preprocessors import HTMLPreprocessor
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource


class FeatureHTMLPreprocessor(HTMLPreprocessor):
    character_references = {
        "copy": "©",
        "169": "©",
        "xA9": "©",

        "233": "&eacute;",
        "xE9": "&eacute;",

        "ntilde": "&#241;",
        "xF1": "&#241;",

        "psi": "&#x3C8;",
        "968": "&#x3C8;",

        "whatever": "Arbitrary text.",
    }


class HTMLResource(PreprocessedResource):
    Preprocessor = FeatureHTMLPreprocessor


class SilentHTMLResource(HTMLResource):
    class Preprocessor(FeatureHTMLPreprocessor):
        suppress_character_reference_warnings = True


resource_configs = {
    "html_preprocessor": _(
        HTMLResource,
        input_filename="input/_html.html",
        output_filename="output/preprocessed.html",
    ),
    "silent_html_preprocessor": _(
        SilentHTMLResource,
        input_filename="input/_html.html",
        output_filename="output/silenced.html",
    ),
}


def update_html_preprocessor():
    add_output_roots("output")
    Doxhooks(resource_configs).update("html_preprocessor")


def update_silent_html_preprocessor():
    Doxhooks(resource_configs).update("silent_html_preprocessor")


def main():
    update_html_preprocessor()
    update_silent_html_preprocessor()


if __name__ == "__main__":
    main()
