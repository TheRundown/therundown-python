from config import Config


class BaseEndpoint:
    """Class has all REST API endpoints grouped by category.

    Advantages:
        - config class doesn't need to be added as argument to each endpoint.
        - separation of concerns

    Attributes:
        config: Store user configuration preferences using Config class.
        _raw: The most recent JSON response.
    """

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self._raw = None

    def _get(self, url):
        """Make get request to the API.

        Returns:
            The JSON response from the API.
        """
        if not self.config:
            # use new request
            pass
        else:
            # use self.config.session
            pass
