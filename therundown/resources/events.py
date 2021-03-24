class Events:
    """Class storing list of resources.Events + state for updating events list.

    Attributes:
        sport_id: Optional, required for delta endpoint call if initial Events creation
            was for a single sport.
        last_id: The delta last id to use for updating the events list.
        events: The events list.

    """

    def update(self):
        """Use last_id to update the events list so all events are up to date."""
        pass
