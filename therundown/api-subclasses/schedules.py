class Schedule:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def by_sport(self, sport_id, from_=None):
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
