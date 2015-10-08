import os
import unittest.mock as mock

from doxhooks.file_domains import InputFileDomain


class FakeFileTree:
    def path(self, dir_path, filename, *, rewrite=None):
        return os.path.join(dir_path, filename)


class BaseTestFileDomain:
    dir_path = ""
    filename = "test.dat"
    fake_filetree = FakeFileTree()

    def given_an_input_file_domain(self):
        self.domain = InputFileDomain(
            self.fake_filetree,
            self.dir_path,
            self.filename,
            "dummy_encoding",
        )


class TestRememberInputPaths(BaseTestFileDomain):
    def test_an_input_file_domain_remembers_all_input_paths(self):
        self.given_an_input_file_domain()
        # and input filenames which have been passed to the domain,
        self.domain.path()
        self.domain.path("test2.dat")
        with mock.patch("doxhooks.fileio.open_input", autospec=True):
            self.domain.open("test3.dat")

        # when getting the paths to all input files in that domain
        paths = self.domain.paths

        # then the paths to those filenames are returned.
        assert paths == {self.filename, "test2.dat", "test3.dat"}
