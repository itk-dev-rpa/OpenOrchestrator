"""Module for the Scheduler ORM class"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.database.base import Base

# All classes in this module are effectively dataclasses without methods.
# pylint: disable=too-few-public-methods


class Scheduler(Base):
    """Class containing the ORM model for schedulers"""
    __tablename__ = "Schedulers"

    machine_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    last_update: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)
    latest_trigger: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    latest_trigger_time: Mapped[Optional[datetime]] = mapped_column(nullable=True, default=None)

    def to_row_dict(self) -> dict[str, str]:
        """Convert scheduler to a row dictionary for display in a table."""
        return {
            "Machine Name": self.machine_name,
            "Last Connection": datetime_util.format_datetime(self.last_update),
            "Latest Trigger": self.latest_trigger if self.latest_trigger else "None yet",
            "Latest Trigger Time": datetime_util.format_datetime(self.latest_trigger_time) if self.latest_trigger_time else ""
        }
