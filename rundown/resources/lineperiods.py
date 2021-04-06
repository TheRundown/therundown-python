from typing import List, Union

from pydantic import BaseModel

from rundown.resources.line import MoneylinePeriod, SpreadPeriod, TotalPeriod


class LinePeriods(BaseModel):
    period_full_game: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_first_half: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_second_half: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_first_period: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_second_period: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_third_period: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_fourth_period: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
    period_live_full_game: List[Union[MoneylinePeriod, SpreadPeriod, TotalPeriod]]
