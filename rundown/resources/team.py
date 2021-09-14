from pydantic import BaseModel

"""Module containing team related resources."""


class BaseTeam(BaseModel):
    """Base team class used by Rundown.team.

    attributes:
        team_id: Team ID
        name: Team name
        mascot: Mascot
        abbreviation: Team abbreviation
    """

    team_id: int
    name: str
    mascot: str
    abbreviation: str


class Team(BaseTeam):
    """Extended team class used by the 'teams_normalized' attribute in the Event
    resource. Inherits from BaseTeam.

    attributes:
        ranking: Ranking
        record: Record
        is_away: Is away
        is_home: Is home
    """

    ranking: int
    record: str
    is_away: bool
    is_home: bool


class TeamDeprecated(BaseModel):
    """Deprecated team class used by the 'team' attribute in the Event resource.

    attributes:
        team_id: Team ID
        team_normalized_id: Team Normalized ID
        name: Team name
        is_away: Is away
    """

    team_id: int
    team_normalized_id: int
    name: str
    is_away: bool
    is_home: bool
