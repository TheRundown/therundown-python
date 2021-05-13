from pydantic import BaseModel


class BaseTeam(BaseModel):
    team_id: int
    name: str
    mascot: str
    abbreviation: str


class Team(BaseTeam):
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
