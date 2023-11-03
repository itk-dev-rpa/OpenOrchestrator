"""This module defines ORM classes for constants and credentials."""

from datetime import datetime

from sqlalchemy import String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods

class Base(DeclarativeBase):
    """SqlAlchemy base class for all ORM classes in this module."""


class Constant(Base):
    """A class representing a constant object in the ORM."""
    __tablename__ = "Constants"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000))
    changed_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def as_tuple(self) -> tuple:
        """Convert the constant to a tuple of values.

        Returns:
            tuple: A tuple of all the triggers values.
        """
        return (self.name, self.value, self.changed_at)


class Credential(Base):
    """A class representing a credential object in the ORM."""
    __tablename__ = "Credentials"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    username: Mapped[str] = mapped_column(String(250))
    password: Mapped[str] = mapped_column(String(1000))
    changed_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def as_tuple(self) -> tuple:
        """Convert the credential to a tuple of values.

        Returns:
            tuple: A tuple of all the triggers values.
        """
        return (
            self.name,
            self.username,
            self.password,
            self.changed_at
        )


def create_tables(engine: Engine):
    """Create all SQL tables related to ORM classes in this module.

    Args:
        engine: The SqlAlchemy connection engine used to create the tables.
    """
    Base.metadata.create_all(engine)
