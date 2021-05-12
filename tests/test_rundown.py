import pytest
import arrow
from deepdiff import DeepDiff

from rundown.rundown import _Base, _RundownBase, _RapidAPIBase
from rundown.resources.events import Events
from rundown.resources.sportsbook import Sportsbook
from rundown.resources.team import Team
from rundown.resources.event import Event
from rundown.resources.lineperiods import LinePeriods
from rundown.resources.line import Moneyline, Spread, Total
from rundown.resources.sport import Sport
from rundown.resources.date import Date, Epoch


def test_auth_factory():
    a = _Base.factory("rapidapi", "apikey")
    assert isinstance(a, _RapidAPIBase)
    a = _Base.factory("rundown", "apikey")
    assert isinstance(a, _RundownBase)

    with pytest.raises(ValueError):
        _Base.factory("foo", "apikey")


class TestAPI:
    """Class that tests API functionality in order to clarify how it works."""

    @pytest.mark.vcr()
    def test_dates_always_has_UTC_time(self, rundown):
        """Show that the API always returns UTC timezone for Rundown.dates, but the
        time of the first event will be localized according the given offset.
        """
        rundown.dates("MLB", offset=420)  # Phoenix Time
        raw_dates1 = rundown._json["dates"]
        rundown.dates("MLB", offset=0)  # UTC Time
        raw_dates2 = rundown._json["dates"]
        for d1, d2 in list(zip(raw_dates1, raw_dates2)):
            # All responses have UTC timezone.
            assert d1[-5:] == d2[-5:] == "+0000"

        # Replace UTC timezone with correct timezone.
        correct_phoenix_time = arrow.get(raw_dates1[0]).replace(
            tzinfo="America/Phoenix"
        )
        correct_utc_time = arrow.get(raw_dates2[0])
        # Convert to UTC to equality.
        assert correct_phoenix_time.to("UTC") == correct_utc_time

    @pytest.mark.vcr()
    def test_dates_epoch_is_shifted(self, rundown):
        """Similar to using 'date' format, the returned timestamp is shifted by the
        offset.
        """
        # Has timestamps with incorrect start times for first game of day.
        rundown.dates("NBA", offset=7 * 60, format="epoch")
        raw_dates1 = rundown._json["dates"]
        rundown.dates("NBA", offset=7 * 60)
        raw_dates2 = rundown._json["dates"]
        for d1, d2 in list(zip(raw_dates1, raw_dates2)):
            assert arrow.Arrow.fromtimestamp(d1) == arrow.get(d2)

        # Has timestamps with correct start times for first game of day. Shifting the
        # timezone should not change the timestamp.
        rundown.dates("NBA", offset=0, format="epoch")
        raw_dates3 = rundown._json["dates"]
        for d1, d3 in list(zip(raw_dates1, raw_dates3)):
            assert d1 != d3

    @pytest.mark.vcr()
    def test_offset_returns_different_events(self, rundown):
        """Show that the events returned when using an offset may be different than
        without an offset, because the 24 hour window of time is different.
        """
        tuesday = "2021-05-11"
        wednesday = "2021-05-12"
        # 24 hour window in Hawaiian time
        t_games = rundown.events("MLB", tuesday, offset=10 * 60)
        # 24 hour window in Australian time
        t_games_australia = rundown.events("MLB", tuesday, offset=-11 * 60)

        # Assert different games in each window.
        for e1 in t_games.events:
            assert e1.event_id not in [e2.event_id for e2 in t_games_australia.events]

        w_games = rundown.events("MLB", wednesday, offset=-11 * 60)
        # Assert same games with different dates because of offset.
        for e1, e2 in list(zip(t_games.events, w_games.events)):
            assert e1.event_id == e2.event_id

    @pytest.mark.parametrize(
        "method_name", ["events", "opening_lines", "closing_lines"]
    )
    @pytest.mark.vcr()
    def test_events_default_is_scores(self, rundown, method_name):
        """Show that the only difference between events requests with 'scores' included
        vs 'scores' not included is the 'delta_last_id' field, and the 'date_updated'
        fields in each line type. I.E. they return the same data.
        """
        method = getattr(rundown, method_name)
        method("MLB", "2021-05-10")
        raw_events1 = rundown._json
        method("MLB", "2021-05-10", "scores")
        raw_events2 = rundown._json

        diff = DeepDiff(raw_events1, raw_events2, ignore_order=True).to_dict()
        if diff:
            for k, v in diff["values_changed"].items():
                assert "delta_last_id" in k or "date_updated" in k

    @pytest.mark.parametrize(
        "method_name", ["events", "opening_lines", "closing_lines"]
    )
    @pytest.mark.vcr()
    def test_events_all_periods_scores(self, rundown, method_name):
        """Show that the only difference between events requests with 'all_periods'
        included vs 'all_periods' and 'scores' both included is the 'delta_last_id'
        field, and the 'date_updated' fields in each line type. I.E. they return the
        same data.
        """
        method = getattr(rundown, method_name)
        method("MLB", "2021-05-10", "all_periods", "scores")
        raw_events1 = rundown._json
        method("MLB", "2021-05-10", "all_periods")
        raw_events2 = rundown._json

        diff = DeepDiff(raw_events1, raw_events2, ignore_order=True).to_dict()
        if diff:
            for k, v in diff["values_changed"].items():
                try:
                    assert "delta_last_id" in k or "date_updated" in k
                except AssertionError:
                    diff2 = DeepDiff(v["new_value"], v["old_value"]).to_dict()
                    for k, v in diff2["values_changed"].items():
                        assert "delta_last_id" in k or "date_updated" in k

    @pytest.mark.parametrize(
        "method_name", ["events", "opening_lines", "closing_lines"]
    )
    @pytest.mark.vcr()
    def test_bad_event_date_returns_todays_lines(self, rundown, method_name):
        """If date string is bad, or too far in the future, server defaults to today's
        lines.
        """
        today = "2021-05-11"
        method = getattr(rundown, method_name)

        # 2021-09-31 has MLB games scheduled on that day, but it's too far in advance.
        bad_dates = ["foobar", "2021-09-31"]
        for d in bad_dates:
            method("MLB", date=d)
            raw_events = rundown._json
            for e in raw_events["events"]:
                assert today in e["event_date"]

    @pytest.mark.parametrize(
        "sport, date, expected", [("CFL", "2019-11-24", 0), ("NHL", "2019-10-02", 4)]
    )
    @pytest.mark.vcr()
    def test_cfl_not_implemented(self, rundown, sport, date, expected):
        """CFL doesn't return any events on days when games were played, but NHL does
        even for events that are older than the CFL events.
        """
        events = rundown.events(sport, date)
        assert len(events.events) == expected

    @pytest.mark.parametrize("method_name", ["moneyline", "spread", "total"])
    @pytest.mark.vcr()
    def test_lines_default_is_scores(self, rundown, method_name):
        """Similar to events, show that for lines methods not including any values for
        'include' parameter is the same as including 'scores'.
        """
        method = getattr(rundown, method_name)
        method(14215098)
        raw_lines1 = rundown._json
        method(14215098, "scores")
        raw_lines2 = rundown._json

        diff = DeepDiff(raw_lines1, raw_lines2, ignore_order=True).to_dict()
        assert not diff

    @pytest.mark.parametrize("method_name", ["moneyline", "spread", "total"])
    @pytest.mark.vcr()
    def test_lines_all_periods_scores(self, rundown, method_name):
        """Similar to events, show that for lines methods including 'all_periods' for
        'include' parameter is the same as including both 'all_periods' and 'scores'.
        """
        method = getattr(rundown, method_name)
        method(14215098, "all_periods")
        raw_lines1 = rundown._json
        method(14215098, "all_periods", "scores")
        raw_lines2 = rundown._json

        diff = DeepDiff(raw_lines1, raw_lines2, ignore_order=True).to_dict()
        assert not diff


