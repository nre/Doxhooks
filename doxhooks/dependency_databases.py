"""
Databases of *products* and their dependencies on *features*.

After a database is updated with the *features* that each *product*
depends on (`DependencyDatabase.update_dependencies`), then all the
products that depend on a given feature can be retrieved
(`DependencyDatabase.retrieve_products`). These are the products that
are affected by a change in that feature.

A database can be loaded and saved (`DependencyDatabase.load`,
`DependencyDatabase.save`).

Exports
-------
DependencyDatabase
    A database of products and their dependencies on features.

See Also
--------
doxhooks.resource_environments.ResourceEnvironment.update_dependents
    Update all resources that depend on a given input file.


.. testsetup::

    import doxhooks.dependency_databases
"""


import doxhooks.console as console
import doxhooks.dataio as dataio
from doxhooks.errors import DoxhooksDataFileError


__all__ = [
    "DependencyDatabase",
]


class DependencyDatabase:
    """
    A database of *products* and their dependencies on *features*.

    Class Interface
    ---------------
    update_dependencies
        Update the database with a product and its features.
    retrieve_products
        Return the products that depend on a given feature.
    load
        Replace the database with a database that is read from a file.
    save
        Write the database to a file.

    Example
    -------
    >>> database = doxhooks.dependency_databases.DependencyDatabase()
    >>> database.update_dependencies("product1", ["feature1", "feature2"])
    >>> database.update_dependencies("product2", ["feature1", "feature3"])
    >>> database.retrieve_products("feature1")  # doctest: +SKIP
    {'product1', 'product2'}
    >>> database.retrieve_products("feature2")
    {'product1'}
    >>> database.retrieve_products("feature3")
    {'product2'}
    >>> database.retrieve_products("feature4")
    set()
    """

    def __init__(self):
        """Initialise an empty database."""
        self._features_products = {}
        self._products_features = {}

    def retrieve_products(self, feature):
        """
        Return the products that depend on a given feature.

        Parameters
        ----------
        feature : ~collections.abc.Hashable
            The feature.

        Returns
        -------
        set
            The products that depend on the feature.
        """
        try:
            products = self._features_products[feature]
        except KeyError:
            return set()
        return products.copy()

    def _add_product(self, product, features):
        # Add a product to each feature's set of products.
        for feature in features:
            try:
                self._features_products[feature].add(product)
            except KeyError:
                self._features_products[feature] = {product}

    def _remove_product(self, product, features):
        # Remove a product from each feature's set of products.
        for feature in features:
            try:
                products = self._features_products[feature]
                products.remove(product)
            except KeyError as error:
                raise RuntimeError("Database is inconsistent.") from error
            if not products:
                del self._features_products[feature]

    def update_dependencies(self, product, features):
        """
        Update the database with a product and its features.

        Parameters
        ----------
        product : ~collections.abc.Hashable
            The product.
        features : Iterable[Hashable]
            The features of the product.
        """
        products_features = self._products_features

        try:
            previous_features = products_features[product]
        except KeyError:
            if features:
                products_features[product] = set(features)
                self._add_product(product, features)
            return

        if features:
            products_features[product] = set(features)
        else:
            del products_features[product]

        added_features = features.difference(previous_features)
        removed_features = previous_features.difference(features)

        if added_features:
            console.log("Added dependencies:", ", ".join(added_features))
            self._add_product(product, added_features)

        if removed_features:
            console.log("Removed dependencies:", ", ".join(removed_features))
            self._remove_product(product, removed_features)

    def load(self, path):
        """
        Replace the database with a database that is read from a file.

        Parameters
        ----------
        path : str
            The path to the file.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be read.
        ~doxhooks.errors.DoxhooksDataFileError
            If the file does not contain a valid database.
        """
        data = dataio.load_literals(path)
        try:
            features_products = data["features_products"]
            products_features = data["products_features"]
        except (KeyError, TypeError):
            raise DoxhooksDataFileError(
                "Not a dependency-database file:", path)

        for dict_ in features_products, products_features:
            try:
                are_sets = [isinstance(value, set) for value in dict_.values()]
            except (AttributeError, TypeError):
                raise DoxhooksDataFileError(
                    "Bad dependency-database file:", path)
            if not all(are_sets):
                raise DoxhooksDataFileError(
                    "Bad dependency-database file:", path)

        self._features_products = features_products
        self._products_features = products_features

    def save(self, path):
        """
        Write the database to a file.

        The database can be saved if the types of *product* and
        *feature* values in the database are Python-literal types. The
        recommended types are `str`, `int` and `tuple`. (The other types
        that can be saved are `bytes`, `bool`, `float`, `complex` and
        ``None``. The Python literal types `list`, `dict` and `set` are
        not `~collections.abc.Hashable` and cannot be stored in the
        database.)

        Parameters
        ----------
        path : str
            The path to the file.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the types of values in the database are not
            Python-literal types.
        ~doxhooks.errors.DoxhooksFileError
            If the file cannot be saved.
        """
        data = {
            "features_products": self._features_products,
            "products_features": self._products_features,
        }
        dataio.save_literals(path, data)
