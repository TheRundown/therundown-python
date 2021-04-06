from typing import List

import pytest

from rundown.rundown import _Auth, _RundownAuth, _RapidAPIAuth
from rundown.resources.events import Events
from rundown.resources.event import Event, EventLinePeriods
from rundown.resources.lineperiods import LinePeriods


def test_auth_factory():
    a = _Auth.factory("rapidapi", "apikey")
    assert isinstance(a, _RapidAPIAuth)
    a = _Auth.factory("rundown", "apikey")
    assert isinstance(a, _RundownAuth)

    with pytest.raises(ValueError):
        _Auth.factory("foo", "apikey")


class TestRundown:
    # def test bad_route(self):
    # moneyline E.G
    # bad event id
    # over 500 scheduled events
    # pass

    @pytest.mark.parametrize(
        "segments, expected",
        [
            (
                [1, "openers", "2021-04-01"],
                "https://therundown-therundown-v1.p.rapidapi.com/1/openers/2021-04-01",
            )
        ],
    )
    def test_build_url(self, rundown, expected, segments):
        assert rundown._build_url(*segments) == expected

    @pytest.mark.parametrize(
        "segments, params",
        [
            (["sports"], {}),
            (["sports", "6", "dates"], {"offset": -480, "format": "date"}),
            (
                ["sports", "6", "events", "2021-04-02"],
                {"offset": -480, "include": ["scores", "all_periods"]},
            ),
        ],
    )
    @pytest.mark.vcr()
    def test_get(self, rundown, segments, params):
        url = rundown._build_url(*segments)
        res = rundown._get(url, **params)
        assert res.status_code == 200

    @pytest.mark.parametrize(
        "segments, params",
        [
            (["sports"], {}),
            (["sports", "6", "dates"], {"offset": -480, "format": "date"}),
            (
                ["sports", "6", "events", "2021-04-02"],
                {"offset": -480, "include": ["scores", "all_periods"]},
            ),
        ],
    )
    @pytest.mark.vcr()
    def test_patched_build_url_and_get_json(self, rundown, segments, params):
        data = rundown._build_url_and_get_json(*segments, **params)
        assert len(data) > 0

    @pytest.mark.vcr()
    def test_sports(self, rundown):
        data = rundown.sports()
        assert len(data) > 0

    @pytest.mark.parametrize(
        "sport_id, offset, format",
        [
            (6, None, "date"),
            (6, 420, "date"),
            (6, 0, "date"),
            (6, 420, "epoch"),
            # (2, None, "epoch"), # TODO: investigate failure
        ],
    )
    @pytest.mark.vcr()
    def test_dates_by_sport(self, rundown, sport_id, offset, format):
        data = rundown.dates_by_sport(sport_id, offset, format)
        assert len(data) > 0

    @pytest.mark.vcr()
    def test_sportsbooks(self, rundown):
        data = rundown.sportsbooks()
        assert len(data) > 0

    @pytest.mark.parametrize("sport_id", [2, 6])
    @pytest.mark.vcr()
    def test_teams_by_sport(self, sport_id, rundown):
        data = rundown.teams_by_sport(sport_id)
        assert len(data) > 0

    @pytest.mark.parametrize(
        "sport_id, date_, offset, include",
        [
            (6, "2021-04-03", None, []),  # completed
            (6, "2021-04-03", None, ["all_periods", "scores"]),
            (6, "2021-04-04", None, []),  # future events
            (6, "2021-04-04", None, ["all_periods", "scores"]),
            (6, "2021-04-03", None, ["scores"]),
            (6, "2021-04-03", None, ["all_periods"]),
        ],
    )
    @pytest.mark.vcr()
    def test_events_by_date(self, rundown, sport_id, date_, offset, include):
        data = rundown.events_by_date(sport_id, date_, offset, *include)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "sport_id, date_, offset, include",
        [
            (6, "2021-04-03", None, []),  # completed
            (6, "2021-04-03", None, ["all_periods", "scores"]),
            (6, "2021-04-04", None, []),  # future events
            (6, "2021-04-04", None, ["all_periods", "scores"]),
            (6, "2021-04-03", None, ["scores"]),
            (6, "2021-04-03", None, ["all_periods"]),
        ],
    )
    @pytest.mark.vcr()
    def test_opening_lines(self, rundown, sport_id, date_, offset, include):
        data = rundown.opening_lines(sport_id, date_, offset, *include)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "sport_id, date_, offset, include",
        [
            (6, "2021-04-03", None, []),  # completed
            (6, "2021-04-03", None, ["all_periods", "scores"]),
            (6, "2021-04-04", None, []),  # future events
            (6, "2021-04-04", None, ["all_periods", "scores"]),
            (6, "2021-04-03", None, ["scores"]),
            (6, "2021-04-03", None, ["all_periods"]),
        ],
    )
    @pytest.mark.vcr()
    def test_closing_lines(self, rundown, sport_id, date_, offset, include):
        data = rundown.closing_lines(sport_id, date_, offset, *include)
        assert isinstance(data, Events)

    @pytest.mark.parametrize("date_", [("2021-04-05")])
    @pytest.mark.vcr()
    def test_events_delta_initial_request(self, rundown, date_):
        """Make initial events request, providing the delta_last_id."""
        data = rundown.events_by_date(6, date_)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "last_id, sport_id, include",
        [
            ("11eb-95cd-8fb13b78-8369-8c223045627f", None, []),
            ("11eb-95cd-8fb13b78-8369-8c223045627f", 4, []),
        ],
    )
    @pytest.mark.vcr()
    def test_events_delta(self, rundown, last_id, sport_id, include):
        # Use delta_last_id from test_events_delta_initial_request.
        data = rundown.events_delta(last_id, sport_id, *include)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "event_id",
        [("3bd014c6b6ce2931653a057ba89237ef")],  # Tampa vs. Detroit NHL 2021-04-03
    )
    @pytest.mark.vcr()
    def test_event(self, rundown, event_id):
        data = rundown.event(event_id)
        assert isinstance(data, (EventLinePeriods, Event))

    @pytest.mark.parametrize(
        "line_id, include",
        [
            (14215098, []),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["scores"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods", "scores"]),  # Tampa vs. Detroit NHL 2021-04-03
        ],
    )
    @pytest.mark.vcr()
    def test_moneyline(self, rundown, line_id, include):
        data = rundown.moneyline(line_id, *include)
        if isinstance(data, List):
            assert len(data) > 0
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize(
        "line_id, include",
        [
            (14215098, []),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["scores"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods", "scores"]),  # Tampa vs. Detroit NHL 2021-04-03
        ],
    )
    @pytest.mark.vcr()
    def test_spread(self, rundown, line_id, include):
        data = rundown.spread(line_id, *include)
        if isinstance(data, List):
            assert len(data) > 0
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize(
        "line_id, include",
        [
            (14215098, []),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["scores"]),  # Tampa vs. Detroit NHL 2021-04-03
            (14215098, ["all_periods", "scores"]),  # Tampa vs. Detroit NHL 2021-04-03
        ],
    )
    @pytest.mark.vcr()
    def test_total(self, rundown, line_id, include):
        data = rundown.total(line_id, *include)
        if isinstance(data, List):
            assert len(data) > 0
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize("sport_id, date_from, limit", [(6, "2021-04-05", 10)])
    @pytest.mark.vcr()
    def test_schedule_by_sport(self, rundown, sport_id, date_from, limit):
        data = rundown.schedule_by_sport(sport_id, date_from, limit)
        assert len(data) > 0
