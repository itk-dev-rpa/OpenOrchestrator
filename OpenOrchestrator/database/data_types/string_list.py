"""This module contains a type decorator class for use in ORM models."""

import json

from sqlalchemy import Dialect, types


# pylint: disable=too-many-ancestors, abstract-method
class StringList(types.TypeDecorator):
    """A type decorator used when defining sqlalchemy columns.
    This type converts a list of strings to a json string before sending to the database.
    """
    impl = types.String
    cache_ok = True

    # pylint: disable=unused-argument
    def process_bind_param(self, value: list[str] | None, dialect: Dialect) -> str | None:
        """Convert to json string before writing to the database."""
        if value is not None:
            return json.dumps(value)

        return None

    # pylint: disable=unused-argument
    def process_result_value(self, value: str | None, dialect: Dialect) -> list[str] | None:
        """Convert from json string when retrieving from the database."""
        if value is not None:
            return json.loads(value)

        return None
