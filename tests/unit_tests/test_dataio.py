import io
import unittest.mock as mock

import doxhooks.dataio as dataio
from doxhooks.errors import DoxhooksDataError, DoxhooksDataFileError
from pytest import fixture, mark

from doxhooks_pytest import withraises


class ExampleNonRestorableRepr:
    def __repr__(self):
        return "0"


class BaseTestDataIO:
    dummy_path = None


class TestLoading(BaseTestDataIO):
    @withraises
    def when_loading_literal_data(self, data_string):
        fake_input_file = io.StringIO(data_string)
        with mock.patch(
                "doxhooks.fileio.open_input", autospec=True,
                return_value=fake_input_file):
            return dataio.load_literals(self.dummy_path)

    @mark.parametrize(
        "data_string, data", [
            ("{}", {}),
        ])
    def test_literal_data_is_loaded_from_a_text_file(self, data_string, data):
        loaded_data = self.when_loading_literal_data(data_string)

        # then the data is returned.
        assert loaded_data == data

    @mark.parametrize("bad_data_string", ["{", "set()"])
    def test_loading_bad_literal_data_is_an_error(self, bad_data_string):
        self.when_loading_literal_data(
            bad_data_string, raises=DoxhooksDataFileError)

        assert self.error


class TestSaving(BaseTestDataIO):
    @fixture(autouse=True)
    def _setup_output_file(self, fake_output_file):
        self.file = fake_output_file

    @withraises
    def when_saving_literal_data(self, data):
        with mock.patch(
                "doxhooks.fileio.open_output", autospec=True,
                return_value=self.file):
            dataio.save_literals(self.dummy_path, data)

    @mark.parametrize(
        "data, data_string", [
            ({}, "{}"),
        ])
    def test_literal_data_is_saved_in_a_text_file(self, data, data_string):
        self.when_saving_literal_data(data)

        # then the data is saved.
        assert self.file.contents == data_string

    @mark.parametrize(
        "non_restorable_data", [set(), ExampleNonRestorableRepr()])
    def test_saving_non_restorable_data_is_an_error(self, non_restorable_data):
        self.when_saving_literal_data(
            non_restorable_data, raises=DoxhooksDataError)

        assert self.error
