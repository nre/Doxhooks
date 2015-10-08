import os

from doxhooks.errors import DoxhooksDataError, DoxhooksLookupError
from doxhooks.filetrees import FileTree, normalise_path
from pytest import mark

from doxhooks_pytest import withraises


def replace_sep_with_slash(path):
    return path.replace(os.sep, "/")


class TestNormalisePath:
    def when_normalising_a_path(self, path):
        self.path = normalise_path(path)

    @mark.parametrize(
        "path, normalised_path", [
            ("/", "/"),
            ("/test.src", "/test.src"),
            (".", "."),
            ("./test.src", "./test.src"),
            ("test.src", "./test.src"),
            ("alpha/./test.src", "./alpha/test.src"),
            ("alpha/../test.src", "./test.src"),
        ])
    def test_a_normalised_path_is_absolute_or_explicitly_relative(
            self, path, normalised_path):
        self.when_normalising_a_path(path)

        # then the normalised path is absolute or explicitly relative.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == normalised_path


class BaseTestFileTree:
    def given_a_filetree(self):
        self.filetree = FileTree({
            "one": "alpha",
            "uno": "<one>",
            "two": "<one>beta",
        })

    @withraises
    def when_computing_a_path(self, dir_path, filename=None, *, rewrite=None):
        self.path = self.filetree.path(dir_path, filename, rewrite=rewrite)


class TestComputingPath(BaseTestFileTree):
    @mark.parametrize(
        "dir_path, filename, path", [
            ("/", None, "/"),
            ("/test.src", None, "/test.src"),
            ("/", "test.src", "/test.src"),
            ("/alpha", "test.src", "/alpha/test.src"),
            ("/alpha/", "test.src", "/alpha/test.src"),

            (".", None, "."),
            ("./test.src", None, "./test.src"),
            (".", "test.src", "./test.src"),
            ("./alpha", "test.src", "./alpha/test.src"),
            ("./alpha/", "test.src", "./alpha/test.src"),

            ("", None, "."),
            ("test.src", None, "./test.src"),
            ("", "test.src", "./test.src"),
            ("alpha", "test.src", "./alpha/test.src"),
            ("alpha/", "test.src", "./alpha/test.src"),
        ])
    def test_computed_paths_are_absolute_or_relative_to_the_working_directory(
            self, dir_path, filename, path):
        self.given_a_filetree()

        self.when_computing_a_path(dir_path, filename)

        # then the computed path is absolute or relative to the working
        # directory.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == path

    @mark.parametrize(
        "dir_path, normalised_path", [
            ("dir/./test.src", "./dir/test.src"),
            ("wrong_way/../test.src", "./test.src"),
        ])
    def test_dot_notation_inside_a_path_is_resolved(
            self, dir_path, normalised_path):
        self.given_a_filetree()

        self.when_computing_a_path(dir_path)

        # then the normalised path is returned.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == normalised_path


class TestResolvingRootName(BaseTestFileTree):
    @mark.parametrize(
        "rooted_path, filename, path", [
            ("<one>", None, "./alpha"),
            ("<uno>", None, "./alpha"),
            ("<one>test.src", None, "./alpha/test.src"),
            ("<uno>test.src", None, "./alpha/test.src"),
            ("<two>test.src", None, "./alpha/beta/test.src"),

            ("<one>", "test.src", "./alpha/test.src"),
            ("<uno>", "test.src", "./alpha/test.src"),
            ("<one>", "beta/test.src", "./alpha/beta/test.src"),
            ("<uno>", "beta/test.src", "./alpha/beta/test.src"),
            ("<one>beta", "test.src", "./alpha/beta/test.src"),
            ("<uno>beta", "test.src", "./alpha/beta/test.src"),
            ("<two>gamma", "test.src", "./alpha/beta/gamma/test.src"),

            ("<one>/", "test.src", "./alpha/test.src"),
            ("<uno>/", "test.src", "./alpha/test.src"),
            ("<one>/beta", "test.src", "./alpha/beta/test.src"),
            ("<uno>/beta", "test.src", "./alpha/beta/test.src"),
            ("<two>/gamma", "test.src", "./alpha/beta/gamma/test.src"),
        ])
    def test_a_root_name_is_substituted_with_its_path(
            self, rooted_path, filename, path):
        self.given_a_filetree()

        self.when_computing_a_path(rooted_path, filename)

        # then the resolved path is returned.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == path

    def test_an_undefined_root_name_is_an_error(self):
        self.given_a_filetree()

        self.when_computing_a_path("<not_a_root>", raises=DoxhooksLookupError)

        assert self.error.key == "not_a_root"


class TestOverridingDirectoryPath(BaseTestFileTree):
    @mark.parametrize("absolute_path", ["/", "/test.src"])
    def test_an_absolute_path_for_filename_overrides_the_directory_path(
            self, absolute_path):
        self.given_a_filetree()

        self.when_computing_a_path("dir_path", absolute_path)

        # then the directory path is overridden.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == absolute_path

    @mark.parametrize("explicit_relative_path", [".", "./test.src"])
    def test_explicit_relative_path_for_filename_overrides_the_directory_path(
            self, explicit_relative_path):
        self.given_a_filetree()

        self.when_computing_a_path("dir_path", explicit_relative_path)

        # then the directory path is overridden.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == explicit_relative_path

    @mark.parametrize(
        "rooted_path, path", [
            ("<one>", "./alpha"),
            ("<uno>", "./alpha"),
            ("<one>test.src", "./alpha/test.src"),
            ("<uno>test.src", "./alpha/test.src"),
            ("<two>test.src", "./alpha/beta/test.src"),
        ])
    def test_a_filename_that_starts_with_a_root_name_overrides_the_dir_path(
            self, rooted_path, path):
        self.given_a_filetree()

        self.when_computing_a_path("dir_path", rooted_path)

        # then the directory path is overridden.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == path


class TestRewriteFilename(BaseTestFileTree):
    @withraises
    def when_computing_and_rewriting_a_path(self, dir_path):
        self.when_computing_a_path(dir_path, rewrite="-rewritten")

    def test_a_filetree_returns_a_rewritten_path(self):
        self.given_a_filetree()

        self.when_computing_and_rewriting_a_path("rewritable{}.src")

        # then the rewritten path is returned.
        slash_path = replace_sep_with_slash(self.path)
        assert slash_path == "./rewritable-rewritten.src"

    @mark.parametrize(
        "bad_rewritable_path", [
            "test{.src", "test}.src", "test{1}.src", "test{}{}.src",
        ])
    def test_rewriting_a_bad_path_is_an_error(self, bad_rewritable_path):
        self.given_a_filetree()

        self.when_computing_and_rewriting_a_path(
            bad_rewritable_path, raises=DoxhooksDataError)

        assert self.error
