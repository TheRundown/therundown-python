import arrow

from rundown.usercontext import context_timezone, context_odds_type
from rundown.utils import american_to_decimal


def change_timezone(dt_str):
    timezone = context_timezone.get()
    dt = arrow.get(dt_str)
    new_dt = dt.to(timezone)
    return str(new_dt)


def odds(o):
    odds_type = context_odds_type.get()
    if odds_type == "american":
        return o
    else:
        return american_to_decimal(o)
