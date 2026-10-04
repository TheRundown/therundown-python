"""Small, synchronous client for the documented TheRundown API v2 endpoints."""

import math
import os
import re
from datetime import date, datetime
from typing import Any, Dict, Optional, Sequence, Union

import requests


IDFilter = Union[str, Sequence[int]]


class TheRundownClient:
    """API v2 client using an explicit key or THERUNDOWN_API_KEY.

    Responses are returned unchanged as JSON dictionaries. HTTP failures raise
    requests.HTTPError; transport failures and timeouts use requests exceptions.
    The latest HTTP response is available through last_response, including its
    usage and delay headers. Requests are not automatically retried.
    """

    BASE_URL = "https://therundown.io/api/v2"

    def __init__(self, api_key: Optional[str] = None, *, timeout: float = 30.0):
        key = os.getenv("THERUNDOWN_API_KEY") if api_key is None else api_key
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Supply an API key or set THERUNDOWN_API_KEY")
        key = key.strip()
        if "\r" in key or "\n" in key:
            raise ValueError("API key must not contain line breaks")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be a positive, finite number of seconds")

        self._session = requests.Session()
        self._session.headers.update({"X-TheRundown-Key": key})
        self._timeout = timeout
        self.last_response: Optional[requests.Response] = None

    def list_sports_dates(self, sport_ids: Optional[IDFilter] = None) -> Dict[str, Any]:
        """GET /sports/dates, optionally filtered by comma-separated sport IDs.

        The returned dictionary is keyed by sport ID, with a dates array for each
        sport. Omit sport_ids to leave the server's selection unchanged.
        """
        params = {}
        if sport_ids is not None:
            params["sport_ids"] = _csv_ids(sport_ids, "sport_ids")
        return self._get("/sports/dates", params)

    def get_events(
        self,
        sport_id: int,
        event_date: Union[str, date],
        *,
        market_ids: Optional[IDFilter] = None,
        affiliate_ids: Optional[IDFilter] = None,
        main_line: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """GET /sports/{sport_id}/events/{YYYY-MM-DD} with optional filters.

        ID filters accept a sequence of integers or a comma-separated string.
        market_ids permits at most 12 IDs. affiliate_ids=[0] requests scores only.
        main_line=True selects main lines and also excludes closed prices.
        Omitted filters retain server defaults. The meta/events envelope and all
        odds, sentinel values and timestamps are returned unchanged.
        """
        _validate_id(sport_id, "sport_id", minimum=1)
        day = _event_date(event_date)
        params = {}
        if market_ids is not None:
            params["market_ids"] = _csv_ids(market_ids, "market_ids", maximum=12)
        if affiliate_ids is not None:
            params["affiliate_ids"] = _csv_ids(
                affiliate_ids, "affiliate_ids", minimum=0
            )
        if main_line is not None:
            if not isinstance(main_line, bool):
                raise ValueError("main_line must be True, False, or None")
            params["main_line"] = "true" if main_line else "false"
        return self._get(f"/sports/{sport_id}/events/{day}", params)

    def _get(self, path: str, params: Dict[str, str]) -> Dict[str, Any]:
        self.last_response = None
        response = self._session.get(
            self.BASE_URL + path,
            params=params,
            timeout=self._timeout,
            allow_redirects=False,
        )
        self.last_response = response
        response.raise_for_status()
        if 300 <= response.status_code < 400:
            # Custom API-key headers must not be forwarded to redirect targets.
            raise requests.HTTPError("Unexpected API redirect", response=response)
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected an API JSON object")
        return data

    def close(self) -> None:
        """Close the client's HTTP connection pool."""
        self._session.close()

    def __enter__(self) -> "TheRundownClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def _validate_id(value: int, name: str, *, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(
            f"{name} must contain integers greater than or equal to {minimum}"
        )


def _csv_ids(
    values: IDFilter, name: str, *, minimum: int = 1, maximum: Optional[int] = None
) -> str:
    if isinstance(values, str):
        parts = values.split(",")
        if not all(re.fullmatch(r"[0-9]+", part.strip()) for part in parts):
            raise ValueError(f"{name} must be a nonempty comma-separated list of IDs")
        items = [int(part.strip()) for part in parts]
    elif isinstance(values, Sequence) and not isinstance(values, (bytes, bytearray)):
        items = list(values)
    else:
        raise ValueError(
            f"{name} must be an integer sequence or comma-separated string"
        )
    if not items:
        raise ValueError(f"{name} must not be empty; use None to omit the filter")
    if maximum is not None and len(items) > maximum:
        raise ValueError(f"{name} accepts at most {maximum} IDs per request")
    for item in items:
        _validate_id(item, name, minimum=minimum)
    return ",".join(str(item) for item in items)


def _event_date(value: Union[str, date]) -> str:
    if isinstance(value, datetime):
        raise ValueError("event_date must be a date or a YYYY-MM-DD string")
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        raise ValueError("event_date must be a date or a YYYY-MM-DD string")
    date.fromisoformat(value)
    return value
