"""This module defines ORM classes for logs"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class LogLevel(enum.Enum):
    """An enum representing the level of logs."""
    TRACE = "Trace"
    INFO = "Info"
    ERROR = "Error"


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
            "Log Time": datetime_util.format_datetime(self.log_time),
            "Level": self.log_level.value,
            "Process Name": self.process_name,
            "Message": self.log_message,
            "ID": str(self.id)
        }
