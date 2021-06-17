from typing import Union, Optional, Literal
from collections.abc import Callable
from functools import wraps
from pathlib import Path

import requests
from pydantic import parse_obj_as

from rundown.utils import utc_shift, utc_shift_to_tz, write_yaml
from rundown.resources.sportsbook import Sportsbook
from rundown.resources.sport import Sport
from rundown.resources.date import Date, Epoch
from rundown.resources.team import BaseTeam
from rundown.resources.events import Events
from rundown.resources.event import Event
from rundown.resources.line import Moneyline, Spread, Total
from rundown.resources.lineperiods import LinePeriods
from rundown.resources.schedule import Schedule
from rundown.usercontext import user_context
from rundown.static.static import build_sports_dict

"""Module containing classes allowing the user to access the Rundown API."""


class _RapidAPIBase:
    """Configuration required for making requests to RapidAPI."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "therundown-therundown-v1.p.rapidapi.com"
        self.api_url = "https://therundown-therundown-v1.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
        }


class _RundownBase:
    """Configuration required for making requests to The Rundown's API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://therundown.io/api/v1"
        self.headers = {"X-TheRundown-Key": self.api_key}


class _Base:
    """Class supporting creation of _RapidAPIBase and _RundownBase objects."""

    @classmethod
    def factory(
        cls, provider: Literal["rapidapi", "rundown"], api_key: str
    ) -> Union[_RapidAPIBase, _RundownBase]:
        """Factory method returning _RapidAPIBase or _RundownBase object."""
        if provider not in ["rapidapi", "rundown"]:
            raise ValueError("API Provider must be either 'rapidapi' or 'rundown'")
        return (
            _RapidAPIBase(api_key) if provider == "rapidapi" else _RundownBase(api_key)
        )


