"""Contains the Base class for all ORM classes"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SqlAlchemy base class for all ORM classes in this project."""
