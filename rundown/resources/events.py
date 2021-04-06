from typing import List, Union

from pydantic import BaseModel

from rundown.resources.event import Event, EventLinePeriods


class Meta(BaseModel):
    delta_last_id: str


class Events(BaseModel):
    """Class storing list of resources.Events + state for updating events list.

    Attributes:
        sport_id: Optional, required for delta endpoint call if initial Events creation
            was for a single sport.
        last_id: The delta last id to use for updating the events list.
        events: The events list.

    """

    meta: Meta
    events: List[Union[Event, EventLinePeriods]]

    # def update(self):
    #     """Use last_id to update the events list so all events are up to date."""
    #     pass
