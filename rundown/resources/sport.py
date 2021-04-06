from pydantic import BaseModel


class Sport(BaseModel):
    """Sport object.

    Attributes:
        name: Sport name.
        id: Sport ID.
    """

    sport_name: str
    sport_id: int
    pass
