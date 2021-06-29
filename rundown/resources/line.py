from typing import Union

from pydantic import BaseModel, validator, StrictInt, StrictFloat

from rundown.resources.validators import change_timezone, make_none_if_not_published

"""Module containing resources used by Rundown line methods and the Event resource."""


class Line(BaseModel):
    """Base line class holding information common to all line classes.

    attributes:
        line_id: Line ID
        date_updated: Date updated
        format: Odds type

    """

    line_id: int
    date_updated: str
    format: str

    _change_timezone = validator("date_updated", allow_reuse=True)(change_timezone)


class ExtendedLine(Line):
    """Line object with added fields, used by Totals and Spread. Inherits from Line.

    attributes:
        event_id: Event ID
        affiliate_id: Affiliate ID
    """

    event_id: str
    affiliate_id: int


class Moneyline(Line):
    """Class with attributes specific to moneyline bets. Inherits from Line.

    attributes:
        moneyline_away: Away team moneyline
        moneyline_away_delta: Change in odds compared to previous
        moneyline_home: Home team moneyline
        moneyline_home_delta: Change in odds compared to previous
        moneyline_draw: Draw moneyline
        moneyline_draw_delta: Change in odds compared to previous
    """

    moneyline_away: Union[StrictInt, StrictFloat] = None
    moneyline_away_delta: Union[StrictInt, StrictFloat] = None
    moneyline_home: Union[StrictInt, StrictFloat] = None
    moneyline_home_delta: Union[StrictInt, StrictFloat] = None
    moneyline_draw: Union[StrictInt, StrictFloat] = None
    moneyline_draw_delta: Union[StrictInt, StrictFloat] = None

    _make_none_if_not_published = validator(
        "moneyline_away",
        "moneyline_away_delta",
        "moneyline_home",
        "moneyline_home_delta",
        "moneyline_draw",
        "moneyline_draw_delta",
        allow_reuse=True,
    )(make_none_if_not_published)


class MoneylinePeriod(Moneyline):
    """Moneyline class for different periods / quarters / halves of a game. Inherits from MoneyLine.

    attributes:
        period_id: Period ID
        period_description: Period description
    """

    period_id: int
    period_description: str


class SpreadElement(BaseModel):
    """Class used by the extended_spread attribute of the Spread class for alternate spreads.

    attributes:
        affiliate_id: Affiliate ID
        point_spread_away: Away team point spread
        point_spread_away_delta: Change in odds compared to previous
        point_spread_home: Home team point spread
        point_spread_home_delta: Change in odds compared to previous
        point_spread_away_money: Away team odds
        point_spread_away_money_delta: Change in odds compared to previous
        point_spread_home_money: Home team odds
        point_spread_home_money_delta: Change in odds compared to previous
    """

    affiliate_id: int
    point_spread_away: Union[StrictInt, StrictFloat] = None
    point_spread_away_delta: Union[StrictInt, StrictFloat] = None
    point_spread_home: Union[StrictInt, StrictFloat] = None
    point_spread_home_delta: Union[StrictInt, StrictFloat] = None
    point_spread_away_money: Union[StrictInt, StrictFloat] = None
    point_spread_away_money_delta: Union[StrictInt, StrictFloat] = None
    point_spread_home_money: Union[StrictInt, StrictFloat] = None
    point_spread_home_money_delta: Union[StrictInt, StrictFloat] = None

    _make_none_if_not_published = validator(
        "point_spread_away",
        "point_spread_away_delta",
        "point_spread_home",
        "point_spread_home_delta",
        "point_spread_away_money",
        "point_spread_away_money_delta",
        "point_spread_home_money",
        "point_spread_home_money_delta",
        allow_reuse=True,
    )(make_none_if_not_published)


