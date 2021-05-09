from rundown.static.sports import build_sports_dict, sports


def test_build_sports_dict():
    s_dict = build_sports_dict()
    for s in sports:
        names = [s["sport_name"]]
        if "sport_alt_names" in s:
            names += s["sport_alt_names"]
    for n in names:
        assert n in s_dict