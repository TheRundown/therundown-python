"""Module for static sportsbook information used by Rundown."""

sportsbooks = [
    {
        "affiliate_id": 1,
        "affiliate_name": "5Dimes",
    },
    {
        "affiliate_id": 3,
        "affiliate_name": "Pinnacle",
    },
    {
        "affiliate_id": 16,
        "affiliate_name": "Matchbook",
    },
    {
        "affiliate_id": 19,
        "affiliate_name": "Draftkings",
    },
    {
        "affiliate_id": 6,
        "affiliate_name": "BetOnline",
    },
    {
        "affiliate_id": 20,
        "affiliate_name": "Pointsbet",
    },
    {
        "affiliate_id": 2,
        "affiliate_name": "Bovada",
    },
    {
        "affiliate_id": 7,
        "affiliate_name": "Bookmaker",
    },
    {
        "affiliate_id": 11,
        "affiliate_name": "LowVig",
    },
    {
        "affiliate_id": 10,
        "affiliate_name": "JustBet",
    },
    {
        "affiliate_id": 4,
        "affiliate_name": "SportsBetting",
    },
    {
        "affiliate_id": 9,
        "affiliate_name": "betcris",
    },
    {
        "affiliate_id": 15,
        "affiliate_name": "TigerGaming",
    },
    {
        "affiliate_id": 14,
        "affiliate_name": "Intertops",
    },
    {
        "affiliate_id": 12,
        "affiliate_name": "Bodog",
    },
    {
        "affiliate_id": 18,
        "affiliate_name": "YouWager",
    },
    {
        "affiliate_id": 17,
        "affiliate_name": "RedZone",
    },
    # Unibet and BetMGM are returned from event routes, but aren't present in the JSON
    # returned by the sportsbooks route, so they were manually added.
    {
        "affiliate_id": 21,
        "affiliate_name": "Unibet",
    },
    {
        "affiliate_id": 22,
        "affiliate_name": "BetMGM",
    },
]
"""list[dict]: List of sports supported by Rundown API."""


def build_sportsbook_dict():
    """Build dictionary with key sportsbook ID, value sportsbook name.

    Returns:
        dict[str, str]: The dictionary.
    """
    # Pydantic expects string type key.
    sportsbook_dict = {
        str(el["affiliate_id"]): el["affiliate_name"] for el in sportsbooks
    }
    return sportsbook_dict


sportsbook_dict = build_sportsbook_dict()
"""dict[str, str]: Dict from sportsbook ID to name used by resources.Events sportsbook
validator.
"""
