from typing import Union
from enum import Enum

import requests


class _RapidAPIAuth:
    """Authorization configuration required for making requests to RapidAPI."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "therundown-therundown-v1.p.rapidapi.com"
        self.api_url = "https://therundown-therundown-v1.p.rapidapi.com/"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }


class _RundownAuth:
    """Authorization configuration required for making requests to The Rundown's API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://therundown.io/api/v1"
        self.headers = {"X-TheRundown-Key": self.api_key}


class _Auth:
    """Class supporting creation of RapidAPIAuth and RundownAuth objects."""

    @classmethod
    def factory(cls, provider: str, api_key: str) -> Union[_RapidAPIAuth, _RundownAuth]:
        """Factory method returning RapidAPIAuth or RundownAuth object."""
        if provider not in ["rapidapi", "rundown"]:
            raise ValueError("API Provider must be either 'rapidapi' or 'rundown'")
        return (
            _RapidAPIAuth(api_key) if provider == "rapidapi" else _RundownAuth(api_key)
        )


class OddsType(str, Enum):
    """Enum type for supporting American, decimal and fractional odds."""

    american = "american"
    decimal = "decimal"
    fractional = "fractional"


class Rundown:
    """The Rundown REST API client class supporting user configuration.

    Args:
        api_key: The API key to use.
        api_provider: The API provider. Must be either 'rundown' or 'rapidapi'
            (case insensitive).
        odds_type: Your preferred odds type. Must be one of 'american', 'decimal',
            or 'fractional' (case insensitive).
        timezone: Your preferred timezone.

    odds_type and timezone will be used to format responses from the API.

    Attributes:
        odds_type (OddsType): Your preferred odds type.
        timezone (str): Your preferred timezone.
    """

    def __init__(
        self,
        api_key: str,
        api_provider: str = "rapidapi",
        odds_type: str = "american",
        timezone: str = "local",
    ):
        self._auth = _Auth.factory(api_provider.lower(), api_key)
        self._session = requests.session()
        self._session.headers.update(self._auth.headers)

        self.odds_type = OddsType(odds_type.lower())
        self.timezone = timezone
