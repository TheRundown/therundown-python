class Team:
    """Team object. 'normalized_teams' maps to this object.

    Attributes:
        abbreviation
        mascot
        name
        record
        team_id
    """

    pass


class EventTeam(Team):
    """Team object within event context.

    Attributes:
        is_home
        is_away
    """

    # TODO: could consolidate into single boolean.
    pass
