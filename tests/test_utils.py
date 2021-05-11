import pytest

from rundown.utils import utc_offset, utc_shift_to_tz


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


@pytest.mark.parametrize(
    "offset, expected",
    [
        (300, "-05:00"),
        (-300, "+05:00"),
        (-301, "+05:01"),
        (301, "-05:01"),
    ],
)
def test_utc_offset_formatted(offset, expected):
    # Use only timezones with no daylight savings so tests will always pass.
    assert utc_shift_to_tz(offset) == expected
