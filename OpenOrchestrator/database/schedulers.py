"""Module for the Scheduler ORM class"""

from datetime import datetime

from sqlalchemy import String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from OpenOrchestrator.common import datetime_util


class Base(DeclarativeBase):
    """Base class for other classes in this module"""


class Scheduler(Base):
    """Class containing the ORM model for schedulers"""
    __tablename__ = "Scheduler"

    computer_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    last_update: Mapped[datetime] = mapped_column(onupdate=datetime.now, default=datetime.now)
    latest_trigger: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    last_trigger_start: Mapped[datetime] = mapped_column(nullable=True, default=None)

    def to_row_dict(self) -> dict[str, str]:
        """Convert scheduler to a row dictionary for display in a table."""
        return {
            "Credential Name": self.computer_name,
            "Last Update": datetime_util.format_datetime(self.last_update),
            "Latest Trigger": self.latest_trigger if self.latest_trigger else "None",
            "Last Trigger Start": datetime_util.format_datetime(self.last_trigger_start) if self.last_trigger_start else "None"
        }


def create_tables(engine: Engine):
    """Create all SQL tables related to ORM classes in this module.

    Args:
        engine: The SqlAlchemy connection engine used to create the tables.
    """
    Base.metadata.create_all(engine)
