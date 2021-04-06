from pydantic import BaseModel


class Sportsbook(BaseModel):
    affiliate_name: str
    affiliate_id: int
    affiliate_url: str
