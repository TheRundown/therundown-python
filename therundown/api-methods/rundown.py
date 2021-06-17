from config import Config


class Rundown:
    """Class has all REST API endpoints available as methods.

    Advantages:
        - config class doesn't need to be added as argument to each endpoint.

    Attributes:
        config: Store user configuration preferences using Config class.
        _raw: The most recent JSON response.
    """

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self._raw = None

    def _get(self, url):
        """Make get request to the API.

        Returns:
            The JSON response from the API.
        """
        if not self.config:
            # use new request
            pass
        else:
            # use self.config.session
            pass

    def sports(self):
        """GET /sports

        Returns:
            list of resources.Sport
        """
        pass

    def dates_by_sport(self, offset=0, format="date"):
        """GET /<sport-id>/dates

        Use Config class to return timezone-aware dates, or offset.

        Returns:
            list of Python datetime objects, or ints (if format=='epoch')
        """
        # TODO: should return different types or not? Could implement 2nd method for
        # epoch.
        pass

    def affiliates(self):
        """GET /affiliates

        Returns:
            list of resources.Affiliate
        """
        pass

    ################################################################################
    # Potential optimization for events: use date range, make multiple calls.
    ################################################################################

    def events_by_date(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/events/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def opening_lines(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/openers/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def closing_lines(self, sport_id, date_, offset=0, include=None):
        """GET /sports/<sport-id>/closing/<date>

        Use Config class timezone with datetime object if both exist.

        Args:
            include (string, or list of string): Any of 'all_periods' and 'scores'.

        Returns:
            resources.Events object.
        """
        pass

    def events_delta(self, last_id, include=None, sport_id=None):
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

    def moneyline(self, line_id, include=None):
        """GET /lines/<line-id>/moneyline

        Returns:
            list of resources.Moneyline
        """
        pass

    def spread(self, line_id, include=None):
        """GET /lines/<line-id>/spread

        Returns:
            list of resources.Spread
        """
        pass

    def total(self, line_id, include=None):
        """GET /lines/<line-id>/total

        Returns:
            list of resources.Total
        """
        pass

    def schedule_by_sport(self, sport_id, from_=None):
        """GET /sports/<sport-id>/schedule

        Needs to handle pagination, so this method will result in multiple API calls.

        Args:
            from_: timezone-aware datetime object. 'from' is a reserved keyword in
            Python.

        Returns:
            list of resource.Event
        """
        # TODO: Should we have function calls that do multiple requests?
        pass

    def teams_by_sport(self, sport_id):
        """GET /sports/<sport-id>/teams

        Returns:
            list of resource.Team
        """
        pass
