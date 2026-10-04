"""Replay recorded documentation responses without any network access."""

import json
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from rundown import TheRundownClient


FIXTURES = Path(__file__).parent / "fixtures" / "v2"


@pytest.fixture
def recorded_http(monkeypatch):
    """Mock the HTTP boundary but use real request preparation/JSON decoding."""
    responses = []

    def send(request, **kwargs):
        response = responses.pop(0)
        response.request = request
        response.url = request.url
        return response

    mock = Mock(side_effect=send)
    monkeypatch.setattr(requests.Session, "send", mock)

    def enqueue(name=None, *, status=200, headers=None, body=None):
        response = requests.Response()
        response.status_code = status
        response.headers.update(headers or {})
        response._content = (
            (FIXTURES / name).read_bytes() if name else json.dumps(body).encode()
        )
        responses.append(response)
        return response

    return mock, enqueue


def test_sports_dates_recorded_response_and_csv(recorded_http):
    send, enqueue = recorded_http
    response = enqueue("sports_dates.json")
    with TheRundownClient("fixture-key") as client:
        result = client.list_sports_dates([2, 3, 4, 6])
        assert result == response.json()
        assert result["4"]["dates"] == ["2026-02-13T00:30:00+0000"]
        assert client.last_response is response

    request = send.call_args.args[0]
    assert urlsplit(request.url).path == "/api/v2/sports/dates"
    assert parse_qs(urlsplit(request.url).query) == {"sport_ids": ["2,3,4,6"]}
    assert request.headers["X-TheRundown-Key"] == "fixture-key"
    assert "fixture-key" not in request.url
    assert send.call_args.kwargs["timeout"] == 30.0
    assert send.call_args.kwargs["allow_redirects"] is False


@pytest.mark.parametrize("day", ["2026-01-15", date(2026, 1, 15)])
@pytest.mark.parametrize("main_line, wire", [(True, "true"), (False, "false")])
def test_events_recorded_response_and_filters(recorded_http, day, main_line, wire):
    send, enqueue = recorded_http
    response = enqueue("events.json", headers={"X-Data-Delay-Seconds": "0"})
    with TheRundownClient("fixture-key", timeout=7.5) as client:
        result = client.get_events(
            4, day, market_ids=[1, 2, 3], affiliate_ids="19, 23", main_line=main_line
        )
        # Fixtures establish parsing, not server-side filtering behavior.
        assert result == response.json()
        assert result["meta"]["delta_last_id"] == "193500000"
        assert client.last_response.headers["X-Data-Delay-Seconds"] == "0"

    request = send.call_args.args[0]
    assert urlsplit(request.url).path == "/api/v2/sports/4/events/2026-01-15"
    assert parse_qs(urlsplit(request.url).query) == {
        "market_ids": ["1,2,3"],
        "affiliate_ids": ["19,23"],
        "main_line": [wire],
    }
    assert send.call_args.kwargs["timeout"] == 7.5


def test_omitted_filters_preserve_server_defaults(recorded_http):
    send, enqueue = recorded_http
    enqueue("sports_dates.json")
    enqueue("events.json")
    with TheRundownClient("fixture-key") as client:
        client.list_sports_dates()
        client.get_events(4, "2026-01-15")
    for call in send.call_args_list:
        assert urlsplit(call.args[0].url).query == ""


def test_scores_only_sentinel_is_serialized(recorded_http):
    send, enqueue = recorded_http
    # The recorded full envelope is not evidence of the scores-only response.
    enqueue("events.json")
    with TheRundownClient("fixture-key") as client:
        client.get_events(4, "2026-01-15", affiliate_ids=[0])
    assert parse_qs(urlsplit(send.call_args.args[0].url).query) == {
        "affiliate_ids": ["0"]
    }


@pytest.mark.parametrize("explicit", [None, " constructor-key "])
def test_key_from_environment_or_constructor(monkeypatch, recorded_http, explicit):
    monkeypatch.setenv("THERUNDOWN_API_KEY", " environment-key ")
    send, enqueue = recorded_http
    enqueue("sports_dates.json")
    with TheRundownClient(explicit) as client:
        client.list_sports_dates()
    expected = "environment-key" if explicit is None else "constructor-key"
    assert send.call_args.args[0].headers["X-TheRundown-Key"] == expected


