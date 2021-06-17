from typing import Optional, Union

from pydantic import BaseModel, validator

from rundown.resources.team import TeamDeprecated, Team
from rundown.resources.schedule import BaseSchedule
from rundown.resources.line import Moneyline, Spread, Total
from rundown.resources.sportsbook import Sportsbook
from rundown.resources.validators import change_timezone
from rundown.static.static import sportsbook_dict

"""Module for resources used by Rundown events."""


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
    """Event class describing an available event or game."""

    event_id: str
    # Some NCAAF and old NHL events don't have uuid.
    event_uuid: Optional[str] = None
    sport_id: int
    event_date: str
    # Rotation numbers not popuated for games 3 days in advance.
    rotation_number_away: Optional[int] = None
    rotation_number_home: Optional[int] = None
    # 'score' may not be populated for games >100 days in advance.
    score: Optional[Score] = None
    # 'teams' not populated for games 3 days in advance.
    teams: Optional[list[TeamDeprecated]] = None
    teams_normalized: list[Team]
    schedule: BaseSchedule
    lines: Optional[dict[str, SportsbookLines]] = None
    line_periods: Optional[dict[str, SportsbookLinePeriods]] = None

    _change_timezone = validator("event_date", allow_reuse=True)(change_timezone)

    @validator("lines", "line_periods")
    def use_sportsbook_names(
        cls, old_dict: dict[str, Union[SportsbookLines, SportsbookLinePeriods]]
    ) -> dict[str, Union[SportsbookLines, SportsbookLinePeriods]]:
        """Validator for lines and line_periods that swaps sportsbook ID for name.

        Args:
            old_dict: The dict with ID keys.

        Returns:
            The dict with sportsbook names as keys. If a sportsbook name is not found
            the key defaults to the original ID.
        """
        if old_dict is None:
            return

        new_dict = {sportsbook_dict.get(k, k): v for k, v in old_dict.items()}
        return new_dict
