import io
import os

import doxhooks.fileio as fileio
from doxhooks.errors import (
    DoxhooksFileSystemError, DoxhooksOutputPathError, DoxhooksValueError)
from pytest import fail, fixture, mark

from doxhooks_pytest import withraises


class BaseTestFileIO:
    no_encoding = None
    text_encoding = "utf-8"

    @fixture
    def directory_path(self, tmpdir):
        return tmpdir.strpath

    @fixture
    def input_file_path(self, tmpdir):
        file = tmpdir.join("input.dat")
        file.ensure()
        return file.strpath

    @fixture
    def missing_input_file_path(self, tmpdir):
        path = tmpdir.join("missing.dat").strpath
        assert not os.path.exists(path)
        return path

    @fixture
    def output_tmpdir(self, tmpdir):
        fileio.add_output_roots(tmpdir.strpath)
        return tmpdir

    @fixture
    def output_file_path(self, output_tmpdir):
        path = output_tmpdir.join("output.dat").strpath
        assert not os.path.exists(path)
        return path

    @fixture
    def cwd_output_file_path(self, monkeypatch, output_tmpdir):
        monkeypatch.chdir(output_tmpdir.strpath)
        filename = "cwd_file.dat"
        assert not os.path.exists(filename)
        return filename

    @fixture
    def new_output_directory_and_file_path(self, output_tmpdir):
        path = output_tmpdir.join("missing_dir", "missing.dat").strpath
        assert not os.path.exists(path)
        return path

    @fixture
    def generic_file_path(self, output_tmpdir):
        file = output_tmpdir.join("filename.src")
        file.ensure()
        self.path = file.strpath

    @fixture(params=["", "/"])
    def invalid_path(self, request):
        path = request.param
        fileio.add_output_roots(path)

        def remove_output_root():
            fileio._output_roots.remove(os.path.abspath(path))

        request.addfinalizer(remove_output_root)
        return path

    @fixture
    def open_input(self):
        self.open = fileio.open_input

    @fixture
    def open_output(self):
        self.open = fileio.open_output

    @fixture(params=[fileio.open_input, fileio.open_output])
    def open_input_and_output(self, request):
        self.open = request.param

    def _open(self, path, encoding, newline):
        self.file_object = self.open(path, encoding, newline)

    def then_the_file_exists(self, file_path):
        file_exists = os.path.exists(file_path)
        assert file_exists


class TestCopying(BaseTestFileIO):
    @withraises
    def when_copying_a_file_from_an_input_path_to_an_output_path(
            self, input_path, output_path):
        fileio.copy(input_path, output_path)

    def test_copying_a_file_preserves_the_input_file(
            self, input_file_path, output_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            input_file_path, output_file_path)

        self.then_the_file_exists(input_file_path)

    def test_copying_a_file_writes_the_output_file(
            self, input_file_path, output_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            input_file_path, output_file_path)

        self.then_the_file_exists(output_file_path)

    def test_new_output_directories_are_silently_made(
            self, input_file_path, new_output_directory_and_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            input_file_path, new_output_directory_and_file_path)

        self.then_the_file_exists(new_output_directory_and_file_path)

    def test_copying_to_a_filename_without_a_directory_is_not_an_error(
            self, input_file_path, cwd_output_file_path):
        try:
            self.when_copying_a_file_from_an_input_path_to_an_output_path(
                input_file_path, cwd_output_file_path)
        except DoxhooksFileSystemError:
            fail("Copying to a filename-only path should not raise an error.")

    def test_copying_a_missing_file_is_an_error(
            self, missing_input_file_path, output_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            missing_input_file_path, output_file_path,
            raises=DoxhooksFileSystemError)

        assert self.error

    def test_copying_a_directory_is_an_error(
            self, directory_path, output_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            directory_path, output_file_path, raises=DoxhooksFileSystemError)

        assert self.error

    def test_copying_from_an_invalid_input_path_is_an_error(
            self, invalid_path, output_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            invalid_path, output_file_path, raises=DoxhooksFileSystemError)

        assert self.error

    def test_copying_to_an_invalid_output_path_is_an_error(
            self, input_file_path, invalid_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            input_file_path, invalid_path, raises=DoxhooksFileSystemError)

        assert self.error

    def test_copying_to_a_non_output_path_is_an_error(self, input_file_path):
        self.when_copying_a_file_from_an_input_path_to_an_output_path(
            input_file_path, input_file_path, raises=DoxhooksOutputPathError)

        assert self.error


@mark.usefixtures("open_input_and_output", "generic_file_path")
class TestOpeningATextFile(BaseTestFileIO):
    def when_opening_a_file_with_an_encoding(self, encoding, newline=None):
        self._open(self.path, encoding, newline)

    def test_opening_a_text_file_returns_an_open_text_file(self):
        self.when_opening_a_file_with_an_encoding(self.text_encoding)

        # then an open text file is returned.
        assert isinstance(self.file_object, io.TextIOWrapper)

    def test_opening_an_encoded_file_returns_an_open_encoded_file(self):
        self.when_opening_a_file_with_an_encoding(self.text_encoding)

        # then the opened text file has that encoding.
        assert self.file_object.encoding == self.text_encoding


