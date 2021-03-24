from config import Config


class Lines:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
