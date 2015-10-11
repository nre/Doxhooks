import os
import unittest.mock as mock

from doxhooks.file_domains import InputFileDomain


class FakeFileTree:
    def path(self, dir_path, filename, *, rewrite=None):
        return os.path.join(dir_path, filename)


class BaseTestFileDomain:
    dir_path = "one"
    filename = "test.dat"
    path = os.path.join(dir_path, filename)
    fake_filetree = FakeFileTree()

    def given_an_input_file_domain(self):
        self.domain = InputFileDomain(
            self.fake_filetree,
            self.dir_path,
            "dummy_filename",
            "dummy_encoding",
        )


class TestRememberInputPaths(BaseTestFileDomain):
    def test_the_paths_to_opened_files_are_remembered(self):
        self.given_an_input_file_domain()
        # that has opened a file,
        with mock.patch("doxhooks.fileio.open_input", autospec=True):
            self.domain.open(self.filename)

        # when getting the paths to all opened input files in that domain
        paths = self.domain.paths

        # then those paths are the path to that file.
        assert paths == {self.path}
