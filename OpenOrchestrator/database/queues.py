from datetime import datetime
import enum
from typing import Optional
import uuid

from sqlalchemy import String, Engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

class QueueStatus(enum.Enum):
    NEW = 'New'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'
    FAILED = 'Failed'


class Base(DeclarativeBase):
    """SqlAlchemy base class for all ORM classes in this module."""


class QueueElement(Base):
    __tablename__ = "Queues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    queue_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[QueueStatus] = mapped_column(default=QueueStatus.NEW)
    data: Mapped[Optional[str]] = mapped_column(String(2000))
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    created_date: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
    start_date: Mapped[Optional[datetime]]
    end_date: Mapped[Optional[datetime]]
    Message: Mapped[Optional[str]] = mapped_column(String(1000))
    created_by: Mapped[Optional[str]] = mapped_column(String(100))


def create_tables(engine: Engine):
    """Create all SQL tables related to ORM classes in this module.

    Args:
        engine: The SqlAlchemy connection engine used to create the tables.
    """
    Base.metadata.create_all(engine)
