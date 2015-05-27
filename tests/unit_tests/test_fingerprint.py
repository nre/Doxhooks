import io
import unittest.mock as mock

import doxhooks.fingerprint as fingerprint
from doxhooks.errors import DoxhooksTypeError, DoxhooksValueError
from pytest import fixture, mark

from doxhooks_pytest import withraises


class BaseTestFingerprint:
    encoding = "utf-8"
    string = "abcdef"
    strings = "abc", "def"
    filename = "test.dat"
    mangled_filename = "test-e80b5017098950fc58aad83c8c14978e.dat"
    dummy_path = None

    @fixture
    def _setup_monkeypatch(self, monkeypatch):
        self.monkeypatch = monkeypatch

    def given_a_customised(self, attribute_name, custom_value):
        self.monkeypatch.setattr(fingerprint, attribute_name, custom_value)

    @withraises
    def when_mangling_a_filename_with_the_fingerprint_of_strings(
            self, filename, *strings, encoding="dummy_encoding"):
        self.returned_filename = fingerprint.filename_for_strings(
            filename, *strings, encoding=encoding)

    def _make_fake_files(self, *strings):
        self.fake_files = [
            io.BytesIO(bytes(string, self.encoding)) for string in strings]

    @fixture
    def one_fake_file(self):
        self._make_fake_files(self.string)

    @fixture
    def two_fake_files(self):
        self._make_fake_files(*self.strings)

    @withraises
    def when_mangling_a_filename_with_the_fingerprint_of_files(
            self, filename, *paths):
        # NB: Passing more paths than expected does not raise an error
        # because the StopIteration raised by mock is caught by a for
        # loop in fingerprint._bytestrings_from_files().
        with mock.patch(
                "doxhooks.fileio.open_input", autospec=True,
                side_effect=self.fake_files):
            self.returned_filename = fingerprint.filename_for_files(
                filename, *paths)


class TestFingerprintStrings(BaseTestFingerprint):
    def test_returns_a_filename_mangled_with_the_fingerprint_of_a_string(self):
        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding)

        # then the mangled filename is returned.
        assert self.returned_filename == self.mangled_filename

    def test_returns_a_filename_mangled_with_the_fingerprint_of_some_strings(
            self):
        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, *self.strings, encoding=self.encoding)

        # then the mangled filename is returned.
        assert self.returned_filename == self.mangled_filename


class TestFingerprintFiles(BaseTestFingerprint):
    @mark.usefixtures("one_fake_file")
    def test_returns_a_filename_mangled_with_the_fingerprint_of_a_file(self):
        self.when_mangling_a_filename_with_the_fingerprint_of_files(
            self.filename, self.dummy_path)

        # then the mangled filename is returned.
        assert self.returned_filename == self.mangled_filename

    @mark.usefixtures("two_fake_files")
    def test_returns_a_filename_mangled_with_the_fingerprint_of_some_files(
            self):
        self.when_mangling_a_filename_with_the_fingerprint_of_files(
            self.filename, self.dummy_path, self.dummy_path)

        # then the mangled filename is returned.
        assert self.returned_filename == self.mangled_filename


class TestRewritableFieldInFilename(BaseTestFingerprint):
    @mark.parametrize(
        "rewritable_filename, mangled_rewritable_filename", [
            ("{}test.dat", "{}test-e80b5017098950fc58aad83c8c14978e.dat"),
            ("te{}st.dat", "te{}st-e80b5017098950fc58aad83c8c14978e.dat"),
            ("test{}.dat", "test{}-e80b5017098950fc58aad83c8c14978e.dat"),
            ("test.{}dat", "test-e80b5017098950fc58aad83c8c14978e.{}dat"),
            ("test.d{}at", "test-e80b5017098950fc58aad83c8c14978e.d{}at"),
            ("test.dat{}", "test-e80b5017098950fc58aad83c8c14978e.dat{}"),
            ("{}.dat", "{}-e80b5017098950fc58aad83c8c14978e.dat"),
            ("test.{}", "test-e80b5017098950fc58aad83c8c14978e.{}"),
        ])
    def test_a_rewritable_field_is_preserved_in_the_mangled_filename(
            self, rewritable_filename, mangled_rewritable_filename):
        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            rewritable_filename, self.string, encoding=self.encoding)

        # then the rewritable field is preserved in the mangled
        # filename.
        assert self.returned_filename == mangled_rewritable_filename

    @mark.parametrize(
        "rewritable_file_extension, mangled_rewritable_file_extension", [
            ("test{}", "test-e80b5017098950fc58aad83c8c14978e{}"),
            ("{}", "-e80b5017098950fc58aad83c8c14978e{}"),
        ])
    def test_a_rewritable_file_extension_is_preserved_in_the_mangled_filename(
            self, rewritable_file_extension,
            mangled_rewritable_file_extension):
        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            rewritable_file_extension, self.string, encoding=self.encoding)

        # then the rewritable field is preserved in the place of the dot
        # and file extension in the mangled filename.
        assert self.returned_filename == mangled_rewritable_file_extension


