from pydantic import BaseModel, validator

from rundown.resources.validators import change_timezone

"""Module with schedule related classes."""


class BaseSchedule(BaseModel):
    """Schedule class used by Event resource.

    attributes:
        season_type: Type of season
        season_year: Year of season
        event_name: Event name
        attendance: Attendance
    """

    season_type: str
    season_year: int
    event_name: str
    attendance: int


class Schedule(BaseSchedule):
    """Schedule class containing more attributes which is used by Rundown.schedule. Inherits from BaseSchedule.

    attributes:
        id: Schedule ID
        event_uuid: Event UUID
        event_id: Event ID
        sport_id: Sport ID
        away_team_id: Away team ID
        home_team_id: Home team ID
        away_team: Away team
        home_team: Home team
        date_event: Event date
        neutral_site: Is neutral site
        conference_competition: Is conference competition
        away_score: Away team score
        home_score: Home team score
        league_name: league name
        event_location: Event location
        updated_at: Time updated at
        event_status: Event status
        event_status_detail: Event status detail
    """

    id: int
    event_uuid: str
    event_id: str
    sport_id: int
    away_team_id: int
    home_team_id: int
    away_team: str
    home_team: str
    date_event: str
    neutral_site: bool
    conference_competition: bool
    away_score: int
    home_score: int
    league_name: str
    event_location: str
    updated_at: str
    event_status: str
    event_status_detail: str

    _change_timezone = validator("date_event", "updated_at", allow_reuse=True)(
        change_timezone
    )
