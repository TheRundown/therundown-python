from typing import Optional, List

# from pydantic import BaseModel, validator
from pydantic import BaseModel, Field

# TODO: Is it bad to have odds being different data types (float or int) / representing
# different meanings (fractional, decimal, or american) based on odds type?


class Line(BaseModel):
    """Base class for different line types.

    Attributes:
        date_updated: Timezone-aware datetime object.
        format: 'American', 'Decimal' or 'Fractional'.
        line_id: The line id.
    """

    line_id: int
    date_updated: str
    format: str

    # @validator("date_updated")
    # def make_timezone(cls, v, values):
    #     pass


class ExtendedLine(Line):
    """Line object with added fields, used by Totals and Spread."""

    event_id: str
    affiliate_id: int


class Moneyline(Line):
    """Moneyline object.

    Attributes may represent american, decimal, or fractional odds.

    Attributes:
        away_odds
        away_delta
        home_odds
        home_delta
    """

    # line_id: int
    # date_updated: str
    # format: str

    moneyline_away: Optional[int] = Field(...)
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
    """Point spread object.

    Attributes may represent american, decimal, or fractional odds.

    Attributes:
        away_spread
        away_spread_delta
        away_odds
        away_delta
        home_spread
        home_spread_delta
        home_odds
        home_delta
    """

    point_spread_away: Optional[float] = Field(...)
    point_spread_away_delta: Optional[float] = Field(...)
    point_spread_home: Optional[float] = Field(...)
    point_spread_home_delta: Optional[float] = Field(...)
    point_spread_away_money: Optional[int] = Field(...)
    point_spread_away_money_delta: Optional[int] = Field(...)
    point_spread_home_money: Optional[int] = Field(...)
    point_spread_home_money_delta: Optional[int] = Field(...)
    extended_spreads: List[SpreadElement] = []


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
    """Totals object.

    Attributes may represent american, decimal, or fractional odds.

    Attributes:
        over_odds
        over_delta
        under_odds
        under_delta
    """

    total_over: Optional[float] = Field(...)
    total_over_delta: Optional[float] = Field(...)
    total_under: Optional[float] = Field(...)
    total_under_delta: Optional[float] = Field(...)
    total_over_money: Optional[int] = Field(...)
    total_over_money_delta: Optional[int] = Field(...)
    total_under_money: Optional[int] = Field(...)
    total_under_money_delta: Optional[int] = Field(...)
    extended_totals: List[TotalElement] = []


class TotalPeriod(Total):
    period_id: int
    period_description: str


################################################################################
#  Alternative - abstract odds types and bet types into options. Allows handling
# arbitrary number of bet options / odds types.
################################################################################


# class DecimalOption:
#
#     Attributes:
#         odds
#         delta
#     """

#     pass


# class MoneylineOption:
#     """
#     Attributes:
#         name: Option name, eg 'away', 'draw' or 'home'
#         odds: One of DecimalOption, AmericanOption, or FractionalOption
#     """

#     pass


# class Moneyline:
#     """
#     Attributes:
#         options: Dict of options (Moneyline, Spread, or Total).
#     """

#     @property
#     def home_odds(self):
#         # Find the right value in the options dict.
#         pass

#     @property
#     def home_delta(self):
#         # Find the right value in the options dict.
#         pass

#     pass


# class MoneyLineTwoWay(Moneyline):
#     pass


# class MoneylineThreeWay(Moneyline):
#     @property
#     def draw_odds(self):
#         # Find the right value in the options dict.
#         pass

#     @property
#     def draw_delta(self):
#         # Find the right value in the options dict.
#         pass
