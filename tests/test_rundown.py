import pytest

from rundown.rundown import _Auth, _RundownAuth, _RapidAPIAuth


def test_auth_factory():
    a = _Auth.factory("rapidapi", "apikey")
    assert isinstance(a, _RapidAPIAuth)
    a = _Auth.factory("rundown", "apikey")
    assert isinstance(a, _RundownAuth)

    with pytest.raises(ValueError):
        _Auth.factory("foo", "apikey")


class TestRundown:
    # @pytest.mark.parametrize()
    def test_api_dates_with_odds(self):
        # TODO: investigate offset and incorrect dates.
        pass

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
