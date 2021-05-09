from typing import Union

from pydantic import BaseModel

from rundown.resources.event import Event, EventLinePeriods


class Meta(BaseModel):
    delta_last_id: str


class Events(BaseModel):
    meta: Meta
    events: list[Union[Event, EventLinePeriods]]