class Rundown:
    """The Rundown REST API client class supporting user configuration.

    Both RapidAPI.com and TheRundown.io are supported.

    Args:
        api_key: The API key to use.
        api_provider: The API provider. Must be either 'rundown' or 'rapidapi'
            (case insensitive).
        timezone: Your preferred timezone.
            The following formats are accepted:
            - A str describing a timezone, similar to ‘US/Pacific’, or ‘Europe/Berlin’.
            - A str in ISO 8601 style, as in ‘+07:00’.
            - A str, one of the following: ‘local’, ‘utc’, ‘UTC’.

    timezone will be used to format responses from the API.

    Attributes:
        sport_names (dict[str, int]): Sports names and their IDs.
        timezone (str): Your preferred timezone.
    """

    def __init__(
        self,
        api_key: str,
        api_provider: Literal["rapidapi", "rundown"] = "rapidapi",
        timezone: str = "local",
        refresh_cached_data: bool = False,
    ):
        self._auth = _Base.factory(api_provider.lower(), api_key)
        self._session = requests.session()
        self._session.headers.update(self._auth.headers)

        self._json = {}

        self.timezone = timezone

        self.sport_names = {}
        if refresh_cached_data:
            self.refresh_sportsbooks()
            self.refresh_sports()
        else:
            self.sport_names = build_sports_dict()

    def _build_url(self, *segments: Union[str, int]) -> str:
        """Build URL without query parameters."""
        base_url = self._auth.api_url
        return f"{base_url}/{'/'.join([str(s) for s in segments])}"

    def _clean_params(self, **params: Union[str, int, list[Optional[str]], None]):
        """Disallow parameters that have `None` or empty list as their value."""

        def is_clean(v):
            if isinstance(v, list) and len(v) == 0:
                return False
            if v is None:
                return False
            return True

        return {k: v for k, v in params.items() if is_clean(v)}

    def _get(self, url: str, **params: Union[str, int, list[str]]) -> requests.Response:
        """Make get request."""
        res = self._session.get(url, params=params)
        # TODO: handle 404 not found - should never happen if called through methods.
        return res

    def _build_url_and_get_json(
        self, *segments: Union[str, int], **params: Union[str, int, list[str]]
    ) -> dict:
        """Build URL from segments and make get request to API."""
        url = self._build_url(*segments)
        params = self._clean_params(**params)
        res = self._get(url, **params)
        self._json = res.json()
        return self._json

    def _validate_offset(self, offset: int) -> int:
        """Determine offset by parameter or self.timezone, with parameter precedence."""
        if offset is None:
            offset = utc_shift(self.timezone)
        return offset

    def _validate_sport(self, sport: Union[int, str]) -> int:
        """Get the sport_id for sport.

        Args:
            sport: Either a string representing the sport, or an integer which is the
                sport's ID.

        Raises:
            KeyError: If the sport string is not a valid sport name.

        Returns:
            int: The sport's ID.
        """
        try:
            # sport may be optional argument to calling function, so allow None.
            sport_id = (
                sport
                if isinstance(sport, int) or sport is None
                else self.sport_names[sport.lower()]
            )
        except KeyError:
            # TODO
            raise KeyError(
                f"{sport} is not a valid sport name. Valid examples: 'NHL', 'nhl', 'MLB', 'NCAAF'."  # noqa E501
            )

        return sport_id

    def _get_events(
        self,
        sport: Union[int, str],
        lines_type: str,
        date: str,
        offset: Optional[int],
        *include: Literal["all_periods", "scores"],
    ) -> dict:
        offset = self._validate_offset(offset)
        sport_id = self._validate_sport(sport)
        data = self._build_url_and_get_json(
            "sports", sport_id, lines_type, date, offset=offset, include=include
        )
        return data

    def _with_timezone_context(f: Callable) -> Callable:
        """Decorator for methods that use self.timezone.

        Args:
            f: The function being given timezone context.

        Returns:
            The wrapped function with timezone context.
        """

        @wraps(f)
        def inner(self, *args, **kwargs):
            offset = kwargs["offset"] if "offset" in kwargs else None
            with user_context(
                self.timezone if offset is None else utc_shift_to_tz(offset)
            ):
                return f(self, *args, **kwargs)

        return inner

    def refresh_sportsbooks(self):
        data = self._build_url_and_get_json("affiliates")
        parent = Path(__file__).resolve().parent
        write_yaml(data, parent / "static/sportsbooks.yaml")

    def refresh_sports(self):
        data = self._build_url_and_get_json("sports")
        parent = Path(__file__).resolve().parent
        write_yaml(data, parent / "static/sports.yaml")
        self.sport_names = build_sports_dict()

    def sports(self) -> list[Sport]:
        """Get available sports.

        GET /sports

        Returns:
            list of resources.Sport.
        """
        data = self._build_url_and_get_json("sports")
        sports = parse_obj_as(list[Sport], data["sports"])
        return sports

    @_with_timezone_context
    def dates(
        self,
        sport: Union[int, str],
        *,
        offset: Optional[int] = None,
        format: Literal["date", "epoch"] = "date",
    ) -> list[Union[Date, Epoch]]:
        """Get dates with odds for future events.

        GET /sports/<sport-id>/dates

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.
            offset: Amount to offset UTC by in minutes. If offset is provided, it takes
                precedence over self.timezone, otherwise dates will be in timezone
                self.timezone.
            format: 'date' or 'epoch'. If format == 'epoch', offset and timezone are
                ignored, and dates will be in epoch format.

        Returns:
            list of resources.Date or resources.Epoch.
        """
        offset = self._validate_offset(offset)
        sport_id = self._validate_sport(sport)

        data = self._build_url_and_get_json(
            "sports", sport_id, "dates", offset=offset, format=format
        )
        if format == "date":
            resource = Date
            dates = [{"date": v} for v in data["dates"]]
        else:
            resource = Epoch
            dates = [{"timestamp": v} for v in data["dates"]]

        dates = parse_obj_as(list[resource], dates)
        return dates

    def sportsbooks(self) -> list[Sportsbook]:
        """Get available sportsbooks.

        GET /affiliates

        Returns:
            list of resources.Sportsbook.
        """
        data = self._build_url_and_get_json("affiliates")
        sportsbooks = parse_obj_as(list[Sportsbook], data["affiliates"])
        return sportsbooks

    def teams(self, sport: Union[int, str]) -> list[BaseTeam]:
        """Get teams for the league referenced by sport id.

        GET /sports/<sport-id>/teams

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.

        Returns:
            list of resource.Team.
        """
        sport_id = self._validate_sport(sport)
        data = self._build_url_and_get_json("sports", sport_id, "teams")
        teams = parse_obj_as(list[BaseTeam], data["teams"])
        return teams

    @_with_timezone_context
    def events(
        self,
        sport: Union[int, str],
        date: str,
        *include: Literal["all_periods", "scores"],
        offset: Optional[int] = None,
    ) -> Events:
        """Get events by sport by date.

        GET /sports/<sport-id>/events/<date>

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.
            date: The date of interest, in IS0 8601 format ('YYYY-MM-DD')
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport, "events", date, offset, *include)
        events = Events(**data)
        return events

    @_with_timezone_context
    def opening_lines(
        self,
        sport: Union[int, str],
        date: str,
        *include: Literal["all_periods", "scores"],
        offset: Optional[int] = None,
    ) -> Events:
        """Get events with opening lines by sport by date.

        GET /sports/<sport-id>/openers/<date>

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.
            date: The date of interest, in IS0 8601 format ('YYYY-MM-DD')
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport, "openers", date, offset, *include)
        events = Events(**data)
        return events

    @_with_timezone_context
    def closing_lines(
        self,
        sport: Union[int, str],
        date: str,
        *include: Literal["all_periods", "scores"],
        offset: Optional[int] = None,
    ) -> Events:
        """Get events with closing lines by sport by date.

        GET /sports/<sport-id>/closing/<date>

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.
            date: The date of interest, in IS0 8601 format ('YYYY-MM-DD')
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.
            offset: UTC offset in minutes. If offset is provided, it takes precedence
                over self.timezone, otherwise dates will be in timezone self.timezone.

        Returns:
            resources.Events object.
        """
        data = self._get_events(sport, "closing", date, offset, *include)
        events = Events(**data)
        return events

    @_with_timezone_context
    def events_delta(
        self,
        last_id: int,
        *include: Literal["all_periods", "scores"],
        sport: Optional[Union[int, str]] = None,
    ) -> Optional[Events]:
        """Get events that have changed since request specified by last_id.

        GET /delta?last_id=<delta-last-id>

        Args:
            last_id: The `delta_last_id` value contained in some previous request to any
                'events' endpoint.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.  If this argument is included, only
                events for the matching sport will be returned.

        Returns:
            resources.Events object.
        """
        sport_id = self._validate_sport(sport)
        data = self._build_url_and_get_json(
            "delta", last_id=last_id, sport_id=sport_id, include=include
        )
        if "error" in data:
            return None

        events = Events(**data)
        return events

    @_with_timezone_context
    def event(
        self, event_id: str, *include: Literal["all_periods", "scores"]
    ) -> Optional[Event]:
        """Get event by event id.

        GET /events/<event-id>

        Args:
            event_id: The event id for the event of interest.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default.

        Returns:
            resources.Event object, or None if no matching event could be found.
        """
        data = self._build_url_and_get_json("events", event_id, include=include)
        if "error" in data:
            return None

        e = Event(**data)
        return e

    @_with_timezone_context
    def moneyline(
        self,
        line_id: int,
        *include: Literal["all_periods", "scores"],
    ) -> Optional[Union[list[Moneyline], LinePeriods]]:
        """Get line history for moneyline referenced by line_id.

        GET /lines/<line-id>/moneyline

        Args:
            line_id: The line id for the line of interest.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default

        Returns:
            list of resources.Moneyline, or resources.LinePeriods object. None if line
                id could not be found, or the line has no moneylines available.
        """
        data = self._build_url_and_get_json(
            "lines", line_id, "moneyline", include=include
        )
        if "error" in data or "moneylines" in data and len(data["moneylines"]) == 0:
            return None

        if "all_periods" in include:
            lines = LinePeriods(**data["moneyline_periods"])
        else:
            lines = parse_obj_as(list[Moneyline], data["moneylines"])
        return lines

    @_with_timezone_context
    def spread(
        self, line_id: int, *include: str
    ) -> Optional[Union[list[Moneyline], LinePeriods]]:
        """Get line history for spread referenced by line_id.

        GET /lines/<line-id>/spread

        Args:
            line_id: The line id for the line of interest.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default

        Returns:
            list of resources.Spead, or resources.LinePeriods object. None if line id
                could not be found, or the line has no spreads available.
        """
        data = self._build_url_and_get_json("lines", line_id, "spread", include=include)
        if "error" in data or "spreads" in data and len(data["spreads"]) == 0:
            return None

        if "all_periods" in include:
            lines = LinePeriods(**data["spread_periods"])
        else:
            lines = parse_obj_as(list[Spread], data["spreads"])
        return lines

    @_with_timezone_context
    def total(
        self,
        line_id,
        *include: Literal["all_periods", "scores"],
    ) -> Optional[Union[list[Moneyline], LinePeriods]]:
        """Get line history for total referenced by line_id.

        GET /lines/<line-id>/total

        Args:
            line_id: The line id for the line of interest.
            include: Any of 'all_periods' and 'scores'. If 'all_periods' is included,
                lines for each period are included in the response. If 'scores' is
                included, lines for the event are included in the response. 'scores' by
                itself is the default

        Returns:
            list of resources.Total, or resources.LinePeriods object. None if line id
                could not be found, or the line has no totals available.
        """
        data = self._build_url_and_get_json("lines", line_id, "total", include=include)
        if "error" in data or "totals" in data and len(data["totals"]) == 0:
            return None

        if "all_periods" in include:
            lines = LinePeriods(**data["total_periods"])
        else:
            lines = parse_obj_as(list[Total], data["totals"])
        return lines

    @_with_timezone_context
    def schedule(
        self,
        sport: Union[int, str],
        date_from: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> list[Schedule]:
        """Get schedule for league referenced by sport.

        GET /sports/<sport-id>/schedule

        Args:
            sport: ID for the league of interest, or a string representing the league of
                interest. Valid sport names can be found in the 'sport_names' attribute.
                Examples: 'NHL', 'NBA', 'MLB'.
            date_from: ISO 8601 date string of the starting date of the scheduled
                events. The server considers the date to be in UTC. Defaults to today.
            limit: Number of events to retrieve. Maximum 500.

        Returns:
            list of resources.Schedule.
        """
        sport_id = self._validate_sport(sport)

        # 'from' is a reserved keyword in Python, so use dict.
        data = self._build_url_and_get_json(
            "sports", sport_id, "schedule", **{"from": date_from, "limit": limit}
        )
        schedules = parse_obj_as(list[Schedule], data["schedules"])
        return schedules
