from pathlib import Path

from rundown.utils import read_yaml


def build_sports_dict():
    """Build dictionary with key sport name and value sport ID.

    Used by Rundown methods for the purpose of getting sport ID from name, because the
    API expects ID.

    Returns:
        dict[str, int]: The dictionary.
    """
    alternate_names = {"NCAAF": 1, "UFC": 7, "MMA": 7, "NCAAB": 5}

    parent = Path(__file__).resolve().parent
    sports = read_yaml(parent / "sports.yaml")["sports"]
    sports_dict = {x["sport_name"]: x["sport_id"] for x in sports}
    sports_dict.update(alternate_names)
    return sports_dict


def build_sportsbook_dict():
    """Build dictionary with key sportsbook ID, value sportsbook name.

    Returns:
        dict[str, str]: The dictionary.
    """
    parent = Path(__file__).resolve().parent
    sportsbooks = read_yaml(parent / "sportsbooks.yaml")["affiliates"]
    # Pydantic expects string type key.
    sportsbook_dict = {
        str(el["affiliate_id"]): el["affiliate_name"] for el in sportsbooks
    }
    return sportsbook_dict


sportsbook_dict = build_sportsbook_dict()
