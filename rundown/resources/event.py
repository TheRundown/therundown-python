from typing import Optional, Union

from pydantic import BaseModel, validator, Field

from rundown.resources.team import TeamDeprecated, Team
from rundown.resources.schedule import BaseSchedule
from rundown.resources.line import Moneyline, Spread, Total
from rundown.resources.sportsbook import Sportsbook
from rundown.resources.validators import change_timezone
from rundown.static.static import sportsbook_dict

"""Module for resources used by Rundown events."""


class SportsbookLines(BaseModel):
    """
    attributes:
        line_id: Line ID
        moneyline: Moneyline
        spread: Spread
        total: Total
        affiliate: Sportsbook
    """

    line_id: int
    moneyline: Moneyline
    spread: Spread
    total: Total
    affiliate: Sportsbook


class SportsbookLinePeriod(SportsbookLines):
    """
    Inherits from SportsbookLines.

    attributes:
        period_id: Period ID
        period_description: Period description
    """

    period_id: Optional[int]
    period_description: str


class SportsbookLinePeriods(BaseModel):
    """
    attributes:
        period_full_game: SportsbookLinePeriod
        period_first_half: SportsbookLinePeriod
        period_second_half: SportsbookLinePeriod
        period_first_period: SportsbookLinePeriod
        period_second_period: SportsbookLinePeriod
        period_third_period: SportsbookLinePeriod
        period_fourth_period: SportsbookLinePeriod
        period_live_full_game: SportsbookLinePeriod
    """

    period_full_game: SportsbookLinePeriod
    period_first_half: SportsbookLinePeriod
    period_second_half: SportsbookLinePeriod
    period_first_period: SportsbookLinePeriod
    period_second_period: SportsbookLinePeriod
    period_third_period: SportsbookLinePeriod
    period_fourth_period: SportsbookLinePeriod
    period_live_full_game: SportsbookLinePeriod


class Score(BaseModel):
    """
    attributes:
        event_id: Event ID
        event_status: Event status
        score_away: Away team score
        score_home: Home team score
        winner_away: 1 if away won, 0 otherwise
        winner_home: 1 if home won, 0 otherwise
        score_away_by_period: Away team score by period
        score_home_by_period: Home team score by period
        venue_name: Venue name
        venue_location: Venue location
        game_clock: Game clock
        display_clock: Display clock
        game_period: Game period
        broadcast: Broadcast
        event_status_detail: Event status detail
    """

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
    """Event class describing an available event or game.

    attributes:
        event_id: Event ID
        event_uuid: Event UUID
        sport_id: Sport ID
        event_date: Event date
        rotation_number_away: Away team rotation number
        rotation_number_home: Home team rotation number
        score: Score
        teams_deprecated: list of TeamDeprecated
        teams: list of Team
        schedule: Schedule
        lines: dict of SportsbookLines
        line_periods: dict of SportsbookLinePeriods
    """

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
    teams_deprecated: Optional[list[TeamDeprecated]] = Field(None, alias="teams")
    teams: list[Team] = Field(alias="teams_normalized")
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
