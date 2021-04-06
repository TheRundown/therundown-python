import arrow

from rundown.usercontext import context_timezone


def change_timezone(dt_str):
    timezone = context_timezone.get()
    dt = arrow.get(dt_str)
    new_dt = dt.to(timezone)
    return str(new_dt)
