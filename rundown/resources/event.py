from typing import Optional, Union

from pydantic import BaseModel, validator

from rundown.resources.team import TeamDeprecated, TeamNormalized
from rundown.resources.schedule import BaseSchedule
from rundown.resources.line import Moneyline, Spread, Total
from rundown.resources.sportsbook import Sportsbook
from rundown.resources.validators import change_timezone


class SportsbookLines(BaseModel):
    line_id: int
    moneyline: Moneyline
    spread: Spread
    total: Total
    affiliate: Sportsbook


class SportsbookLinePeriod(SportsbookLines):
    period_id: Optional[int]
    period_description: str


class SportsbookLinePeriods(BaseModel):
    period_full_game: SportsbookLinePeriod
    period_first_half: SportsbookLinePeriod
    period_second_half: SportsbookLinePeriod
    period_first_period: SportsbookLinePeriod
    period_second_period: SportsbookLinePeriod
    period_third_period: SportsbookLinePeriod
    period_fourth_period: SportsbookLinePeriod
    period_live_full_game: SportsbookLinePeriod


class Score(BaseModel):
    event_id: str
    event_status: str
    score_away: int
    score_home: int
    winner_away: int
    winner_home: int
    score_away_by_period: list[int]
    score_home_by_period: list[int]
    venue_name: str
    venue_location: str
    game_clock: int
    display_clock: str
    game_period: int
    broadcast: str
    event_status_detail: str


class Event(BaseModel):
    event_id: str
    event_uuid: str
    sport_id: int
    event_date: str
    rotation_number_away: int
    rotation_number_home: int
    # 'score' may not be populated for games >100 days in advance.
    score: Optional[Score]
    teams: list[TeamDeprecated]
    teams_normalized: list[TeamNormalized]
    schedule: BaseSchedule
    lines: dict[int, Union[SportsbookLines, SportsbookLinePeriods]]

    _change_timezone = validator("event_date", allow_reuse=True)(change_timezone)
