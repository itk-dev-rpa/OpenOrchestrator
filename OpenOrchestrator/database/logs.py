"""This module defines ORM classes for logs"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class LogLevel(enum.Enum):
    """An enum representing the level of logs."""
    TRACE = "Trace"
    INFO = "Info"
    ERROR = "Error"


class Base(DeclarativeBase):
    """SqlAlchemy base class for all ORM classes in this module."""


class Log(Base):
    """A class representing log objects in the ORM."""
    __tablename__ = "Logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    log_time: Mapped[datetime] = mapped_column(default=datetime.now)
    log_level: Mapped[LogLevel]
    process_name: Mapped[str] = mapped_column(String(100))
    log_message: Mapped[str] = mapped_column(String(8000))

    def to_row_dict(self) -> dict[str, str]:
        """Convert log to a row dictionary for display in a table."""
        return {
            "Log Time": self.log_time.strftime("%d-%m-%Y %H:%M:%S"),
            "Level": self.log_level.value,
            "Process Name": self.process_name,
            "Message": self.format_message(),
            "ID": str(self.id)
        }

    def format_message(self) -> str:
        """Format the log message to be shown in a table."""
        string = self.log_message

        if "\n" in string:
            string = repr(string)

        if len(self.log_message) > 120:
            string = string[:120] + "..."

        return string


def create_tables(engine: Engine):
    """Create all SQL tables related to ORM classes in this module.

    Args:
        engine: The SqlAlchemy connection engine used to create the tables.
    """
    Base.metadata.create_all(engine)
