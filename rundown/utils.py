import arrow


def utc_offset(timezone: str) -> int:
    """Get UTC offset in minutes for timezone.

    Args:
        timezone: Timezone string of form accepted by Arrow library.

    Returns:
        int: the UTC offset in minutes.
    """
    t_delta = arrow.now(timezone).utcoffset()
    return int(t_delta.days * 24 * 60 + t_delta.seconds / 60)
