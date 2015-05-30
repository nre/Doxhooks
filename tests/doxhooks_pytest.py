import filecmp
import importlib
import os
import sys

import pytest
from pytest import fixture


tests_path = os.path.dirname(__file__)
examples_path = os.path.normpath(
    os.path.join(tests_path, os.pardir, "examples"))


def withraises(method):
    # Decorator to wrap a test utility method. This allows the same
    # (wrapped) test utility method to be called for positive and
    # negative (error-raising) tests. The positive/negative switch is
    # triggered by the "raises" kwarg.
    def withraises_wrapper(self, *args, raises=None, **kwargs):
        if raises:
            with pytest.raises(raises) as excinfo:
                method(self, *args, **kwargs)
            error = excinfo.value
            self.error = error
            return error
        return method(self, *args, **kwargs)
    return withraises_wrapper


class OutputFilesTest:
    @property
    def dir_path(self):
        # Return the dir path of the module that imports this class.
        try:
            dir_path = self._dir_path
        except AttributeError:
            nodes = self.__module__.split(".")
            dir_path = os.path.abspath(os.path.join(*nodes[:-1]))
            self._dir_path = dir_path
        return dir_path

    @fixture(autouse=True)
    def _setup_user_module(self, monkeypatch):
        monkeypatch.chdir(self.dir_path)
        monkeypatch.syspath_prepend(self.dir_path)

        try:
            del sys.modules[self.user_module_name]
        except KeyError:
            pass
        self.user_module = importlib.import_module(self.user_module_name)

    def _redirect_copy(self, input_path, output_path):
        # A patch for doxhooks.fileio.copy.
        test_output_path = os.path.join(self.test_output_root, output_path)
        return self._fileio_copy(input_path, test_output_path)

    def _redirect_open_output(self, path, *args, **kwargs):
        # A patch for doxhooks.fileio.open_output.
        test_output_path = os.path.join(self.test_output_root, path)
        return self._fileio_open_output(test_output_path, *args, **kwargs)

    @fixture(autouse=True)
    def _setup_output_tmpdir(self, monkeypatch, tmpdir):
        # Patch doxhooks.fileio to prefix output paths with a tmpdir path.
        self.test_output_root = tmpdir.strpath

        fileio = importlib.import_module("doxhooks.fileio")
        fileio.add_output_roots(self.test_output_root)
        self._fileio_copy = fileio.copy
        monkeypatch.setattr(fileio, "copy", self._redirect_copy)
        self._fileio_open_output = fileio.open_output
        monkeypatch.setattr(fileio, "open_output", self._redirect_open_output)

    def _raise_error(self, error):
        raise error

    def assert_the_output_files_match_the_established_output_files(self):
        for path, directories, files in os.walk(
                self.output_directory, onerror=self._raise_error):

            test_path = os.path.join(self.test_output_root, path)
            entries = os.listdir(test_path)
            entries.sort()
            test_directories = []
            test_files = []
            for entry in entries:
                entry_path = os.path.join(test_path, entry)
                if os.path.isfile(entry_path):
                    test_files.append(entry)
                else:
                    test_directories.append(entry)

            assert test_directories == directories
            assert test_files == files

            for file in files:
                file_path = os.path.join(path, file)
                test_file_path = os.path.join(test_path, file)

                files_are_the_same = filecmp.cmp(
                    file_path, test_file_path, shallow=False)

                assert files_are_the_same, file + " are not the same."


class OutputTestDriver(OutputFilesTest):
    def test_the_output_files_match_the_established_output_files(self):
        self.user_module.main()
        self.assert_the_output_files_match_the_established_output_files()


class ExampleTestDriver(OutputTestDriver):
    user_module_name = "example"
    output_directory = "www"


class SystemTestDriver(OutputTestDriver):
    user_module_name = "feature"
    output_directory = "output"
