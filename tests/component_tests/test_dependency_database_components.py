import doxhooks.fileio as fileio
from doxhooks.dependency_databases import DependencyDatabase
from doxhooks.errors import DoxhooksDataError, DoxhooksDataFileError
from pytest import fail, fixture, mark


class BaseTestDatabase:
    @fixture
    def _setup_path(self, tmpdir):
        fileio.add_output_roots(tmpdir.strpath)
        self.path = tmpdir.join("test_database.dat").strpath

    def given_a_database_of_products_and_their_features(self):
        self.db = DependencyDatabase()

    def _update(self, product, features):
        self.db.update_dependencies(product, features)

    def and_the_records_on_that_product_and_its_features_are_updated(
            self, product, features):
        self._update(product, features)

    def when_saving_and_loading_the_database_then_an_error_is_not_raised(self):
        try:
            self.db.save(self.path)
        except DoxhooksDataError:
            fail("Saving the database should not raise an error.")
        try:
            self.db.load(self.path)
        except (DoxhooksDataFileError, SyntaxError, ValueError):
            fail("Reloading the database should not raise an error.")


@mark.usefixtures("_setup_path")
class TestDatabaseDoesNotSaveEmptySet(BaseTestDatabase):
    # ast.literal_eval raises an error when evaluating "set()".
    no_features = set()

    def test_database_does_not_save_an_empty_set_of_features(self):
        self.given_a_database_of_products_and_their_features()
        # and a product that has no features
        self.and_the_records_on_that_product_and_its_features_are_updated(
            "lonely_product", self.no_features)

        self.when_saving_and_loading_the_database_then_an_error_is_not_raised()

    def test_database_does_not_save_an_empty_set_of_removed_features(self):
        self.given_a_database_of_products_and_their_features()
        self._update("product", {"feature"})
        self._update("another_product", {"feature"})
        # and a product that has lost all of its features
        self.and_the_records_on_that_product_and_its_features_are_updated(
            "product", self.no_features)

        self.when_saving_and_loading_the_database_then_an_error_is_not_raised()

    def test_database_does_not_save_an_empty_set_of_removed_products(self):
        self.given_a_database_of_products_and_their_features()
        self._update("product", {"feature", "another_feature"})
        # and a feature that is no longer depended on by any products
        self.and_the_records_on_that_product_and_its_features_are_updated(
            "product", {"another_feature"})

        self.when_saving_and_loading_the_database_then_an_error_is_not_raised()