class Spread(ExtendedLine):
    """Class with attributes specific to spread bets. Includes alternate spreads. Inherits from ExtendedLine.

    attributes:
        point_spread_away: Away team point spread
        point_spread_away_delta: Change in odds compared to previous
        point_spread_home: Home team point spread
        point_spread_home_delta: Change in odds compared to previous
        point_spread_away_money: Away team odds
        point_spread_away_money_delta: Change in odds compared to previous
        point_spread_home_money: Home team odds
        point_spread_home_money_delta: Change in odds compared to previous
        extended_spreads: list of SpreadElement
    """

    point_spread_away: Union[StrictInt, StrictFloat] = None
    point_spread_away_delta: Union[StrictInt, StrictFloat] = None
    point_spread_home: Union[StrictInt, StrictFloat] = None
    point_spread_home_delta: Union[StrictInt, StrictFloat] = None
    point_spread_away_money: Union[StrictInt, StrictFloat] = None
    point_spread_away_money_delta: Union[StrictInt, StrictFloat] = None
    point_spread_home_money: Union[StrictInt, StrictFloat] = None
    point_spread_home_money_delta: Union[StrictInt, StrictFloat] = None
    extended_spreads: list[SpreadElement] = []

    _make_none_if_not_published = validator(
        "point_spread_away",
        "point_spread_away_delta",
        "point_spread_home",
        "point_spread_home_delta",
        "point_spread_away_money",
        "point_spread_away_money_delta",
        "point_spread_home_money",
        "point_spread_home_money_delta",
        allow_reuse=True,
    )(make_none_if_not_published)


class SpreadPeriod(Spread):
    """Spread class for different periods / quarters / halves of a game. Inherits from Spread.

    attributes:
        period_id: Period ID
        period_description: Period description
    """

    period_id: int
    period_description: str


class TotalElement(BaseModel):
    """Class used by the extended_total attribute of the Total class for alternate spreads.

    attributes:
        affiliate_id: Affiliate ID
        total_over: Over total
        total_over_delta: Change in odds compared to previous
        total_under: Under total
        total_under_delta: Change in odds compared to previous
        total_over_money: Over odds
        total_over_money_delta: Change in odds compared to previous
        total_under_money: Under odds
        total_under_money_delta: Change in odds compared to previous
    """

    affiliate_id: int
    total_over: Union[StrictInt, StrictFloat] = None
    total_over_delta: Union[StrictInt, StrictFloat] = None
    total_under: Union[StrictInt, StrictFloat] = None
    total_under_delta: Union[StrictInt, StrictFloat] = None
    total_over_money: Union[StrictInt, StrictFloat] = None
    total_over_money_delta: Union[StrictInt, StrictFloat] = None
    total_under_money: Union[StrictInt, StrictFloat] = None
    total_under_money_delta: Union[StrictInt, StrictFloat] = None

    _make_none_if_not_published = validator(
        "total_over",
        "total_over_delta",
        "total_under",
        "total_under_delta",
        "total_over_money",
        "total_over_money_delta",
        "total_under_money",
        "total_under_money_delta",
        allow_reuse=True,
    )(make_none_if_not_published)


class Total(ExtendedLine):
    """Class with attributes specific to total bets. Includes alternate totals. Inherits from ExtendedLine.

    attributes:
        total_over: Over total
        total_over_delta: Change in odds compared to previous
        total_under: Under total
        total_under_delta: Change in odds compared to previous
        total_over_money: Over odds
        total_over_money_delta: Change in odds compared to previous
        total_under_money: Under odds
        total_under_money_delta: Change in odds compared to previous
        extended_totals: list of TotalElement
    """

    total_over: Union[StrictInt, StrictFloat] = None
    total_over_delta: Union[StrictInt, StrictFloat] = None
    total_under: Union[StrictInt, StrictFloat] = None
    total_under_delta: Union[StrictInt, StrictFloat] = None
    total_over_money: Union[StrictInt, StrictFloat] = None
    total_over_money_delta: Union[StrictInt, StrictFloat] = None
    total_under_money: Union[StrictInt, StrictFloat] = None
    total_under_money_delta: Union[StrictInt, StrictFloat] = None
    extended_totals: list[TotalElement] = []

    _make_none_if_not_published = validator(
        "total_over",
        "total_over_delta",
        "total_under",
        "total_under_delta",
        "total_over_money",
        "total_over_money_delta",
        "total_under_money",
        "total_under_money_delta",
        allow_reuse=True,
    )(make_none_if_not_published)


class TotalPeriod(Total):
    """Total class for different periods / quarters / halves of a game. Inherits from Total.

    attributes:
        period_id: Period ID
        period_description: Period description
    """

    period_id: int
    period_description: str
