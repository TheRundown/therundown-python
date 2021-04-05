from typing import Union, List, Dict, Optional
from enum import Enum

import requests

from rundown.utils import utc_shift


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
        """Disallow parameters that have `None` or empty list as their value."""
        return {k: v for k, v in params.items() if v}

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

    def _validate_offset(self, offset: int):
        """Determine offset by parameter or self.timezone, with parameter precedence."""
        if offset is None:
            offset = utc_shift(self.timezone)
        return offset

    def _get_events(
        self,
        sport_id: int,
        lines_type: str,
        date_: str,
        offset: Optional[int] = None,
        *include: str,
    ):
        offset = self._validate_offset(offset)
        data = self._build_url_and_get_json(
            "sports", sport_id, lines_type, date_, offset=offset, include=include
        )
        return data

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

        Args:
            sport_id: ID for the league of interest.
            offset: Amount to offset UTC by in minutes. If offset is provided, it takes
                precedence over self.timezone, otherwise dates will be in timezone
                self.timezone.
            format: 'date' or 'epoch'. If format == 'epoch', offset and timezone are
                ignored, and dates will be in epoch format.

        Returns:
            list of Python datetime objects, or ints (if format=='epoch')
        """
        offset = self._validate_offset(offset)

        data = self._build_url_and_get_json(
            "sports", sport_id, "dates", offset=offset, format=format
        )
        return data

    def sportsbooks(self):
        """Get available sportsbooks.

        GET /affiliates

        Returns:
            list of resources.Sportsbook
        """
        data = self._build_url_and_get_json("affiliates")
        return data

    def teams_by_sport(self, sport_id: int):
        """Get teams for the league referenced by sport id.

        GET /sports/<sport-id>/teams

        Returns:
            list of resource.Team
        """
        data = self._build_url_and_get_json("sports", sport_id, "teams")
        return data

    def events_by_date(
        self,
        sport_id: int,
        date_: str,
        offset: Optional[int] = None,
        *include: str,
    ):
        """Get events by sport by date.

        GET /sports/<sport-id>/events/<date>

        Args:
            sport_id: ID for the league of interest.
            date_: The date of interest, in IS0 8601 format.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport_id, "events", date_, offset, *include)
        return data

    def opening_lines(
        self,
        sport_id: int,
        date_: str,
        offset: Optional[int] = None,
        *include: str,
    ):
        """Get events with opening lines by sport by date.

        GET /sports/<sport-id>/openers/<date>

        Args:
            sport_id: ID for the league of interest.
            date_: The date of interest, in IS0 8601 format.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport_id, "openers", date_, offset, include)
        return data

    def closing_lines(
        self,
        sport_id: int,
        date_: str,
        offset: Optional[int] = None,
        *include: str,
    ):
        """Get events with closing lines by sport by date.

        GET /sports/<sport-id>/closing/<date>

        Args:
            sport_id: ID for the league of interest.
            date_: The date of interest, in IS0 8601 format.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport_id, "closing", date_, offset, include)
        return data

    def events_delta(self, last_id, sport_id=None, *include: str):
        """Get events that have changed since request specified by last_id.

        GET /delta?last_id=<delta-last-id>

        Args:
            last_id: The `delta_last_id` value contained in some previous request to any
                'events' endpoint.
            sport_id: If included, return only events of sport sport_id.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Events object.

        Raises:
            requests.HTTPError: If too many events have been updated since last_id.
        """
        data = self._build_url_and_get_json(
            "delta", last_id=last_id, sport_id=sport_id, include=include
        )
        return data

    def event(self, event_id: int, *include: str):
        """Get event by event id.

        GET /events/<event-id>

        Args:
            event_id: The event id for the event of interest.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Event object.
        """
        data = self._build_url_and_get_json("events", event_id, *include)
        return data

    def moneyline(self, line_id, *include: str):
        """Get line history for moneyline referenced by line_id.

        GET /lines/<line-id>/moneyline

        Returns:
            list of resources.Moneyline
        """
        data = self._build_url_and_get_json(
            "lines", line_id, "moneyline", include=include
        )
        return data

    def spread(self, line_id: int, *include: str):
        """Get line history for spread referenced by line_id.

        GET /lines/<line-id>/spread

        Returns:
            list of resources.Spread
        """
        data = self._build_url_and_get_json("lines", line_id, "spread", include=include)
        return data

    def total(self, line_id, *include: str):
        """Get line history for total referenced by line_id.

        GET /lines/<line-id>/total

        Returns:
            list of resources.Total
        """
        data = self._build_url_and_get_json("lines", line_id, "total", include=include)
        return data
