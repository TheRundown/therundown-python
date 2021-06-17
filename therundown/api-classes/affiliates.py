class Affiliates:
    def __init__(**kwargs):
        """GET /affiliates

        Returns:
            list of resources.Affiliate
        """
        super().__init__(**kwargs)
        # build URL and make call to self._get()