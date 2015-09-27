"""
Containers for the type and configuration data of information resources.

Exports
-------
ResourceConfiguration
    The type and configuration data of an information resource.
"""


from doxhooks.functions import importattr


__all__ = [
    "ResourceConfiguration",
]


class ResourceConfiguration(dict):
    """
    The type and configuration data of an information resource.

    `ResourceConfiguration` extends `dict`.

    Class Interface
    ---------------
    make
        Return a new configured resource.

    Magic Methods
    -------------
    __repr__
        Override `dict.__repr__` to feature the resource type.
    """

    def __init__(self, resource_class, **kwargs):
        r"""
        Initialise the configuration with a resource type and data.

        The `ResourceConfiguration` constructor overrides the `dict`
        constructor to initialise `self.resource_class`.

        Parameters
        ----------
        resource_class : type or str
            The resource class, especially a subclass of
            `doxhooks.resources.Resource`. The argument is either the
            class itself, or an import name for the class, e.g.
            ``"module_name.ClassName"``.
        \**kwargs
            Keyword arguments that are passed to
            `doxhooks.resources.Resource.new`.
        """
        self._resource_class = resource_class
        self.update(kwargs)

    def __repr__(self):
        """
        Return a string featuring the resource type and data.

        Overrides `dict.__repr__`.

        Returns
        -------
        str
            A representation of the resource configuration.
        """
        return "<{} object resource_class=`{}` {}>".format(
            type(self).__name__, self._resource_class, super().__repr__())

    def make(self, **kwargs):
        r"""
        Return a new configured resource.

        Parameters
        ----------
        \**kwargs
            Additional keyword arguments that are passed to
            `doxhooks.resources.Resource.new`.

        Returns
        -------
        ~doxhooks.resources.Resource
            The new resource.

        Raises
        ------
        ~doxhooks.errors.DoxhookDataError
            If the resource configuration data is invalid.
        """
        class_ = self._resource_class
        if isinstance(class_, str):
            class_ = importattr(class_)

        new_kwargs = self.copy()
        new_kwargs.update(kwargs)
        return class_.new(**new_kwargs)
