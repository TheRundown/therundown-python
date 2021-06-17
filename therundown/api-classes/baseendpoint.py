from config import Config


class BaseEndpoint:
    """Class has all REST API endpoints available as separate classes.

    Advantages:
        - separation of concerns
        - single-use class, store JSON response

    Attributes:
        config: Store user configuration preferences using Config class.
        _raw: The JSON response.
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
