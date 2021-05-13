"""Module for static sports information used by Rundown."""

sports = [
    {"sport_id": 1, "sport_name": "NCAA Football", "sport_alt_names": ["NCAAF"]},
    {"sport_id": 2, "sport_name": "NFL"},
    {"sport_id": 3, "sport_name": "MLB"},
    {"sport_id": 4, "sport_name": "NBA"},
    {
        "sport_id": 5,
        "sport_name": "NCAA Men's Basketball",
        "sport_alt_names": ["NCAAB"],
    },
    {"sport_id": 6, "sport_name": "NHL"},
    {"sport_id": 7, "sport_name": "UFC/MMA", "sport_alt_names": ["UFC", "MMA"]},
    {"sport_id": 8, "sport_name": "WNBA"},
    {"sport_id": 9, "sport_name": "CFL"},
    {"sport_id": 10, "sport_name": "MLS"},
]
"""list[dict]: List of sports supported by Rundown API.

'sport_id' and 'sport_name' are from the Rundown API. 'sport_alt_names' defines other
names that the user might try to identify a sport / league with.
"""


def build_sports_dict():
    """Build dictionary with key sport name and value sport ID.

    Used by Rundown methods for the purpose of getting sport ID from name, because the
    API expects ID.

    Returns:
        dict[str, int]: The dictionary.
    """
    sports_dict = {}
    for s in sports:
        names = [s["sport_name"]]
        if "sport_alt_names" in s:
            names += s["sport_alt_names"]
        for name in names:
            sports_dict[name.lower()] = s["sport_id"]

    return sports_dict
