"""Custom sqlalchemy Type for generating limited String objects"""

import math

from sqlalchemy import String, TypeDecorator


class LimitedLengthString(TypeDecorator):
    """Custom String type that automatically truncates its value on insert."""
    impl = String

    def process_bind_param(self, value, dialect):
        return _truncate_message(value)


def _truncate_message(message: str, max_length: int = 8000) -> str:
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
