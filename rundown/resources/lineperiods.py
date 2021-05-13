from typing import Union

from pydantic import BaseModel

from rundown.resources.line import MoneylinePeriod, SpreadPeriod, TotalPeriod

"""Module containing class used by Rundown line methods and the Event resource, when
'all_periods' is used as a parameter in a method call.
"""


class LinePeriods(BaseModel):
    """Class used to aggregate lines for different periods of a game or event."""

    period_full_game: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_first_half: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_second_half: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_first_period: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_second_period: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_third_period: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_fourth_period: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
    period_live_full_game: list[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]] = []
