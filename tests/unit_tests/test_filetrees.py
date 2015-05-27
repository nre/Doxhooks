import os

from doxhooks.errors import DoxhooksLookupError, DoxhooksValueError
from doxhooks.filetrees import FileTree, OutputFileTree
from pytest import fixture, mark

from doxhooks_pytest import withraises


test_path_args = "branch, filename, path", [
    ("", "test.src", "test.src"),
    ("test_branch", "test.src",
        os.path.normpath("test_branch/test.src")),
    ("<one>", "test.src",
        os.path.normpath("alpha/test.src")),
    ("<one>", "two/test.src",
        os.path.normpath("alpha/two/test.src")),
    ("<one>two", "test.src",
        os.path.normpath("alpha/two/test.src")),
    ("<two>three", "test.src",
        os.path.normpath("alpha/beta/three/test.src")),
    ("default", "<one>two/test.src",
        os.path.normpath("alpha/two/test.src")),
    ("<one>", "/test.src", os.path.normpath("/test.src")),
    ("<one>/two", "test.src", os.path.normpath("/two/test.src")),
]


class BaseTestFileTree:
    default_branch = "test_branch"
    default_filename = "test.src"
    default_path = os.path.normpath("test_branch/test.src")

    branches = {
        "one": "alpha",
        "two": "<one>beta",
    }

    def given_a_filetree(self, *, branch=None, filename=None):
        self.filetree = FileTree(
            self.default_branch if branch is None else branch,
            self.default_filename if filename is None else filename,
            self.branches,
        )

    def given_an_output_filetree(self, *, branch=None, filename=None):
        self.filetree = OutputFileTree(
            self.default_branch if branch is None else branch,
            self.default_filename if filename is None else filename,
            output_branches=None,
            url_branches=self.branches,
        )

    def when_getting_the_path_for_a_filename(self, filename, *, rewrite=None):
        self.path = self.filetree.path(filename, rewrite=rewrite)

    @withraises
    def when_getting_the_path_to_the_default_file(self, *, rewrite=None):
        self.when_getting_the_path_for_a_filename(None, rewrite=rewrite)

    def when_getting_the_url_path_to_the_output_file(self, *, rewrite=None):
        self.path = self.filetree.url_path(rewrite=rewrite)


class TestPath(BaseTestFileTree):
    @fixture(params=[(os.curdir,), ("wrong_way", os.pardir)])
    def dot_notation_nodes(self, request):
        return request.param

    @mark.parametrize(*test_path_args)
    def test_a_filetree_returns_the_path_to_its_default_file(
            self, branch, filename, path):
        self.given_a_filetree(branch=branch, filename=filename)

        self.when_getting_the_path_to_the_default_file()

        # then the path to the default file is returned.
        assert self.path == path

    @mark.parametrize(*test_path_args)
    def test_a_filetree_returns_the_path_for_a_filename(
            self, branch, filename, path):
        self.given_a_filetree(branch=branch, filename="dummy")

        self.when_getting_the_path_for_a_filename(filename)

        # then the path for the filename is returned.
        assert self.path == path

    def test_a_filetree_returns_normalised_paths(self, dot_notation_nodes):
        dotted_branch = os.path.join(self.default_branch, *dot_notation_nodes)
        self.given_a_filetree(branch=dotted_branch)

        self.when_getting_the_path_to_the_default_file()

        # then a normalised path to the default file is returned.
        assert self.path == self.default_path

    def test_an_undefined_branch_name_is_an_error(self):
        self.given_a_filetree(filename="<not_a_branch>test.src")

        self.when_getting_the_path_to_the_default_file(
            raises=DoxhooksLookupError)

        assert self.error.key == "not_a_branch"


class TestRewriteFilename(BaseTestFileTree):
    rewritable_filename = "rewritable{}.src"
    rewrite = "-rewritten"
    rewritten_path = os.path.normpath("test_branch/rewritable-rewritten.src")

    bad_rewritable_filename = "test_index_error{1}.src"

    def test_a_filetree_returns_the_path_for_a_rewritten_default_filename(
            self):
        self.given_a_filetree(filename=self.rewritable_filename)

        self.when_getting_the_path_to_the_default_file(rewrite=self.rewrite)

        # then the path to the rewritten default filename is returned.
        assert self.path == self.rewritten_path

    def test_a_filetree_returns_the_path_for_a_rewritten_filename(self):
        self.given_a_filetree(filename="dummy")

        self.when_getting_the_path_for_a_filename(
            self.rewritable_filename, rewrite=self.rewrite)

        # then the path to the rewritten default filename is returned.
        assert self.path == self.rewritten_path

    def test_rewriting_a_bad_filename_is_an_error(self):
        self.given_a_filetree(filename=self.bad_rewritable_filename)

        self.when_getting_the_path_to_the_default_file(
            rewrite=self.rewrite, raises=DoxhooksValueError)

        assert self.error.value == self.bad_rewritable_filename


class TestURLPath(BaseTestFileTree):
    @mark.parametrize(*test_path_args)
    def test_a_filetree_returns_the_url_path_to_its_default_file(
            self, branch, filename, path):
        self.given_an_output_filetree(branch=branch, filename=filename)

        self.when_getting_the_url_path_to_the_output_file()

        # then the URL path to the output file is returned.
        assert self.path == path
