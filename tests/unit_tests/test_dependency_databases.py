import unittest.mock as mock

from doxhooks.dependency_databases import DependencyDatabase
from doxhooks.errors import DoxhooksDataFileError
from pytest import fail, fixture, mark

from doxhooks_pytest import withraises


class BaseTestDatabase:
    @fixture(autouse=True)
    def _setup_mutable_test_data(self):
        self._products_features = {
            "product1": {"feature1", "feature2", "feature3"},
            "product2": {"feature1", "feature2"},
            "product3": {"feature1"},
        }
        self._features_products = {
            "feature1": {"product1", "product2", "product3"},
            "feature2": {"product1", "product2"},
            "feature3": {"product1"},
        }

    def _update(self, product, features):
        self.db.update_dependencies(product, features)

    def given_a_database_of_products_and_their_features(self):
        self.db = DependencyDatabase()
        for product, features in self._products_features.items():
            self._update(product, features)

    @withraises
    def when_updating_the_records_on_a_product_and_its_features(
            self, product, features):
        self._update(product, features)

    and_the_records_on_that_product_and_its_features_are_updated = \
        when_updating_the_records_on_a_product_and_its_features

    def when_updating_the_records_then_an_error_is_not_raised(
            self, product, features):
        try:
            self._update(product, features)
        except (KeyError, RuntimeError):
            fail("Updating the database should not raise an error.")

    def _retrieve_products(self, feature):
        return self.db.retrieve_products(feature)

    def when_retrieving_the_products_that_depend_on_a_given_feature(
            self, feature):
        self.products = self._retrieve_products(feature)


class TestRetrieval(BaseTestDatabase):
    @mark.parametrize(
        "feature", ["feature1", "feature2", "feature3"],
    )
    def test_a_database_returns_the_products_that_depend_on_a_given_feature(
            self, feature):
        self.given_a_database_of_products_and_their_features()

        self.when_retrieving_the_products_that_depend_on_a_given_feature(
            feature)

        # then the set of products that depend on that feature is
        # returned.
        assert self.products == self._features_products[feature]

    def test_a_database_returns_an_empty_set_of_products_for_a_lonely_feature(
            self):
        self.given_a_database_of_products_and_their_features()

        self.when_retrieving_the_products_that_depend_on_a_given_feature(
            "lonely_feature")

        # then an empty set is returned.
        assert self.products == set()

    def test_data_returned_by_a_database_is_only_a_copy_of_its_data(self):
        self.given_a_database_of_products_and_their_features()

        # when retrieving the products that depend on a given feature
        feature = "feature1"
        products_copy1 = self._retrieve_products(feature)
        products_copy2 = self._retrieve_products(feature)

        # then the set of products that is returned is a copy.
        assert products_copy1  # Not an empty set.
        assert products_copy1 is not products_copy2


class TestUpdating(BaseTestDatabase):
    def test_the_data_stored_by_a_database_is_only_a_copy_of_the_data(self):
        self.given_a_database_of_products_and_their_features()
        product = "product"
        updated_features = {"feature"}
        updated_features_copy1 = updated_features.copy()
        updated_features_copy2 = updated_features.copy()
        updated_features_copy3 = updated_features.copy()
        self.and_the_records_on_that_product_and_its_features_are_updated(
            product, updated_features_copy1)

        updated_features_copy1.add("another_feature")
        # If db has stored copy1 in its database, db will raise an
        # error when it tries to remove "another_feature":
        self.when_updating_the_records_then_an_error_is_not_raised(
            product, updated_features_copy2)

        updated_features_copy2.add("yet_another_feature")
        # If db has stored copy2 in its database, db will raise an
        # error when it tries to remove "yet_another_feature":
        self.when_updating_the_records_then_an_error_is_not_raised(
            product, updated_features_copy3)


class TestProductGainedAFeature(BaseTestDatabase):
    def _add_feature(self, product, added_feature):
        products = self._retrieve_products(added_feature)
        assert product not in products
        features = self._products_features[product].copy()
        assert added_feature not in features
        features.add(added_feature)
        return features

    def test_a_database_returns_product_given_a_feature_added_to_that_product(
            self):
        self.given_a_database_of_products_and_their_features()
        # and a product that now depends on an additional feature
        product = "product3"
        added_feature = "feature2"
        updated_features = self._add_feature(product, added_feature)
        self.and_the_records_on_that_product_and_its_features_are_updated(
            product, updated_features)

        self.when_retrieving_the_products_that_depend_on_a_given_feature(
            added_feature)

        # then the product is in that set of products.
        assert product in self.products


