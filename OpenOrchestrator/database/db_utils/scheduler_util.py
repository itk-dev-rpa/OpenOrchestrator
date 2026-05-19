"""Database access functions for Scheduler heartbeats.

A row in the Schedulers table represents a running Scheduler instance,
keyed by its machine name. The Scheduler updates ``last_update`` on
every poll and records the most recently launched trigger.
"""

from datetime import datetime

from sqlalchemy import select

from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.schedulers import Scheduler


def get_schedulers() -> tuple[Scheduler, ...]:
    """Get all Scheduler heartbeat rows from the database."""
    with _get_session() as session:
        query = select(Scheduler).order_by(Scheduler.machine_name)
        result = session.scalars(query).all()
        return tuple(result)


def send_ping_from_scheduler(machine_name: str) -> None:
    """Update (or insert) the heartbeat row for a running Scheduler.

    Args:
        machine_name: The machine pinging the Orchestrator.
    """
    with _get_session() as session:
        scheduler = session.get(Scheduler, machine_name)

        if scheduler:
            scheduler.last_update = datetime.now()
        else:
            scheduler = Scheduler(machine_name=machine_name, last_update=datetime.now())
            session.add(scheduler)

        session.commit()


def start_trigger_from_machine(machine_name: str, trigger_name: str) -> None:
    """Record that a Scheduler launched a trigger; updates the heartbeat row.

    Args:
        machine_name: The machine starting the trigger.
        trigger_name: The trigger being started on the machine.
    """
    with _get_session() as session:
        scheduler = session.get(Scheduler, machine_name)
        now = datetime.now()

        if scheduler:
            scheduler.last_update = now
            scheduler.latest_trigger = trigger_name
            scheduler.latest_trigger_time = now
        else:
            scheduler = Scheduler(
                machine_name=machine_name,
                last_update=now,
                latest_trigger=trigger_name,
                latest_trigger_time=now,
            )
            session.add(scheduler)

        session.commit()