@pytest.mark.parametrize("key", [None, "", "  ", 123, "secret\r\nheader"])
def test_invalid_credentials_fail_without_disclosing_key(monkeypatch, key):
    monkeypatch.delenv("THERUNDOWN_API_KEY", raising=False)
    with pytest.raises(ValueError) as error:
        TheRundownClient(key)
    assert "secret" not in str(error.value)


def test_invalid_environment_key_does_not_disclose_key(monkeypatch):
    monkeypatch.setenv("THERUNDOWN_API_KEY", "secret\nheader")
    with pytest.raises(ValueError) as error:
        TheRundownClient()
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("timeout", [0, -1, True, "30", float("inf"), float("nan")])
def test_invalid_timeout(timeout):
    with pytest.raises(ValueError):
        TheRundownClient("fixture-key", timeout=timeout)


@pytest.mark.parametrize("ids", [[], "", "1,", "1.5", [True], [-1], b"1,2"])
def test_invalid_sports_filter_never_sends(recorded_http, ids):
    send, _ = recorded_http
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(ValueError):
            client.list_sports_dates(ids)
    send.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [
        {"market_ids": list(range(1, 14))},
        {"market_ids": [0]},
        {"market_ids": []},
        {"affiliate_ids": [-1]},
        {"affiliate_ids": ["19"]},
        {"affiliate_ids": []},
        {"main_line": "false"},
        {"main_line": 1},
    ],
)
def test_invalid_event_filters_never_send(recorded_http, options):
    send, _ = recorded_http
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(ValueError):
            client.get_events(4, "2026-01-15", **options)
    send.assert_not_called()


@pytest.mark.parametrize(
    "sport, day",
    [
        (True, "2026-01-15"),
        (0, "2026-01-15"),
        ("4", "2026-01-15"),
        (4, "2026-02-30"),
        (4, "20260115"),
        (4, "2026-01-15/other"),
        (4, datetime(2026, 1, 15)),
    ],
)
def test_invalid_event_path_never_sends(recorded_http, sport, day):
    send, _ = recorded_http
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(ValueError):
            client.get_events(sport, day)
    send.assert_not_called()


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500, 503])
def test_http_error_preserves_response_and_does_not_retry(recorded_http, status):
    send, enqueue = recorded_http
    response = enqueue(
        status=status,
        headers={"Retry-After": "60"},
        body={"error": "Injected fixture failure"},
    )
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(requests.HTTPError) as error:
            client.list_sports_dates()
        assert error.value.response is response
        assert client.last_response.json() == {"error": "Injected fixture failure"}
        assert client.last_response.headers["Retry-After"] == "60"
    assert send.call_count == 1


def test_redirect_is_not_followed(recorded_http):
    send, enqueue = recorded_http
    enqueue(status=302, headers={"Location": "https://example.invalid/"}, body={})
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(requests.HTTPError, match="Unexpected API redirect"):
            client.list_sports_dates()
    assert send.call_count == 1
    assert send.call_args.kwargs["allow_redirects"] is False


def test_timeout_does_not_retry_or_keep_stale_response(recorded_http):
    send, enqueue = recorded_http
    enqueue("sports_dates.json")
    with TheRundownClient("fixture-key") as client:
        client.list_sports_dates()
        send.side_effect = requests.Timeout("Injected timeout")
        with pytest.raises(requests.Timeout):
            client.list_sports_dates()
        assert client.last_response is None
    assert send.call_count == 2


def test_context_manager_closes_pool(monkeypatch):
    close = Mock()
    monkeypatch.setattr(requests.Session, "close", close)
    with TheRundownClient("fixture-key"):
        pass
    close.assert_called_once()


@pytest.mark.parametrize("body", [[], None])
def test_invalid_response_shape(recorded_http, body):
    _, enqueue = recorded_http
    enqueue(body=body)
    with TheRundownClient("fixture-key") as client:
        with pytest.raises(ValueError, match="Expected an API JSON object"):
            client.list_sports_dates()