@mark.usefixtures("open_input_and_output", "generic_file_path")
class TestOpeningABinaryFile(BaseTestFileIO):
    @withraises
    def when_opening_a_file_without_an_encoding(self, newline=None):
        self._open(self.path, self.no_encoding, newline)

    def test_opening_a_binary_file_returns_an_open_binary_file(self):
        self.when_opening_a_file_without_an_encoding()

        # then an open binary file is returned.
        assert isinstance(self.file_object, io.BufferedIOBase)

    @mark.parametrize("newline_not_none", ["", "\n", "not_a_newline"])
    def test_any_newline_for_a_binary_file_is_an_error(self, newline_not_none):
        self.when_opening_a_file_without_an_encoding(
            newline=newline_not_none, raises=DoxhooksValueError)

        assert self.error.value == newline_not_none


@mark.usefixtures("open_input")
class TestOpeningAnInputFile(BaseTestFileIO):
    @withraises
    def when_opening_an_input_file(self, path):
        self._open(path, self.no_encoding, newline=None)

    def test_opening_a_missing_input_file_is_an_error(
            self, missing_input_file_path):
        self.when_opening_an_input_file(
            missing_input_file_path, raises=DoxhooksFileSystemError)

        assert self.error


@mark.usefixtures("open_output")
class TestOpeningAnOutputFile(BaseTestFileIO):
    @withraises
    def when_opening_an_output_file(self, path):
        self._open(path, self.no_encoding, newline=None)

    def test_new_output_directories_are_silently_made(
            self, new_output_directory_and_file_path):
        self.when_opening_an_output_file(new_output_directory_and_file_path)

        self.then_the_file_exists(new_output_directory_and_file_path)

    def test_opening_a_filename_without_a_directory_is_not_an_error(
            self, cwd_output_file_path):
        try:
            self.when_opening_an_output_file(cwd_output_file_path)
        except DoxhooksFileSystemError:
            fail("Opening a filename-only path should not raise an error.")

    def test_opening_an_output_file_with_a_non_output_path_is_an_error(
            self, input_file_path):
        self.when_opening_an_output_file(
            input_file_path, raises=DoxhooksOutputPathError)

        assert self.error


@mark.usefixtures("open_input_and_output", "generic_file_path")
class TestOpeningAFile(BaseTestFileIO):
    @fixture(autouse=True)
    def _setup(self):
        self.encoding = self.text_encoding
        self.newline = None

    @withraises
    def when_opening_a_file(self, path, encoding, newline):
        self._open(path, encoding, newline)

    def test_opening_a_directory_as_a_file_is_an_error(self, directory_path):
        self.when_opening_a_file(
            directory_path, self.encoding, self.newline,
            raises=DoxhooksFileSystemError)

        assert self.error

    def test_opening_an_invalid_path_is_an_error(self, invalid_path):
        self.when_opening_a_file(
            invalid_path, self.encoding, self.newline,
            raises=DoxhooksFileSystemError)

        assert self.error


class TestConvenienceWrappers(BaseTestFileIO):
    no_encoding = BaseTestFileIO.no_encoding
    text_encoding = BaseTestFileIO.text_encoding

    data = "test{0}data{0}"
    system_newline = os.linesep
    unix_newline = "\n"
    system_data = data.format(system_newline)
    system_data_bytes = bytes(system_data, "ascii")
    unix_data = data.format(unix_newline)
    unix_data_bytes = bytes(unix_data, "ascii")

    @mark.parametrize(
        "encoding, newline, data", [
            (no_encoding, None, system_data_bytes),
            (text_encoding, None, unix_data),
            (text_encoding, system_newline, system_data),
        ])
    def test_data_is_loaded_from_a_file(
            self, input_file_path, encoding, newline, data):
        # Given the path to a data file,
        path = input_file_path
        with open(path, "bw") as file:
            file.write(self.system_data_bytes)

        # when loading data from the file
        returned_data = fileio.load(path, encoding, newline)

        # then the data is returned.
        assert returned_data == data

    @withraises
    def when_saving_data_to_a_file(self, path, data, encoding, newline=None):
        fileio.save(path, data, encoding, newline)

    @mark.parametrize(
        "data, encoding, newline, data_bytes", [
            (system_data_bytes, no_encoding, None, system_data_bytes),
            (unix_data_bytes, no_encoding, None, unix_data_bytes),
            (system_data, text_encoding, "", system_data_bytes),
            (unix_data, text_encoding, None, system_data_bytes),
            (unix_data, text_encoding, "", unix_data_bytes),
        ])
    def test_data_is_saved_in_a_file(
            self, output_file_path, data, encoding, newline, data_bytes):
        path = output_file_path
        self.when_saving_data_to_a_file(path, data, encoding, newline)

        # then the data is saved in the file.
        with open(path, "br") as file:
            file_contents = file.read()
        assert file_contents == data_bytes

    def test_saving_data_to_a_non_output_path_is_an_error(
            self, input_file_path):
        self.when_saving_data_to_a_file(
            input_file_path, "data", self.text_encoding,
            raises=DoxhooksOutputPathError)

        assert self.error
