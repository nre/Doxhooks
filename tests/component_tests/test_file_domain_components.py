from doxhooks.file_domains import OutputFileDomain
from pytest import mark


class BaseTestFileDomain:
    filename = "test.dat"
    encoding = "ascii"

    def given_an_output_file_domain(self):
        dummy_filetree = None
        self.domain = OutputFileDomain(
            dummy_filetree,
            "dummy_dir_path",
            self.filename,
            self.encoding,
            "dummy_newline",
        )


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

        # when getting the output filename
        path = self.domain.filename

        # then the filename is the initial filename mangled with the
        # latest fingerprint.
        assert path == mangled_path
