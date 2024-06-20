"""Module for truncating a string by removing the middle part."""

import math


def truncate_message(message: str, max_length: int = 8000) -> str:
    """Truncate a message to max_length characters

    Args:
        message: The string to truncate
        max_length: Maximum allowed length, defaults to 8000

    Returns:
        A string with length set to max_length
    """
    if len(message) <= max_length:
        return message
    return message[:math.ceil(max_length/2)] + message[-math.floor(max_length/2):]
