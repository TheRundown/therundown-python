class Resource:
    """Base class for resources.

    Attributes:
        _data: The JSON data the resource is created from
    """

    def set_attributes(self, **kwargs):
        """Set attributes on the implementing class using kwargs."""
        pass

    def json(self):
        return self._data
