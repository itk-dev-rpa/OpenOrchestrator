"""This module defines ORM classes for constants and credentials."""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class Constant(Base):
    """A class representing a constant object in the ORM."""
    __tablename__ = "Constants"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000))
    changed_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def to_row_dict(self) -> dict[str, str]:
        """Convert constant to a row dictionary for display in a table."""
        return {
            "Constant Name": self.name,
            "Value": self.value,
            "Last Changed": datetime_util.format_datetime(self.changed_at)
        }


class Credential(Base):
    """A class representing a credential object in the ORM."""
    __tablename__ = "Credentials"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    username: Mapped[str] = mapped_column(String(250))
    password: Mapped[str] = mapped_column(String(1000))
    changed_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)

    def to_row_dict(self) -> dict[str, str]:
        """Convert credential to a row dictionary for display in a table."""
        return {
            "Credential Name": self.name,
            "Username": self.username,
            "Password": self.format_password(),
            "Last Changed": datetime_util.format_datetime(self.changed_at)
        }

    def format_password(self) -> str:
        """Format the password to be shown in a table."""
        length = len(self.password)
        lower_length = int(((length-100)/20)*16)
        upper_length = lower_length + 15
        return f"{length} encrypted bytes. {lower_length}-{upper_length} decrypted bytes."