@mark.usefixtures("_setup_monkeypatch")
class TestCustomAlgorithm(BaseTestFingerprint):
    @mark.parametrize(
        "custom_algorithm, custom_mangled_filename", [
            ("sha1", "test-1f8ac10f23c5b5bc1167bda84b833e5c057a77d2.dat"),
        ])
    def test_the_fingerprinting_algorithm_is_customisable(
            self, custom_algorithm, custom_mangled_filename):
        self.given_a_customised("algorithm", custom_algorithm)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding)

        # then the filename is mangled with a hash from that algorithm.
        assert self.returned_filename == custom_mangled_filename

    @mark.parametrize("bad_custom_algorithm", ["not_an_algorithm"])
    def test_a_bad_algorithm_name_is_an_error(self, bad_custom_algorithm):
        self.given_a_customised("algorithm", bad_custom_algorithm)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding,
            raises=DoxhooksValueError)

        assert self.error.value == bad_custom_algorithm

    def test_a_bad_type_of_algorithm_name_is_an_error(self, not_str):
        bad_type_custom_algorithm = not_str
        self.given_a_customised("algorithm", bad_type_custom_algorithm)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding,
            raises=DoxhooksTypeError)

        assert self.error.value == bad_type_custom_algorithm


@mark.usefixtures("_setup_monkeypatch")
class TestCustomFingerprintFilenameSeparator(BaseTestFingerprint):
    @mark.parametrize(
        "custom_separator, custom_mangled_filename", [
            ("", "teste80b5017098950fc58aad83c8c14978e.dat"),
            (".", "test.e80b5017098950fc58aad83c8c14978e.dat"),
        ])
    def test_the_separator_between_file_stem_and_fingerprint_is_customisable(
            self, custom_separator, custom_mangled_filename):
        self.given_a_customised("separator", custom_separator)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding)

        # then the separator is between the file stem and the
        # fingerprint.
        assert self.returned_filename == custom_mangled_filename

    def test_a_bad_type_of_separator_is_an_error(self, not_str):
        bad_type_custom_separator = not_str
        self.given_a_customised("separator", bad_type_custom_separator)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding,
            raises=DoxhooksTypeError)

        assert self.error.value == bad_type_custom_separator


@mark.usefixtures("_setup_monkeypatch")
class TestCustomFingerprintMaxLength(BaseTestFingerprint):
    @mark.parametrize(
        "custom_max_length, custom_mangled_filename", [
            (0, "test-.dat"),
            (5, "test-e80b5.dat"),
            (None, BaseTestFingerprint.mangled_filename),
        ])
    def test_the_max_length_of_the_fingerprint_in_the_filename_is_customisable(
            self, custom_max_length, custom_mangled_filename):
        self.given_a_customised("max_length", custom_max_length)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding)

        # then the fingerprint in the filename is not longer than that
        # maximum length.
        assert self.returned_filename == custom_mangled_filename

    def test_a_bad_type_of_max_length_is_an_error(self, not_int_or_none):
        bad_type_custom_max_length = not_int_or_none
        self.given_a_customised("max_length", bad_type_custom_max_length)

        self.when_mangling_a_filename_with_the_fingerprint_of_strings(
            self.filename, self.string, encoding=self.encoding,
            raises=DoxhooksTypeError)

        assert self.error.value == bad_type_custom_max_length
