import arrow
import yaml


def utc_offset(timezone: str) -> int:
    """Get UTC offset in minutes for timezone.

    Args:
        timezone: Timezone string of form accepted by Arrow library.

    Returns:
        int: the UTC offset in minutes.
    """
    t_delta = arrow.now(timezone).utcoffset()
    return int(t_delta.days * 24 * 60 + t_delta.seconds / 60)


def utc_shift(timezone: str) -> int:
    """Get the number of minutes to shift UTC time by for a 24 hour window in timezone.

    This function is used by Rundown events methods in order to shift the 24 hour window
    for which the API will match events.

    Args:
        timezone: Timezone string of form accepted by Arrow library.

    Example:
        Phoenix is 7 hours behind UTC, so midnight in Phoenix is UTC midnight + 7 hours.
        Therefore in order to get capture events Monday's events in Phoenix time, the 24
        hour window needs to be shifted forwards by 7 hours. Otherwise Monday night's
        games (Phoenix time) would be split between Monday and Tuesday (UTC time).

    Returns:
        int: The number of minutes to shift UTC by.
    """
    return -utc_offset(timezone)


def utc_shift_to_tz(shift: int) -> str:
    """Given a number of minutes to shift UTC by, get matching ISO 8601 timezone string.

    Args:
        shift (int): Amount to shift UTC by to get 24 hour window in desired timezone.

    Example:
        shift = 420 (Phoenix time): function returns '-07:00'

    Returns:
        str: ISO 8601 timezone string.
    """
    sign = "+" if shift < 0 else "-"
    # Need to use the absolute value because of the way Python does modular arithmetic.
    hours, minutes = divmod(abs(shift), 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def write_yaml(obj, fname):
    with open(fname, "w") as f:
        yaml.dump(obj, f)


def read_yaml(fname):
    with open(fname, "r") as f:
        obj = yaml.safe_load(f)
    return obj
