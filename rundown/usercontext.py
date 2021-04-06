from contextvars import ContextVar
from contextlib import contextmanager

context_timezone = ContextVar("context_timezone")


@contextmanager
def user_context(timezone: str):
    """Context manager used by Rundown in order to pass state to Pydantic validators.

    Args:
        timezone: A timezone string.
    """
    token_timezone = context_timezone.set(timezone)
    yield
    context_timezone.reset(token_timezone)
