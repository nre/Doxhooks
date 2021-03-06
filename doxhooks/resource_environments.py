"""
Environments in which the information resources are updated.

The resources in the environment can be updated individually
(`ResourceEnvironment.update`), all together
(`ResourceEnvironment.update_all`) or only if they depend on a given
input file (`ResourceEnvironment.update_dependents`).

Exports
-------
ResourceEnvironment
    An environment in which information resources are updated.
"""


import os

import doxhooks.console as console
from doxhooks.errors import DoxhooksLookupError
from doxhooks.filetrees import normalise_path


__all__ = [
    "ResourceEnvironment",
]


class ResourceEnvironment:
    """
    An environment in which information resources are updated.

    Class Interface
    ---------------
    update
        Update a resource configured in this environment.
    update_all
        Update all resources configured in this environment.
    update_dependents
        Update all resources that depend on a given input file.
    """

    def __init__(
            self, resource_configs, common_configs, dependency_database,
            *, reverse_order=False):
        """
        Initialise the environment with data about the resources.

        Parameters
        ----------
        resource_configs : Subscriptable[ResourceConfiguration]
            A subscriptable container of resource configurations. The
            subscripts are the resource identities.
        common_configs : dict
            Configuration data that is common to all the resources in
            the environment.
        dependency_database : ~doxhooks.dependency_databases.DependencyDatabase
            A database of resource identities and the paths to the input
            files that those resources depend on.
        reverse_order : bool, optional
            Keyword-only. Whether the order of iterating over
            `resource_configs` should be reversed. Defaults to
            ``False``.
        """
        self._resource_configs = resource_configs
        self._common_configs = common_configs
        self._database = dependency_database
        self._reverse_order = reverse_order

    def update(self, resource_id):
        """
        Update a resource configured in this environment.

        Parameters
        ----------
        resource_id : ~collections.abc.Hashable
            The identity of the resource to be updated.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If `resource_id` is not a subscript in the *resource
            configurations* of this `ResourceEnvironment`.
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        try:
            config = self._resource_configs[resource_id]
        except LookupError:
            raise DoxhooksLookupError(
                resource_id, self._resource_configs, "`resource_configs`")

        resource = config.make(id=resource_id, **self._common_configs)
        resource.update()

    @property
    def _resource_ids(self):
        # Return a sequence of the IDs in the resource configurations.
        try:
            resource_ids = tuple(self._resource_configs.keys())
        except (AttributeError, TypeError):
            resource_ids = range(len(self._resource_configs))
        return reversed(resource_ids) if self._reverse_order else resource_ids

    def update_all(self):
        """
        Update all resources configured in this environment.

        The order that the resources are updated in is either the
        iteration order of the *resource configurations* or the *reverse
        order*.

        Raises
        ------
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        for resource_id in self._resource_ids:
            self.update(resource_id)

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
            *dependency database* of this `ResourceEnvironment`.
            Defaults to ``None``.

        Raises
        ------
        ~doxhooks.errors.DoxhooksLookupError
            If a resource identity retrieved from the *dependency
            database* of this `ResourceEnvironment` is not a subscript
            in the *resource configurations* of this
            `ResourceEnvironment`.
        ~doxhooks.errors.DoxhooksDataError
            If the resource or environment data are invalid.
        ~doxhooks.errors.DoxhooksFileError
            If an input file cannot be read, or an output file cannot be
            written.
        """
        if input_root is None:
            path = input_path
        else:
            path = os.path.relpath(input_path, input_root)
        path = normalise_path(path)

        dependent_ids = self._database.retrieve_products(path)
        if not dependent_ids:
            console.info("No dependency data for {!r}.".format(path))
            return

        update_ids = []
        for id_ in self._resource_ids:
            if id_ in dependent_ids:
                update_ids.append(id_)
                dependent_ids.remove(id_)
        if dependent_ids:
            raise DoxhooksLookupError(
                ", ".join(dependent_ids), self._resource_configs,
                "`resource_configs`")

        resource_count = len(update_ids)
        plural = "" if resource_count == 1 else "s"
        console.info(
            "Found {} resource{} dependent on {!r}."
            .format(resource_count, plural, path))

        for resource_id in update_ids:
            self.update(resource_id)
