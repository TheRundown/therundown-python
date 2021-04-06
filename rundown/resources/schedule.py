from pydantic import BaseModel, validator

from rundown.resources.validators import change_timezone


class BaseSchedule(BaseModel):
    season_type: str
    season_year: int
    event_name: str
    attendance: int


class Schedule(BaseSchedule):
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
