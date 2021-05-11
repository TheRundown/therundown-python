from pydantic import BaseModel

from rundown.resources.event import Event


class Meta(BaseModel):
    delta_last_id: str


class Events(BaseModel):
    meta: Meta
    events: list[Event]
