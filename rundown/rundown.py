from typing import Union, List, Dict, Optional
from enum import Enum

import requests

from rundown.utils import utc_offset


class _RapidAPIAuth:
    """Authorization configuration required for making requests to RapidAPI."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "therundown-therundown-v1.p.rapidapi.com"
        self.api_url = "https://therundown-therundown-v1.p.rapidapi.com"
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

    def _build_url(self, *segments: Union[str, int]) -> str:
        """Build URL without query parameters."""
        base_url = self._auth.api_url
        return f"{base_url}/{'/'.join([str(s) for s in segments])}"

    def _clean_params(self, **params):
        """Disallow parameters that have `None` as their value."""
        return {k: v for k, v in params.items() if v is not None}

    def _get(self, url: str, **params: Union[str, int, List[str]]) -> requests.Response:
        """Make get request."""
        res = self._session.get(url, params=params)
        # TODO: handle 404 not found - should never happen if called through methods.
        return res

    def _build_url_and_get_json(
        self, *segments: Union[str, int], **params: Union[str, int, List[str]]
    ) -> Dict:
        """Build URL from segments and make get request to API.

        Returns:
            [type]: [description]
        """
        url = self._build_url(*segments)
        params = self._clean_params(**params)
        res = self._get(url, **params)
        return res.json()

    def sports(self):
        """Get available sports.

        GET /sports

        Returns:
            list of resources.Sport
        """
        data = self._build_url_and_get_json("sports")
        return data

    def dates_by_sport(
        self, sport_id: int, offset: Optional[int] = None, format: str = "date"
    ):
        """Get dates with odds for future events.

        GET /sports/<sport-id>/dates

        If offset is provided, it takes precedence over self.timezone, otherwise dates
        will be in timezone self.timezone.

        If format == 'epoch', offset and timezone are ignored, and dates will be in
        epoch format.

        Returns:
            list of Python datetime objects, or ints (if format=='epoch')
        """
        if offset is None:
            offset = utc_offset(self.timezone)

        data = self._build_url_and_get_json(
            "sports", sport_id, "dates", offset=offset, format=format
        )
        return data
