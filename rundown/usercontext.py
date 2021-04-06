from contextvars import ContextVar
from contextlib import contextmanager

context_timezone = ContextVar("context_timezone")
context_odds_type = ContextVar("context_odds_type")


def set_context_var(var, val):
    if val is not None:
        return var.set(val)


def reset_context_var(var, val, token):
    if val is not None:
        return var.reset(token)


@contextmanager
def user_context(timezone=None, odds_type=None):
    token_timezone = set_context_var(context_timezone, timezone)
    token_odds_type = set_context_var(context_odds_type, odds_type)
    yield
    reset_context_var(context_timezone, timezone, token_timezone)
    reset_context_var(context_odds_type, odds_type, token_odds_type)
