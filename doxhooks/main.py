"""
User-friendly encapsulations of the Doxhooks components.

Resources can be updated individually (`Doxhooks.update`), all together
(`Doxhooks.update_all`) or only if they depend on a given input file
(`Doxhooks.update_dependents`).

The resource environment data can be loaded and saved (`Doxhooks.load`,
`Doxhooks.save`).

Exports
-------
add_output_roots
    Declare the paths to directories where overwriting files is ok.
Doxhooks
    A user-friendly encapsulation of the Doxhooks components.
"""


import os

import doxhooks.fileio as fileio
from doxhooks.dependency_databases import DependencyDatabase
from doxhooks.resource_environments import ResourceEnvironment
from doxhooks.url_mappings import URLMapping


__all__ = [
    "Doxhooks",
    "add_output_roots",
]


add_output_roots = fileio.add_output_roots
r"""
Declare the paths to directories where overwriting files is ok.

The paths are either absolute or relative to the current working
directory.

`doxhooks.main.add_output_roots` is a convenient alias for
`doxhooks.fileio.add_output_roots`.

Parameters
----------
root_path : str
    The path to a output root directory.
\*root_paths : str
    The paths to more output root directories.
"""


class Doxhooks:
    """
    A user-friendly encapsulation of the Doxhooks components.

    The `Doxhooks` class encapsulates the Doxhooks components and their
    dependency injection. All methods return `self` to allow method
    chaining.

    Class Interface
    ---------------
    update
        Update a configured resource.
    update_all
        Update all configured resources.
    update_dependents
        Update all resources that depend on a given input file.
    load
        Replace the environment data with data read from files.
    save
        Save the environment data in data files.
    """

    def __init__(
            self, resource_configs, *, reverse_order=False,
            input_roots=None, output_roots=None, url_roots=None,
            urls=None, data_dir_path=os.curdir):
        """
        Initialise Doxhooks with user data and internal components.

        Parameters
        ----------
        resource_configs : Subscriptable[ResourceConfiguration]
            A subscriptable container of resource configurations. The
            subscripts are the resource identities.
        reverse_order : bool, optional
            Keyword-only. Whether the order of iterating over
            `resource_configs` should be reversed. Defaults to
            ``False``.
        input_roots : dict or None, optional
            Keyword-only. Named root paths in the input-file tree.
            Defaults to ``None``.
        output_roots : dict or None, optional
            Keyword-only. Named root paths in the output-file tree.
            Defaults to ``None``.
        url_roots : dict or None, optional
            Keyword-only. Named root paths in the resource URLs.
            Defaults to ``None``.
        urls : dict or None, optional
            Keyword-only. A dictionary of resource identities and
            predefined URLs. Defaults to ``None``.
        data_dir_path : str, optional
            Keyword-only. The path to a directory where the data files
            are loaded and saved. Defaults to the current directory.
        """
        url_mapping = URLMapping()
        if urls:
            url_mapping.update(urls)

        self._environment = ResourceEnvironment(
            resource_configs,
            {
                "urls": url_mapping,
                "input_roots": input_roots or {},
                "output_roots": output_roots or {},
                "url_roots": url_roots or {},
            },
            DependencyDatabase(),
            reverse_order=reverse_order,
        )
        self._data_dir_path = data_dir_path

    def update(self, resource_id):
        """
        Update a configured resource.

        Parameters
        ----------
        resource_id : ~collections.abc.Hashable
            The identity of the resource to be updated.

        Returns
        -------
        Doxhooks
            This instance of `Doxhooks`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        self._environment.update(resource_id)
        return self

    def update_all(self):
        """
        Update all configured resources.

        The order that the resources are updated in is either the
        iteration order of the *resource configurations* or the *reverse
        order*.

        Returns
        -------
        Doxhooks
            This instance of `Doxhooks`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        self._environment.update_all()
        return self

    def update_dependents(self, input_path, *, input_root=None):
        """
        Update all resources that depend on a given input file.

        The order that the resources are updated in is either the
        iteration order of the *resource configurations* or the *reverse
        order*.

        Parameters
        ----------
        input_path : str
            The path to the input file.
        input_root : str or None, optional
            Keyword-only. A path that the input path should be made
            relative to, in order to match the input paths stored in the
            *dependency database*. Defaults to ``None``.

        Returns
        -------
        Doxhooks
            This instance of `Doxhooks`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        self._environment.update_dependents(
            input_path, input_root=input_root)
        return self

    def load(self):
        """
        Replace the environment data with data read from files.

        Returns
        -------
        Doxhooks
            This instance of `Doxhooks`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If a data file cannot be read.
        ~doxhooks.errors.DoxhooksDataFileError
            If a data file does not contain valid data.
        """
        self._environment.load(self._data_dir_path)
        return self

    def save(self):
        """
        Save the environment data in data files.

        Returns
        -------
        Doxhooks
            This instance of `Doxhooks`.

        Raises
        ------
        ~doxhooks.errors.DoxhooksFileError
            If a data file cannot be saved.
        """
        self._environment.save(self._data_dir_path)
        return self
