from typing import Optional, Union

from pydantic import BaseModel, Field, validator

from rundown.resources.validators import change_timezone


class Line(BaseModel):
    line_id: int
    date_updated: str
    format: str

    _change_timezone = validator("date_updated", allow_reuse=True)(change_timezone)


class ExtendedLine(Line):
    """Line object with added fields, used by Totals and Spread."""

    event_id: str
    affiliate_id: int


class Moneyline(Line):
    moneyline_away: Optional[Union[int, float]] = Field(...)
    moneyline_away_delta: Optional[int] = Field(...)
    moneyline_home: Optional[int] = Field(...)
    moneyline_home_delta: Optional[int] = Field(...)
    moneyline_draw: Optional[int] = Field(...)
    moneyline_draw_delta: Optional[int] = Field(...)


class MoneylinePeriod(Moneyline):
    period_id: int
    period_description: str


class SpreadElement(BaseModel):
    affiliate_id: int
    point_spread_away: Optional[float]
    point_spread_away_delta: Optional[float]
    point_spread_home: Optional[float]
    point_spread_home_delta: Optional[float]
    point_spread_away_money: Optional[int]
    point_spread_away_money_delta: Optional[int]
    point_spread_home_money: Optional[int]
    point_spread_home_money_delta: Optional[int]


class Spread(ExtendedLine):
    point_spread_away: Optional[float] = Field(...)
    point_spread_away_delta: Optional[float] = Field(...)
    point_spread_home: Optional[float] = Field(...)
    point_spread_home_delta: Optional[float] = Field(...)
    point_spread_away_money: Optional[int] = Field(...)
    point_spread_away_money_delta: Optional[int] = Field(...)
    point_spread_home_money: Optional[int] = Field(...)
    point_spread_home_money_delta: Optional[int] = Field(...)
    extended_spreads: list[SpreadElement] = []


class SpreadPeriod(Spread):
    period_id: int
    period_description: str


class TotalElement(BaseModel):
    affiliate_id: int
    total_over: Optional[float]
    total_over_delta: Optional[float]
    total_under: Optional[float]
    total_under_delta: Optional[float]
    total_over_money: Optional[int]
    total_over_money_delta: Optional[int]
    total_under_money: Optional[int]
    total_under_money_delta: Optional[int]


class Total(ExtendedLine):
    total_over: Optional[float] = Field(...)
    total_over_delta: Optional[float] = Field(...)
    total_under: Optional[float] = Field(...)
    total_under_delta: Optional[float] = Field(...)
    total_over_money: Optional[int] = Field(...)
    total_over_money_delta: Optional[int] = Field(...)
    total_under_money: Optional[int] = Field(...)
    total_under_money_delta: Optional[int] = Field(...)
    extended_totals: list[TotalElement] = []


class TotalPeriod(Total):
    period_id: int
    period_description: str
