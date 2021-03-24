class Line:
    """Base class for different line types.

    Attributes:
        date_updated: Timezone-aware datetime object.
        format: 'American', 'Decimal' or 'Fractional'.
        line_id: The line id.
    """

    def __init__(self):

        pass


# TODO: Is it bad to have odds being different data types (float or int) / representing
# different meanings (fractional, decimal, or american) based on odds type?


class Moneyline:
    """Moneyline object.

    Attributes may represent american, decimal, or fractional odds.

    Attributes:
        away_odds
        away_delta
        home_odds
        home_delta
    """

    pass


class Spread:
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

    pass


class Totals:
    """Totals object.

    Attributes may represent american, decimal, or fractional odds.

    Attributes:
        over_odds
        over_delta
        under_odds
        under_delta
    """

    pass


################################################################################
#  Alternative - abstract odds types and bet types into options. Allows handling
# arbitrary number of bet options / odds types.
################################################################################


class DecimalOption:
    """
    Attributes:
        odds
        delta
    """

    pass


class MoneylineOption:
    """
    Attributes:
        name: Option name, eg 'away', 'draw' or 'home'
        odds: One of DecimalOption, AmericanOption, or FractionalOption
    """

    pass


class Moneyline:
    """
    Attributes:
        options: Dict of options (Moneyline, Spread, or Total).
    """

    @property
    def home_odds(self):
        # Find the right value in the options dict.
        pass

    @property
    def home_delta(self):
        # Find the right value in the options dict.
        pass

    pass


class MoneyLineTwoWay(Moneyline):
    pass


class MoneylineThreeWay(Moneyline):
    @property
    def draw_odds(self):
        # Find the right value in the options dict.
        pass

    @property
    def draw_delta(self):
        # Find the right value in the options dict.
        pass
