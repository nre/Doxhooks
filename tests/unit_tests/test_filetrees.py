import os

from doxhooks.errors import DoxhooksDataError, DoxhooksLookupError
from doxhooks.filetrees import FileTree
from pytest import mark

from doxhooks_pytest import withraises


join = os.path.join
norm = os.path.normpath


class BaseTestFileTree:
    def given_a_filetree(self):
        self.filetree = FileTree({
            "one": "alpha",
            "two": "<one>beta",
        })

    @withraises
    def when_computing_a_path(self, branch, leaf=None, *, rewrite=None):
        self.path = self.filetree.path(branch, leaf, rewrite=rewrite)


class TestPath(BaseTestFileTree):
    @mark.parametrize(
        "branch, leaf, path", [
            ("test.src", None, "test.src"),
            ("<one>", None, "alpha"),
            ("<one>test.src", None, norm("alpha/test.src")),
            ("test_branch", "test.src", norm("test_branch/test.src")),
            ("<one>", "test.src", norm("alpha/test.src")),
            ("<one>", "two/test.src", norm("alpha/two/test.src")),
            ("<one>two", "test.src", norm("alpha/two/test.src")),
            ("<two>three", "test.src", norm("alpha/beta/three/test.src")),
            ("default", "<one>two/test.src", norm("alpha/two/test.src")),
            ("test_branch/", "test.src", norm("test_branch/test.src")),
            ("<one>/two", "test.src", norm("/two/test.src")),
        ])
    def test_a_filetree_substitutes_branch_names_with_branch_paths(
            self, branch, leaf, path):
        self.given_a_filetree()

        self.when_computing_a_path(branch, leaf)

        # then the path is returned.
        assert self.path == path

    @mark.parametrize(
        "branch, normalised_path", [
            (join(os.curdir, "test.src"), "test.src"),
            (join("wrong_way", os.pardir, "test.src"), "test.src"),
        ])
    def test_a_filetree_returns_a_normalised_path(
            self, branch, normalised_path):
        self.given_a_filetree()

        self.when_computing_a_path(branch)

        # then the normalised path is returned.
        assert self.path == normalised_path

    def test_an_undefined_branch_name_is_an_error(self):
        self.given_a_filetree()

        self.when_computing_a_path("<no_branch>", raises=DoxhooksLookupError)

        assert self.error.key == "no_branch"


class TestRewriteFilename(BaseTestFileTree):
    @withraises
    def when_computing_and_rewriting_a_path(self, branch):
        self.when_computing_a_path(branch, rewrite="-rewritten")

    def test_a_filetree_returns_a_rewritten_path(self):
        self.given_a_filetree()

        self.when_computing_and_rewriting_a_path("rewritable{}.src")

        # then the rewritten path is returned.
        assert self.path == "rewritable-rewritten.src"

    @mark.parametrize(
        "bad_rewritable_path", [
            "test{.src", "test}.src", "test{1}.src", "test{}{}.src",
        ])
    def test_rewriting_a_bad_path_is_an_error(self, bad_rewritable_path):
        self.given_a_filetree()

        self.when_computing_and_rewriting_a_path(
            bad_rewritable_path, raises=DoxhooksDataError)

        assert self.error
