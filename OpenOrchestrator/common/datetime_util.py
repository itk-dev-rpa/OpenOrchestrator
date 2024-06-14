"""A module for performing common tasks regarding datetimes."""


from datetime import datetime


def format_datetime(datetime_: datetime | None, default: str = 'N/A') -> str:
    """Format a datetime to a string.

    Args:
        datetime_: The datetime to format.
        default: A default string to return if the datetime is None. Defaults to 'N/A'.

    Returns:
        A datetime string in the format %d-%m-%Y %H:%M:%S.
    """
    if not datetime_:
        return default

    return datetime_.strftime("%d-%m-%Y %H:%M:%S")
