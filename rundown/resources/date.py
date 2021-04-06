from pydantic import BaseModel, validator


class Date(BaseModel):
    timezone: str
    date_: str

    @validator("date_")
    def make_timezone(cls, v, values):
        """Format date returned from server.

        The dates incorrectly always show UTC timezone, but the local time will be
        correct with respect to timezone. So it is only necessary to truncate the date
        string.
        """
        return v.split("+")[0]


class Epoch(BaseModel):
    timestamp: int
