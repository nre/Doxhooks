import unittest.mock as mock

from doxhooks.errors import DoxhooksDataFileError
from doxhooks.url_mappings import URLMapping
from pytest import fail

from doxhooks_pytest import withraises


class BaseTestURLMapping:
    resource_id = "test_resource_id"
    url = "test_url"
    different_url = "test_different_url"

    def given_a_url_mapping(self, *args, **kwargs):
        self.urls = URLMapping(*args, **kwargs)

    def given_a_url_mapping_containing_a_resource_url(self):
        self.given_a_url_mapping()
        self.urls[self.resource_id] = self.url


class TestWritableOnce(BaseTestURLMapping):
    @withraises
    def when_setting_the_resource_url(self, url):
        self.urls[self.resource_id] = url

    @withraises
    def when_deleting_the_resource_url(self):
        del self.urls[self.resource_id]

    def test_changing_a_resource_url_is_an_error(self):
        self.given_a_url_mapping_containing_a_resource_url()

        self.when_setting_the_resource_url(
            self.different_url, raises=RuntimeError)

        assert self.error

    def test_setting_a_resource_url_to_the_same_value_is_not_an_error(self):
        self.given_a_url_mapping_containing_a_resource_url()

        try:
            self.when_setting_the_resource_url(self.url)
        except RuntimeError:
            fail(
                "Setting a resource URL to the same value "
                "should not raise an error.")

    def test_deleting_a_resource_url_is_an_error(self):
        self.given_a_url_mapping_containing_a_resource_url()

        self.when_deleting_the_resource_url(raises=RuntimeError)

        assert self.error


class TestLoading(BaseTestURLMapping):
    @withraises
    def when_loading_url_data(self, value):
        dummy_path = None
        with mock.patch(
                "doxhooks.dataio.load_literals", autospec=True,
                return_value=value):
            self.urls.load(dummy_path)

    def test_loaded_url_data_replaces_the_previous_url_data(self):
        previous_urls = {
            "id_1": "url_1",
            "id_2": "url_2",
        }
        loaded_urls = {
            "id_2": "url_2+",
            "id_3": "url_3",
        }
        self.given_a_url_mapping(previous_urls)

        self.when_loading_url_data(loaded_urls)

        urls = dict(self.urls)
        assert urls == loaded_urls

    def test_loading_url_data_that_is_not_a_dictionary_is_an_error(self):
        not_dict = None

        self.given_a_url_mapping()

        self.when_loading_url_data(not_dict, raises=DoxhooksDataFileError)

        assert self.error
