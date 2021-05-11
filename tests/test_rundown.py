import pytest
import arrow

from rundown.rundown import _Base, _RundownBase, _RapidAPIBase
from rundown.resources.events import Events
from rundown.resources.event import Event, EventLinePeriods
from rundown.resources.lineperiods import LinePeriods
from rundown.resources.sport import Sport


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
    def test_dates_by_sport_always_has_UTC_time(self, rundown):
        """Show that the API always returns UTC timezone for dates_by_sport, but the
        time of the first event will be localized according the given offset.
        """
        rundown.dates_by_sport("MLB", offset=420)  # Phoenix Time
        raw_dates1 = rundown._json["dates"]
        rundown.dates_by_sport("MLB", offset=0)  # UTC Time
        raw_dates2 = rundown._json["dates"]
        for d1, d2 in list(zip(raw_dates1, raw_dates2)):
            # All responses have UTC timezone.
            assert d1[-5:] == d2[-5:] == "+0000"

        # Replace UTC timezone with correct timezone.
        correct_phoenix_time = arrow.get(raw_dates1[1]).replace(
            tzinfo="America/Phoenix"
        )
        correct_utc_time = arrow.get(raw_dates2[0])
        # Convert to UTC to equality.
        assert correct_phoenix_time.to("UTC") == correct_utc_time

    @pytest.mark.vcr()
    def test_offset_returns_different_events(self, rundown):
        """Show that the events returned when using an offset may be different than
        without an offset, because the 24 hour window of time is different.
        """
        tuesday = "2021-05-11"
        wednesday = "2021-05-12"
        # 24 hour window in Hawaiian time
        t_games = rundown.events_by_date("MLB", tuesday, offset=10 * 60)
        # 24 hour window in Australian time
        t_games_australia = rundown.events_by_date("MLB", tuesday, offset=-11 * 60)

        # Assert different games in each window.
        for e1 in t_games.events:
            assert e1.event_id not in [e2.event_id for e2 in t_games_australia.events]

        w_games = rundown.events_by_date("MLB", wednesday, offset=-11 * 60)
        # Assert same games with different dates because of offset.
        for e1, e2 in list(zip(t_games.events, w_games.events)):
            assert e1.event_id == e2.event_id


class TestRundown:
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
            # test with sport name
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
        # test with sport name
        data = rundown.teams_by_sport(sport_id)
        assert len(data) > 0

    @pytest.mark.parametrize(
        "sport_id, date, offset, include",
        [
            (6, "2021-04-03", None, []),  # completed
            (6, "2021-04-03", None, ["all_periods", "scores"]),
            (6, "2021-04-04", None, []),  # future events
            (6, "2021-04-04", None, ["all_periods", "scores"]),
            (6, "2021-04-03", None, ["scores"]),
            (6, "2021-04-03", None, ["all_periods"]),
            (6, "2021-05-08", None, []),  # some events in progress
            (6, "2021-05-08", None, ["all_periods"]),
            (6, "2021-05-08", None, ["all_periods"]),
        ],
    )
    @pytest.mark.vcr()
    def test_events_by_date(self, rundown, sport_id, date, offset, include):
        data = rundown.events_by_date(sport_id, date, *include, offset=offset)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "sport_id, date, offset, include",
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
    def test_opening_lines(self, rundown, sport_id, date, offset, include):
        data = rundown.opening_lines(sport_id, date, *include, offset=offset)
        assert isinstance(data, Events)

    @pytest.mark.parametrize(
        "sport_id, date, offset, include",
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
    def test_closing_lines(self, rundown, sport_id, date, offset, include):
        data = rundown.closing_lines(sport_id, date, *include, offset=offset)
        assert isinstance(data, Events)

    @pytest.mark.parametrize("date", [("2021-04-05")])
    @pytest.mark.vcr()
    def test_events_delta_initial_request(self, rundown, date):
        """Make initial events request, providing the delta_last_id."""
        data = rundown.events_by_date(6, date)
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
        data = rundown.events_delta(last_id, *include, sport=sport_id)
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
        if isinstance(data, list):
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
        if isinstance(data, list):
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
        if isinstance(data, list):
            assert len(data) > 0
        else:
            assert isinstance(data, LinePeriods)

    @pytest.mark.parametrize("sport_id, date_from, limit", [(6, "2021-04-05", 10)])
    @pytest.mark.vcr()
    def test_schedule(self, rundown, sport_id, date_from, limit):
        data = rundown.schedule(sport_id, date_from, limit)
        assert len(data) > 0
