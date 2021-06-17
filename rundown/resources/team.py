from pydantic import BaseModel

"""Module containing team related resources."""


class BaseTeam(BaseModel):
    """Base team class used by Rundown.team."""

    team_id: int
    name: str
    mascot: str
    abbreviation: str


class Team(BaseTeam):
    """Extended team class used by the 'teams_normalized' attribute in the Event
    resource.
    """

    ranking: int
    record: str
    is_away: bool
    is_home: bool


class TeamDeprecated(BaseModel):
    """Deprecated team class used by the 'team' attribute in the Event resource."""

    team_id: int
    team_normalized_id: int
    name: str
    is_away: bool
    is_home: bool
