from pydantic import BaseModel, validator
import arrow

from rundown.usercontext import context_timezone

"""Module containing resources returned by Rundown.dates method."""


class Date(BaseModel):
    """Date class for returning dates in ISO 8601 string format.

    attributes:
        date: ISO 8601 date
    """

    date: str

    @validator("date")
    def make_timezone(cls, v):
        """Format date returned from server.

        The dates incorrectly always show UTC timezone, but the local time will be
        correct with respect to timezone context_timezone. So it is only necessary to
        truncate the date string.
        """
        wrong_timezone = arrow.get(v)
        correct_timezone = wrong_timezone.replace(tzinfo=context_timezone.get())
        return str(correct_timezone)


class Epoch(BaseModel):
    """Epoch class for returning dates in timestamp format.

    attributes:
        timestamp: Epoch timestamp
    """

    timestamp: int
