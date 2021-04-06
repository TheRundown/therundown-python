from pydantic import BaseModel


class Sport(BaseModel):
    sport_name: str
    sport_id: int
