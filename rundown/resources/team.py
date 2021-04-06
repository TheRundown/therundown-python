from pydantic import BaseModel


class Team(BaseModel):
    """Team object. 'normalized_teams' maps to this object.

    Attributes:
        abbreviation
        mascot
        name
        record
        team_id
    """

    team_id: int
    name: str
    mascot: str
    abbreviation: str


class TeamNormalized(Team):
    """Team object within event context.

    Attributes:
        is_home
        is_away
    """

    ranking: int
    record: str
    is_away: bool
    is_home: bool


class TeamDeprecated(BaseModel):
    team_id: int
    team_normalized_id: int
    name: str
    is_away: bool
    is_home: bool
