from pydantic import BaseModel

"""Module containing resource used by Rundown.sports"""


class Sport(BaseModel):
    """Sport class returned by Rundown.sports."""

    sport_name: str
    sport_id: int
