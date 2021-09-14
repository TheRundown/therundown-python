from pydantic import BaseModel

"""Module containing resource used by Rundown.sportsbooks"""


class Sportsbook(BaseModel):
    """Sportsbook class returned by Rundown.sportsbooks.

    attributes:
        affiliate_name: Sportsbook name
        affiliate_id: Sportsbook ID
        affiliate_url: Sportsbook URL
    """

    affiliate_name: str
    affiliate_id: int
    affiliate_url: str
