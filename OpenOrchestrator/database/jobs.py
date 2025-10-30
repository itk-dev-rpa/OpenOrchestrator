"""This module defines ORM classes for jobs"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class JobStatus(enum.Enum):
    """An enum representing the level of logs."""
    RUNNING = "Running"
    DONE = "Done"
    FAILED = "Failed"
    KILLED = "Killed"


class Job(Base):
    """A class representing job objects in the ORM."""

    __tablename__ = "Jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    process_name: Mapped[str] = mapped_column(String(100))
    scheduler_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.RUNNING)
    start_time: Mapped[datetime] = mapped_column(default=datetime.now)
    end_time: Mapped[datetime] = mapped_column(default=None, nullable=True)

    def to_row_dict(self) -> dict[str, str]:
        """Convert log to a row dictionary for display in a table."""
        return {
            "ID": str(self.id),
            "Process Name": self.process_name,
            "Scheduler": self.scheduler_name,
            "Start Time":  datetime_util.format_datetime(self.start_time),
            "End Time":  datetime_util.format_datetime(self.end_time),
            "Status": self.status.value
        }
