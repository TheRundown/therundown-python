class Events:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def dates_by_sport(self, offset=0, format="date"):
        """GET /<sport-id>/dates

        Use Config class to return timezone-aware dates, or offset.

        Returns:
            list of Python datetime objects, or ints (if format=='epoch')
        """
        # TODO: should return different types or not? Could implement 2nd method for
        # epoch.
        pass

    def by_date(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/events/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def opening(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/openers/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def closing(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/closing/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def updated(self, last_id, include=None, sport_id=None):
        """GET /delta?last_id=<delta-last-id>

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.

        Raises:
            requests.HTTPError: If too many events have been updated since last_id.
        """
        pass

    def event(self, event_id, include=None):
        """GET /events/<event-id>

        Use Config class timezone with datetime object if both exist.

        Returns:
            resources.Events object.
        """
        pass
