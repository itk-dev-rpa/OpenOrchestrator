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

    constant_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    constant_value: Mapped[str] = mapped_column(String(1000))
    change_date: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def as_tuple(self) -> tuple:
        """Convert the constant to a tuple of values.

        Returns:
            tuple: A tuple of all the triggers values.
        """
        return (self.constant_name, self.constant_value, self.change_date)


class Credential(Base):
    """A class representing a credential object in the ORM."""
    __tablename__ = "Credentials"

    credential_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    credential_username: Mapped[str] = mapped_column(String(250))
    credential_password: Mapped[str] = mapped_column(String(1000))
    change_date: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def as_tuple(self) -> tuple:
        """Convert the credential to a tuple of values.

        Returns:
            tuple: A tuple of all the triggers values.
        """
        return (
            self.credential_name,
            self.credential_username,
            self.credential_password,
            self.change_date
        )


def create_tables(engine: Engine):
    """Create all SQL tables related to ORM classes in this module.

    Args:
        engine: The SqlAlchemy connection engine used to create the tables.
    """
    Base.metadata.create_all(engine)
