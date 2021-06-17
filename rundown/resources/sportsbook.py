from pydantic import BaseModel

"""Module containing resource used by Rundown.sportsbooks"""


class Sportsbook(BaseModel):
    """Sportsbook class returned by Rundown.sportsbooks."""

    affiliate_name: str
    affiliate_id: int
    affiliate_url: str
