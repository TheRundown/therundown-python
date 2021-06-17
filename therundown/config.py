class Config:
    """Class defining configuration preferences

    Attributes:
        rapidapi_key: RapidAPI key.
        therundown_key: TheRundown API key.
        session: Python requests module session.

        odds_type: Preferred odds type, one of 'decimal', 'american' or 'fractional'.
        sportsbooks (list): Sportsbooks to return data for.
        timezone: User timezone, default to system timezone. Example format 'PST'
    """

    def __init__(self):
        """Create requests session and store config preferences."""
        pass