class TestProductLostAFeature(BaseTestDatabase):
    def _remove_feature(self, product, removed_feature):
        products = self._retrieve_products(removed_feature)
        assert product in products
        features = self._products_features[product].copy()
        features.remove(removed_feature)
        return features

    def given_records_on_product_and_its_lost_feature_are_updated(self):
        self.given_a_database_of_products_and_their_features()
        # and a product that no longer depends on a removed feature
        self.product = "product2"
        self.removed_feature = "feature2"
        self.updated_features = self._remove_feature(
            self.product, self.removed_feature)
        self.and_the_records_on_that_product_and_its_features_are_updated(
            self.product, self.updated_features)

    def test_does_not_return_a_product_given_feature_removed_from_that_product(
            self):
        self.given_records_on_product_and_its_lost_feature_are_updated()

        self.when_retrieving_the_products_that_depend_on_a_given_feature(
            self.removed_feature)

        # then the product is not in that set of products.
        assert self.product not in self.products

    def test_a_database_is_consistent_in_updating_a_lost_feature(self):
        self.given_records_on_product_and_its_lost_feature_are_updated()

        self.when_updating_the_records_then_an_error_is_not_raised(
            self.product, self.updated_features)


class TestProductLostAllItsFeatures(BaseTestDatabase):
    def _remove_all_features(self, product):
        features = self._products_features[product]
        assert features
        self.removed_features = features
        return set()

    def given_records_on_product_that_lost_all_its_features_are_updated(self):
        self.given_a_database_of_products_and_their_features()
        # and a product that no longer depends on any features
        self.product = "product2"
        self.no_features = self._remove_all_features(self.product)
        self.and_the_records_on_that_product_and_its_features_are_updated(
            self.product, self.no_features)

    def test_does_not_return_lonely_product_given_any_feature_removed_from_it(
            self):
        self.given_records_on_product_that_lost_all_its_features_are_updated()

        # when retrieving the products that depend on each removed feature
        for removed_feature in self.removed_features:
            products = self._retrieve_products(removed_feature)

            # then the product is not in that set of products.
            assert self.product not in products

    def test_a_database_is_consistent_in_updating_a_product_with_no_features(
            self):
        self.given_records_on_product_that_lost_all_its_features_are_updated()

        self.when_updating_the_records_then_an_error_is_not_raised(
            self.product, self.no_features)


class BaseTestLoading(BaseTestDatabase):
    @fixture
    def _setup_load_data(self):
        self._load_products_features = {
            "loaded_product1": {"feature1"},
            "loaded_product2": {"feature1"},
        }
        self._load_features_products = {
            "feature1": {"loaded_product1", "loaded_product2"},
        }
        self._load_data = {
            "products_features": self._load_products_features,
            "features_products": self._load_features_products,
        }
        self.feature_in_loaded_database = "feature1"

    @fixture
    def _setup_inconsistent_data(self):
        self._inconsistent_data_missing_feature_key = {
            "products_features": {
                "product": {"feature"},
            },
            "features_products": {},
        }
        self._inconsistent_data_missing_product_value = {
            "products_features": {
                "product": {"feature"},
            },
            "features_products": {
                "feature": set(),
            },
        }
        self.product_in_inconsistent_database = "product"

    @fixture(
        params=[
            "_inconsistent_data_missing_feature_key",
            "_inconsistent_data_missing_product_value",
        ])
    def inconsistent_data(self, request):
        return getattr(self, request.param)

    @withraises
    def when_loading_a_database(self, data):
        dummy_path = None
        with mock.patch(
                "doxhooks.dataio.load_literals", autospec=True,
                return_value=data):
            self.db.load(dummy_path)

    and_a_database_is_loaded = when_loading_a_database


class TestLoading(BaseTestLoading):
    @mark.usefixtures("_setup_load_data")
    def test_a_loaded_database_replaces_the_current_database(self):
        self.given_a_database_of_products_and_their_features()
        self.and_a_database_is_loaded(self._load_data)

        feature = self.feature_in_loaded_database
        self.when_retrieving_the_products_that_depend_on_a_given_feature(
            feature)

        # then the set of products that depend on that feature is
        # returned.
        assert self.products == self._load_features_products[feature]

    @mark.usefixtures("_setup_inconsistent_data")
    def test_updating_an_inconsistent_database_is_an_error(
            self, inconsistent_data):
        self.given_a_database_of_products_and_their_features()
        # and a product that no longer depends on a removed feature
        product = self.product_in_inconsistent_database
        features = set()
        self.and_a_database_is_loaded(inconsistent_data)

        self.when_updating_the_records_on_a_product_and_its_features(
            product, features, raises=RuntimeError)

        assert self.error

    @mark.parametrize(
        "bad_data", [
            None, 1, "", (), [], {}, {0: 1}, set(),
            {
                "features_products": None,
                "products_features": {},
            },
            {
                "features_products": {0: 1},
                "products_features": {},
            },
        ])
    def test_loading_a_bad_database_is_an_error(self, bad_data):
        self.given_a_database_of_products_and_their_features()

        self.when_loading_a_database(bad_data, raises=DoxhooksDataFileError)

        assert self.error
