from typing import Union, Optional
import arrow

from rundown.usercontext import context_timezone


def change_timezone(dt_str: str) -> str:
    """Pydantic validator which changes the timezone of a date string.

    Uses context_timezone to get the timezone because Pydantic validation doesn't allow
    for passing arguments to validator functions.

    Args:
        dt_str: The date string to change.

    Returns:
        str: New date string with updated timezone.
    """
    timezone = context_timezone.get()
    dt = arrow.get(dt_str)
    new_dt = dt.to(timezone)
    return str(new_dt)


def make_none_if_not_published(line: Union[int, float]) -> Optional[Union[int, float]]:
    """Pydantic validator that looks for 'Not Published' marker and changes to None.

    Args:
        line: The line to check.

    Returns:
        The line if it doesn't have the 'Not Published' marker, otherwise None.
    """
    if line == 0.0001:
        return None
    else:
        return line
