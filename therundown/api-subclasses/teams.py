from config import Config


class Teams:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def teams(self, sport_id):
        """GET /sports/<sport-id>/teams

        Returns:
            list of resource.Team
        """
        pass
