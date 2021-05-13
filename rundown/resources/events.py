from pydantic import BaseModel

from rundown.resources.event import Event

"""Module for resources used by Rundown events methods."""


class Meta(BaseModel):
    """Meta contains delta_last_id, which is used by Rundown.events_delta."""

    delta_last_id: str


class Events(BaseModel):
    """Class holding a list of Event resources. Used by Rundown events methods."""

    meta: Meta
    events: list[Event]
