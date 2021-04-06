from datetime import datetime

from pydantic import BaseModel, validator
import arrow

from rundown.usercontext import context_timezone


class Date(BaseModel):
    date: str

    @validator("date")
    def make_timezone(cls, v):
        """Format date returned from server.

        The dates incorrectly always show UTC timezone, but the local time will be
        correct with respect to timezone. So it is only necessary to truncate the date
        string.
        """
        naive_dt_str = v.split("+")[0]
        naive_dt = datetime.fromisoformat(naive_dt_str)
        dt = arrow.get(naive_dt, context_timezone.get())
        return str(dt)


class Epoch(BaseModel):
    timestamp: int
