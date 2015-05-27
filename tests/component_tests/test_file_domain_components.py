from doxhooks.file_domains import InputFileDomain, OutputFileDomain
from doxhooks.filetrees import InputFileTree, OutputFileTree
from pytest import mark


class BaseTestFileDomain:
    branch = ""
    filename = "test.dat"
    encoding = "ascii"
    newline = "dummy_newline"
    dummy_branches = None

    def given_an_input_file_domain(self):
        self.domain = InputFileDomain(
            InputFileTree(
                self.branch,
                self.filename,
                self.dummy_branches,
            ),
            self.encoding,
        )

    def given_an_output_file_domain(self):
        self.domain = OutputFileDomain(
            OutputFileTree(
                self.branch,
                self.filename,
                output_branches=self.dummy_branches,
                url_branches=self.dummy_branches,
            ),
            self.encoding,
            self.newline,
        )


class TestRememberInputPaths(BaseTestFileDomain):
    def test_an_input_file_domain_remembers_all_input_paths(self):
        self.given_an_input_file_domain()
        # and filenames for which the domain has returned paths,
        self.domain.path()
        self.domain.path("test2.dat")
        self.domain.path("test3.dat")

        # when getting the paths to all input files in that domain
        paths = self.domain.paths

        # then the paths to those filenames are returned.
        assert paths == {self.filename, "test2.dat", "test3.dat"}


class TestOutputFilenameMangling(BaseTestFileDomain):
    @mark.parametrize(
        "string1, string2, mangled_path", [
            ("abcdef", "abcdef",
                "test-e80b5017098950fc58aad83c8c14978e.dat"),
            ("abcdef", "ghijkl",
                "test-26e162d0b5706141bdb954900aebe804.dat"),
        ])
    def test_output_filename_mangling_is_idempotent(
            self, string1, string2, mangled_path):
        self.given_an_output_file_domain()
        # and the output filename is mangled more than once,
        self.domain.fingerprint_strings(string1)
        self.domain.fingerprint_strings(string2)

        # when getting the path to that output file
        path = self.domain.path()

        # then the returned path is the initial filename mangled with
        # the latest fingerprint.
        assert path == mangled_path
