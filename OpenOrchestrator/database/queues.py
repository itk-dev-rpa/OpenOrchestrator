"""This module defines ORM classes for queue elements."""

from datetime import datetime
import enum
from typing import Optional
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class QueueStatus(enum.Enum):
    """An enum representing the status of a queue element."""
    NEW = 'New'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'
    FAILED = 'Failed'
    ABANDONED = 'Abandoned'


class QueueElement(Base):
    """A class representing a queue element in the ORM."""
    __tablename__ = "Queues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    queue_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[QueueStatus] = mapped_column(default=QueueStatus.NEW)
    data: Mapped[Optional[str]] = mapped_column(String(2000))
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    created_date: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
    start_date: Mapped[Optional[datetime]]
    end_date: Mapped[Optional[datetime]]
    message: Mapped[Optional[str]] = mapped_column(String(1000))
    created_by: Mapped[Optional[str]] = mapped_column(String(100))

    def to_row_dict(self) -> dict:
        """Convert the object to a dict for display in a table."""
        return {
            "ID": self.id,
            "Reference": self.reference,
            "Status": self.status,
            "Data": self.data,
            "Created Date": datetime_util.format_datetime(self.created_date),
            "Start Date": datetime_util.format_datetime(self.start_date),
            "End Date": datetime_util.format_datetime(self.end_date),
            "Message": self.message,
            "Created By": self.created_by
        }
