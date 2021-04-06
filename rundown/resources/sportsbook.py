from pydantic import BaseModel


class Sportsbook(BaseModel):
    """Class representing a sportsbook.

    Attributes:
        name: Affiliate name.
        id: Affiliate ID.
        url: Affiliate url.
    """

    affiliate_name: str
    affiliate_id: int
    affiliate_url: str
