import pytest

from rundown.utils import utc_offset


@pytest.mark.parametrize(
    "tz, expected",
    [
        ("America/Phoenix", -7 * 60),
        ("Australia/Brisbane", 10 * 60),
        ("Atlantic/Reykjavik", 0 * 60),
    ],
)
def test_utc_offset(tz, expected):
    # Use only timezones with no daylight savings so tests will always pass.
    assert utc_offset(tz) == expected
