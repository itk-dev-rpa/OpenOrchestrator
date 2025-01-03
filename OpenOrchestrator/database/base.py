"""Contains the Base class for all ORM classes"""

from sqlalchemy.orm import DeclarativeBase


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """SqlAlchemy base class for all ORM classes in this project."""