class TestRundown:
    event_methods_args = [
        ("MLB", "2021-04-03", None, []),  # completed events
        ("MLB", "2021-04-03", None, ["all_periods"]),
        ("MLB", "2021-05-11", None, []),  # today's events, some in progress
        ("MLB", "2021-05-11", None, ["all_periods"]),
        ("MLB", "2021-05-12", None, []),  # events 1 day in future
        ("MLB", "2021-05-12", None, ["all_periods"]),
        ("MLB", "2021-05-15", None, []),  # events 3 days in future (no lines yet)
        ("MLB", "2021-05-15", None, ["all_periods"]),
        # Test all sports
        ("NCAAF", "2020-09-05", None, []),
        ("NCAAF", "2020-09-05", None, ["all_periods"]),
        ("NFL", "2020-09-13", None, []),
        ("NFL", "2020-09-13", None, ["all_periods"]),
        ("NBA", "2021-05-11", None, []),
        ("NBA", "2021-05-11", None, ["all_periods"]),
        ("NCAAB", "2021-03-18", None, []),
        ("NCAAB", "2021-03-18", None, ["all_periods"]),
        ("NHL", "2021-05-11", None, []),
        ("NHL", "2021-05-11", None, ["all_periods"]),
        ("UFC", "2021-04-24", None, []),
        ("UFC", "2021-04-24", None, ["all_periods"]),
        ("WNBA", "2021-05-14", None, []),
        ("WNBA", "2021-05-14", None, ["all_periods"]),
        ("MLS", "2021-05-08", None, []),
        ("MLS", "2021-05-08", None, ["all_periods"]),
    ]

    line_methods_args = [
        (14526697, []),  # MLB
        (14526696, ["all_periods"]),
        (14525410, []),  # NHL
        (14525400, ["all_periods"]),
        # (10970577, []),  # NCAAF - line history not found for lines.
        # (10970698, ["all_periods"]),
        (10731355, []),  # NFL
        (10719638, ["all_periods"]),
        (14525462, []),  # NBA
        (14525460, ["all_periods"]),
        (13825276, []),  # NCAAB
        (13825255, ["all_periods"]),
        (13843138, []),  # UFC
        (13843162, ["all_periods"]),
        (14418793, []),  # MLS
        (14418796, ["all_periods"]),
    ]

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

    @pytest.mark.parametrize(
        "sport, expected",
        [
            ("UFC/MMA", 7),
            ("UFC", 7),
            ("MMA", 7),
            (7, 7),
            (42, 42),  # not a valid sport ID
        ],
    )
    def test_validate_sport(self, rundown, sport, expected):
        sport_id = rundown._validate_sport(sport)
        assert sport_id == expected

    def test_validate_sport_exception(self, rundown):
        with pytest.raises(KeyError):
            rundown._validate_sport("ufc")

    @pytest.mark.vcr()
    def test_sports(self, rundown):
        data = rundown.sports()
        assert len(data) > 0
        assert all(isinstance(el, Sport) for el in data)

    @pytest.mark.parametrize(
        "sport_id, offset, format, expected_timezone",
        [
            (6, None, "date", "-07:00"),  # rundown fixture using Phoenix time.
            (6, 420, "date", "-07:00"),
            (6, -420, "date", "+07:00"),
            (6, 300, "date", "-05:00"),
            (6, 30, "date", "-00:30"),
            ("NBA", None, "date", "-07:00"),
            ("MLB", None, "date", "-07:00"),
        ],
    )
    @pytest.mark.vcr()
    def test_dates(self, rundown, sport_id, offset, format, expected_timezone):
        dates = rundown.dates(sport_id, offset=offset, format=format)
        assert len(dates) > 0
        for d in dates:
            assert isinstance(d, Date)
            assert d.date[-6:] == expected_timezone

    @pytest.mark.vcr()
    def test_dates_bad_sport_id(self, rundown):
        dates = rundown.dates(42)
        assert len(dates) == 0

    @pytest.mark.vcr()
    def test_dates_offset(self, rundown):
        dates1 = rundown.dates("NBA", offset=7 * 60)
        dates2 = rundown.dates("NBA", offset=-5 * 60)
        for d1, d2 in list(zip(dates1, dates2)):
            assert arrow.get(d1.date).to("UTC") == arrow.get(d2.date).to("UTC")

    @pytest.mark.vcr()
    def test_dates_epoch(self, rundown):
        dates1 = rundown.dates("NBA", offset=0, format="epoch")
        dates2 = rundown.dates("NBA", offset=0)

        ts1 = [d.timestamp for d in dates1]
        ts2 = [arrow.get(d.date).int_timestamp for d in dates2]
        for t1, t2 in list(zip(ts1, ts2)):
            assert t1 == t2

        for d in dates1:
            assert isinstance(d, Epoch)

    @pytest.mark.vcr()
    def test_sportsbooks(self, rundown):
        sportsbook = rundown.sportsbooks()
        assert len(sportsbook) > 0
        for s in sportsbook:
            assert isinstance(s, Sportsbook)

    @pytest.mark.parametrize("sport_id", [2, 6])
    @pytest.mark.vcr()
    def test_teams(self, sport_id, rundown):
        teams = rundown.teams(sport_id)
        assert len(teams) > 0
        for t in teams:
            assert isinstance(t, Team)

    @pytest.mark.parametrize("sport_id, date, offset, include", event_methods_args)
    @pytest.mark.vcr()
    def test_events(self, rundown, sport_id, date, offset, include):
        # sport_id, date, offset, include = method_args
        events = rundown.events(sport_id, date, *include, offset=offset)
        assert isinstance(events, Events)
        assert len(events.events) > 0
        for e in events.events:
            assert isinstance(e, Event)

    @pytest.mark.parametrize(
        "sport, date",
        [(6, "2000-05-11"), (42, "2021-05-11"), (42, "2000-05-11")],
    )
    @pytest.mark.vcr()
    def test_events_bad_arguments(self, rundown, sport, date):
        events = rundown.events(sport=sport, date=date)
        assert len(events.events) == 0

    @pytest.mark.parametrize("sport_id, date, offset, include", event_methods_args)
    @pytest.mark.vcr()
    def test_opening_lines(self, rundown, sport_id, date, offset, include):
        events = rundown.opening_lines(sport_id, date, *include, offset=offset)
        assert isinstance(events, Events)
        assert len(events.events) > 0
        for e in events.events:
            assert isinstance(e, Event)

    @pytest.mark.parametrize("sport_id, date, offset, include", event_methods_args)
    @pytest.mark.vcr()
    def test_closing_lines(self, rundown, sport_id, date, offset, include):
        events = rundown.closing_lines(sport_id, date, *include, offset=offset)
        assert isinstance(events, Events)
        assert len(events.events) > 0
        for e in events.events:
            assert isinstance(e, Event)

    @pytest.mark.parametrize("date", [("2021-04-05")])
    @pytest.mark.vcr()
    def test_events_delta_initial_request(self, rundown, date):
        """Make initial events request, providing the delta_last_id."""
        data = rundown.events(6, date)
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
        events = rundown.events_delta(last_id, *include, sport=sport_id)
        assert len(events.events) > 0
        for e in events.events:
            assert isinstance(e, Event)

    @pytest.mark.parametrize(
        "event_id",
        [("3bd014c6b6ce2931653a057ba89237ef")],  # Tampa vs. Detroit NHL 2021-04-03
    )
    @pytest.mark.vcr()
    def test_event(self, rundown, event_id):
        data = rundown.event(event_id)
        assert isinstance(data, Event)

    @pytest.mark.parametrize(
        "line_id, include",
        line_methods_args,
    )
    @pytest.mark.vcr()
    def test_moneyline(self, rundown, line_id, include):
        data = rundown.moneyline(line_id, *include)
        if isinstance(data, list):
            assert len(data) > 0
            for ml in data:
                assert isinstance(ml, Moneyline)
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize(
        "line_id, include",
        line_methods_args,
    )
    @pytest.mark.vcr()
    def test_spread(self, rundown, line_id, include):
        data = rundown.spread(line_id, *include)
        if isinstance(data, list):
            assert len(data) > 0
            for sp in data:
                assert isinstance(sp, Spread)
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize(
        "line_id, include",
        line_methods_args,
    )
    @pytest.mark.vcr()
    def test_total(self, rundown, line_id, include):
        data = rundown.total(line_id, *include)
        if isinstance(data, list):
            assert len(data) > 0
            for to in data:
                assert isinstance(to, Total)
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize("sport_id, date_from, limit", [(6, "2021-04-05", 10)])
    @pytest.mark.vcr()
    def test_schedule(self, rundown, sport_id, date_from, limit):
        data = rundown.schedule(sport_id, date_from, limit)
        assert len(data) > 0
