#!/usr/bin/env python3
import io

from doxhooks.main import Doxhooks, add_output_roots
from doxhooks.resource_configs import ResourceConfiguration as _
from doxhooks.resources import PreprocessedResource, Resource


class FingerprintedResource(Resource):
    def _write(self):
        self._fingerprint_files()
        self._copy()


class FingerprintedPreprocessedResource(PreprocessedResource):
    def _write(self):
        with io.StringIO() as output:
            preprocessor = self._preprocessor_factory.make(output)
            preprocessor.insert_file(self._input.filename, idempotent=True)
            content = output.getvalue()

        self._output.fingerprint_strings(content)
        self._output.save(content)


resource_configs = [
    _(
        FingerprintedResource,
        input_filename="input/image.png",
        output_filename="output/resource.png",
    ),
    _(
        FingerprintedPreprocessedResource,
        input_filename="input/_text.txt",
        output_filename="output/preprocessed.txt",
    ),
]


def main():
    add_output_roots("output")
    Doxhooks(resource_configs).update_all()


if __name__ == "__main__":
    main()
