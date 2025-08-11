"""This module defines ORM classes for triggers."""

from datetime import datetime
import enum
from typing import Optional
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class TriggerStatus(enum.Enum):
    """An enum representing the status of trigger processes."""
    IDLE = "Idle"
    RUNNING = "Running"
    FAILED = "Failed"
    DONE = "Done"
    PAUSED = "Paused"
    PAUSING = "Pausing"


class TriggerType(enum.Enum):
    """An enum representing the type of triggers."""
    SINGLE = "Single"
    SCHEDULED = "Scheduled"
    QUEUE = "Queue"


class Trigger(Base):
    """A base class for all triggers in the ORM."""
    __tablename__ = "Triggers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trigger_name: Mapped[str] = mapped_column(String(100))
    process_name: Mapped[str] = mapped_column(String(100))
    last_run: Mapped[Optional[datetime]]
    process_path: Mapped[str] = mapped_column(String(250))
    process_args: Mapped[Optional[str]] = mapped_column(String(1000))
    process_status: Mapped[TriggerStatus] = mapped_column(default=TriggerStatus.IDLE)
    is_git_repo: Mapped[bool]
    is_blocking: Mapped[bool]
    scheduler_whitelist: Mapped[str] = mapped_column(String(250))
    priority: Mapped[int] = mapped_column(default=0)
    type: Mapped[TriggerType]

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_abstract": True
    }

    def __repr__(self) -> str:
        return f"{self.trigger_name}: {self.type.value}"

    def to_row_dict(self) -> dict[str, str]:
        """Convert trigger to a row dictionary for display in a table."""
        return {
            "Trigger Name": self.trigger_name,
            "Type": self.type.value,
            "Status": self.process_status.value,
            "Process Name": self.process_name,
            "Last Run": datetime_util.format_datetime(self.last_run, "Never"),
            "ID": str(self.id),
            "Priority": str(self.priority)
        }


class SingleTrigger(Trigger):
    """A class representing single trigger objects in the ORM."""
    __tablename__ = "Single_Triggers"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Triggers.id"), primary_key=True)
    next_run: Mapped[datetime]

    __mapper_args__ = {"polymorphic_identity": TriggerType.SINGLE}

    def to_row_dict(self) -> dict[str, str]:
        row_dict = super().to_row_dict()
        row_dict["Next Run"] = datetime_util.format_datetime(self.next_run)
        return row_dict


class ScheduledTrigger(Trigger):
    """A class representing scheduled trigger objects in the ORM."""
    __tablename__ = "Scheduled_Triggers"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Triggers.id"), primary_key=True)
    cron_expr: Mapped[str] = mapped_column(String(200))
    next_run: Mapped[datetime]

    __mapper_args__ = {"polymorphic_identity": TriggerType.SCHEDULED}

    def to_row_dict(self) -> dict[str, str]:
        row_dict = super().to_row_dict()
        row_dict["Next Run"] = datetime_util.format_datetime(self.next_run)
        return row_dict


class QueueTrigger(Trigger):
    """A class representing queue trigger objects in the ORM."""
    __tablename__ = "Queue_Triggers"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Triggers.id"), primary_key=True)
    queue_name: Mapped[str] = mapped_column(String(200))
    min_batch_size: Mapped[int]

    __mapper_args__ = {"polymorphic_identity": TriggerType.QUEUE}

    def to_row_dict(self) -> dict[str, str]:
        row_dict = super().to_row_dict()
        row_dict["Next Run"] = "N/A"
        return row_dict
