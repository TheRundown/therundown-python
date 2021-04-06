from contextvars import ContextVar
from contextlib import contextmanager

context_timezone = ContextVar("context_timezone")


def set_context_var(var, val):
    if val is not None:
        return var.set(val)


def reset_context_var(var, val, token):
    if val is not None:
        return var.reset(token)


@contextmanager
def user_context(timezone=None, odds_type=None):
    token_timezone = set_context_var(context_timezone, timezone)
    yield
    reset_context_var(context_timezone, timezone, token_timezone)
