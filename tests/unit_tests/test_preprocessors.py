import io
import unittest.mock as mock

from doxhooks.preprocessors import Preprocessor
from pytest import mark


class FakeInputFileDomain:
    def __init__(self):
        self.open = mock.Mock(side_effect=self._open_fake_file)

    def _open_fake_file(self, *args):
        return io.StringIO()


class FakeOutputFile:
    def __init__(self):
        self.lines = []

    def write(self, line):
        self.lines.append(line)


class BaseTestPreprocessors:
    filename = "test_filename.src"

    def given_a_preprocessor(self, *, context=None, output_file=None):
        self.input = FakeInputFileDomain()
        self.prepro = Preprocessor(context, self.input, output_file)

    def _insert_file(self, filename, *, idempotent=False):
        self.prepro.insert_file(filename, idempotent=idempotent)

    def given_a_preprocessor_that_has_inserted_a_file(self):
        self.given_a_preprocessor()
        self._insert_file(self.filename)

    def when_inserting_an_input_file(self, filename):
        self._insert_file(filename)

    def when_inserting_that_file_again(self, *, idempotent):
        self.input.open.reset_mock()
        self._insert_file(self.filename, idempotent=idempotent)


class TestInputFiles(BaseTestPreprocessors):
    def test_a_preprocessor_remembers_each_input_file_that_it_opens(self):
        self.given_a_preprocessor()

        self.when_inserting_an_input_file(self.filename)

        # then the filename is remembered.
        assert self.filename in self.prepro.input_files

    @mark.parametrize("falsey_filename", [None, ""])
    def test_a_preprocessor_does_not_remember_a_placeholder_filename(
            self, falsey_filename):
        self.given_a_preprocessor()

        self.when_inserting_an_input_file(falsey_filename)

        # then the filename is not remembered.
        assert falsey_filename not in self.prepro.input_files

    def test_idempotent_file_insertion_does_not_reopen_a_remembered_file(self):
        self.given_a_preprocessor_that_has_inserted_a_file()

        self.when_inserting_that_file_again(idempotent=True)

        # then that file is not opened again.
        assert not self.input.open.called

    def test_non_idempotent_file_insertion_does_reopen_a_remembered_file(self):
        self.given_a_preprocessor_that_has_inserted_a_file()

        self.when_inserting_that_file_again(idempotent=False)

        # then that file is opened again.
        assert self.input.open.called


class TestLines(BaseTestPreprocessors):
    def test_a_string_of_lines_is_split_into_lines_and_not_characters(self):
        output_file = FakeOutputFile()
        self.given_a_preprocessor(output_file=output_file)

        # when the preprocessor is passed a string instead of an
        # iterable of strings
        self.prepro.insert_lines("line 1\nline 2\n")

        # then the string is split into lines, not characters.
        assert output_file.lines == ["line 1\n", "line 2\n"]

    def test_directive_indentation_does_not_leak_into_a_new_stack(self):
        output_file = FakeOutputFile()
        self.given_a_preprocessor(context=mock.Mock(), output_file=output_file)

        # when the preprocessor stack is started more than once
        self.prepro.insert_lines(["    ##indented_directive\n"])
        self.prepro.insert_lines(["No indent.\n"])

        # then the directive indentation from a previous stack does not
        # leak into the new stack.
        assert output_file.lines == ["No indent.\n"]
