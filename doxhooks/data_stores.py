"""
Collections of data objects.

The data objects can be loaded and saved individually (`DataStore.load`,
`DataStore.save`) or all together (`DataStore.load_all`,
`DataStore.save_all`).

Exports
-------
DataStore
    A collection of data objects that are loaded and saved together.
"""


import os


__all__ = [
    "DataStore",
]


class DataStore(dict):
    """
    A collection of data objects that are loaded and saved together.

    `DataStore` extends `dict`.

    Class Interface
    ---------------
    load
        Tell a data object to load its data.
    save
        Tell a data object to save its data.
    load_all
        Tell each data object in the collection to load its data.
    save_all
        Tell each data object in the collection to save its data.

    Magic Methods
    -------------
    __repr__
        Override `dict.__repr__` to return a non-literal representation.
    """

    def __init__(self, dir_path=os.curdir, **kwargs):
        r"""
        Initialise the data store.

        The `DataStore` constructor overrides the `dict` constructor.

        Parameters
        ----------
        dir_path : str, optional
            The path to a directory where the data objects will load and
            save their data. Defaults to the current directory.
        \**kwargs
            The initial keys and data objects in the store.

        Attributes
        ----------
        dir_path : str
            The argument of `dir_path`.
        """
        self.dir_path = dir_path
        self.update(kwargs)

    def __repr__(self):
        """
        Return a representation of the data store.

        Overrides `dict.__repr__`.

        Returns
        -------
        str
            The representation.
        """
        return "<{} object dir_path={!r} {!r}>".format(
            type(self).__name__, self.dir_path, set(self.keys()))

    def _path(self, key):
        return os.path.join(self.dir_path, str(key) + ".dat")

    def load(self, key):
        """
        Tell a data object to load its data.

        Parameters
        ----------
        key : ~collections.abc.Hashable
            The key for the data object.

        Raises
        ------
        KeyError
            If the key is not found in the data store.
        ~doxhooks.errors.DoxhooksFileError
            If the data file cannot be loaded.
        """
        data_object = self[key]
        path = self._path(key)
        data_object.load(path)

    def save(self, key):
        """
        Tell a data object to save its data.

        Parameters
        ----------
        key : ~collections.abc.Hashable
            The key for the data object.

        Raises
        ------
        KeyError
            If the key is not found in the data store.
        ~doxhooks.errors.DoxhooksDataError
            If the data cannot be saved.
        ~doxhooks.errors.DoxhooksFileError
            If the data file cannot be saved.
        """
        data_object = self[key]
        path = self._path(key)
        data_object.save(path)

    def load_all(self):
        """
        Tell each data object in the collection to load its data.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If a data file cannot be loaded.
        ~doxhooks.errors.DoxhooksDataFileError
            If a data file contains invalid data.
        """
        for key in self.keys():
            self.load(key)

    def save_all(self):
        """
        Tell each data object in the collection to save its data.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If some data cannot be saved.
        ~doxhooks.errors.DoxhooksFileError
            If a data file cannot be saved.
        """
        for key in self.keys():
            self.save(key)
