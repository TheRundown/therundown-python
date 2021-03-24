class EventsByDate:
    def __init__(self, sport_id, date_, offset=0, include=None, **kwargs):
        """GET /sports/<sport-id>/events/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        super().__init__(**kwargs)
        # build URL and make call to self._get()
