import os

from doxhooks.errors import DoxhooksDataError
from doxhooks.server_configs import ServerConfiguration
from pytest import mark

from doxhooks_pytest import withraises


class FakeFileTree:
    def path(self, dir_path, *args, **kwargs):
        return dir_path


class BaseTestServerConfiguration:
    fake_filetree = FakeFileTree()

    def given_a_server_configuration(
            self, *, protocol=None, hostname=None, root=None, rewrite=None):
        self.server_config = ServerConfiguration(
            self.fake_filetree, protocol, hostname, root, rewrite
        )

    @withraises
    def when_computing_the_url_for_a_file(self, dir_path, filename=None):
        self.url = self.server_config.url_for_file(dir_path, filename)


class TestURL(BaseTestServerConfiguration):
    @mark.parametrize(
        "protocol, hostname, path, url", [
            (None, None, "one/test.dat", "/one/test.dat"),
            (None, "example.com", "one/test.dat", "example.com/one/test.dat"),
            ("//", "example.com", "one/test.dat",
                "//example.com/one/test.dat"),
            ("http://", "example.com", "one/test.dat",
                "http://example.com/one/test.dat"),
        ])
    def test_a_url_starts_with_optional_protocol_and_hostname(
            self, protocol, hostname, path, url):
        self.given_a_server_configuration(protocol=protocol, hostname=hostname)

        self.when_computing_the_url_for_a_file(path)

        # then the URL starts with the protocol and hostname.
        assert self.url == url

    @mark.parametrize(
        "server_root, path, url", [
            (None, "/one/test.dat", "/one/test.dat"),
            (None, "./one/test.dat", "/one/test.dat"),
            (None, "one/test.dat", "/one/test.dat"),
            (mark.skipif(os.sep != "\\", reason="Windows backslash separator")
                ((None, "one\\test.dat", "/one/test.dat"))),
            ("", "one/test.dat", "/one/test.dat"),
            (os.curdir, "one/test.dat", "/one/test.dat"),
            ("one", "one/test.dat", "/test.dat"),
            ("one/test.dat", "one/test.dat", "/"),
        ])
    def test_a_url_path_is_relative_to_a_path_on_the_server(
            self, server_root, path, url):
        self.given_a_server_configuration(root=server_root)

        self.when_computing_the_url_for_a_file(path)

        # then the URL path is the file path relative to the server
        # root.
        assert self.url == url

    @mark.parametrize(
        "server_root, path", [
            (None, "../test.dat"),
            ("one/two", "one/test.dat"),
            ("one", "test.dat"),
        ])
    def test_parent_path_notation_in_the_url_is_an_error(
            self, path, server_root):
        self.given_a_server_configuration(root=server_root)

        self.when_computing_the_url_for_a_file(path, raises=DoxhooksDataError)

        assert self.error
