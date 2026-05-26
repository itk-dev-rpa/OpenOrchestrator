"""Database access functions for triggers.

Covers single, scheduled, and queue triggers. Includes the polling
queries used by the Scheduler to find pending work.
"""

from datetime import datetime
from uuid import UUID

from cronsim import CronSim
from sqlalchemy import select
from sqlalchemy import func as alc_func
from sqlalchemy.orm import selectin_polymorphic

from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.exceptions import TriggerNotFoundError
from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from OpenOrchestrator.database.triggers import (
    Trigger,
    SingleTrigger,
    ScheduledTrigger,
    QueueTrigger,
    TriggerStatus,
)


def get_trigger(trigger_id: UUID | str) -> Trigger:
    """Get the trigger with the given id.

    Args:
        trigger_id: The id of the trigger.

    Returns:
        Trigger: The trigger with the given id.

    Raises:
        TriggerNotFoundError: If the trigger doesn't exist.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        query = (
            select(Trigger)
            .where(Trigger.id == trigger_id)
            .options(selectin_polymorphic(Trigger, (ScheduledTrigger, QueueTrigger, SingleTrigger)))
        )
        trigger = session.scalar(query)

    if not trigger:
        raise TriggerNotFoundError(f"No trigger with the given id: {trigger_id}")

    return trigger


def get_all_triggers() -> tuple[Trigger, ...]:
    """Get all triggers in the database."""
    with _get_session() as session:
        query = (
            select(Trigger)
            .options(selectin_polymorphic(Trigger, (ScheduledTrigger, QueueTrigger, SingleTrigger)))
        )
        return tuple(session.scalars(query))


def update_trigger(trigger: Trigger):
    """Updates an existing trigger in the database.

    Args:
        trigger: The trigger object with updated values.
    """
    with _get_session() as session:
        session.add(trigger)
        session.commit()
        session.refresh(trigger)


def get_scheduled_triggers() -> tuple[ScheduledTrigger, ...]:
    """Get all scheduled triggers from the database."""
    with _get_session() as session:
        query = select(ScheduledTrigger)
        result = session.scalars(query).all()
        return tuple(result)


def get_single_triggers() -> tuple[SingleTrigger, ...]:
    """Get all single triggers from the database."""
    with _get_session() as session:
        query = select(SingleTrigger)
        result = session.scalars(query).all()
        return tuple(result)


def get_queue_triggers() -> tuple[QueueTrigger, ...]:
    """Get all queue triggers from the database."""
    with _get_session() as session:
        query = select(QueueTrigger)
        result = session.scalars(query).all()
        return tuple(result)


def delete_trigger(trigger_id: UUID | str) -> None:
    """Delete the given trigger from the database.

    Args:
        trigger_id: The id of the trigger to delete.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        trigger = get_trigger(trigger_id)
        session.delete(trigger)
        session.commit()


# pylint: disable=too-many-positional-arguments
def create_single_trigger(trigger_name: str, process_name: str, next_run: datetime,
                          process_path: str, process_args: str, is_git_repo: bool, is_blocking: bool,
                          priority: int, scheduler_whitelist: list[str] | None = None, git_branch: str | None = None) -> UUID:
    """Create a new single trigger in the database.

    Args:
        trigger_name: The name of the trigger.
        process_name: The process name.
        next_run: The datetime when the trigger should run.
        process_path: The path of the process.
        process_args: The argument string of the process.
        is_git_repo: If the process_path points to a git repo.
        is_blocking: If the process should be blocking.
        priority: The integer priority of the trigger.
        scheduler_whitelist: A list of names of schedulers the trigger may run on.
        git_branch: The specific git branch of the trigger.

    Returns:
        The id of the trigger that was created.
    """
    with _get_session() as session:
        trigger = SingleTrigger(
            trigger_name=trigger_name,
            process_name=process_name,
            process_path=process_path,
            process_args=process_args,
            is_git_repo=is_git_repo,
            is_blocking=is_blocking,
            next_run=next_run,
            priority=priority,
            scheduler_whitelist=scheduler_whitelist,
            git_branch=git_branch,
        )
        session.add(trigger)
        session.commit()
        return trigger.id


# pylint: disable=too-many-positional-arguments
def create_scheduled_trigger(trigger_name: str, process_name: str, cron_expr: str, next_run: datetime,
                             process_path: str, process_args: str, is_git_repo: bool,
                             is_blocking: bool, priority: int, scheduler_whitelist: list[str] | None = None,
                             git_branch: str | None = None) -> UUID:
    """Create a new scheduled trigger in the database.

    Args:
        trigger_name: The name of the trigger.
        process_name: The process name.
        cron_expr: The cron expression of the trigger.
        next_run: The date to first run the trigger.
        process_path: The path of the process.
        process_args: The argument string of the process.
        is_git_repo: If the process_path points to a git repo.
        is_blocking: If the process should be blocking.
        priority: The integer priority of the trigger.
        scheduler_whitelist: A list of names of schedulers the trigger may run on.
        git_branch: The specific git branch of the trigger.

    Returns:
        The id of the trigger that was created.
    """
    with _get_session() as session:
        trigger = ScheduledTrigger(
            trigger_name=trigger_name,
            process_name=process_name,
            process_path=process_path,
            process_args=process_args,
            is_git_repo=is_git_repo,
            is_blocking=is_blocking,
            next_run=next_run,
            cron_expr=cron_expr,
            priority=priority,
            scheduler_whitelist=scheduler_whitelist,
            git_branch=git_branch,
        )
        session.add(trigger)
        session.commit()
        return trigger.id


# pylint: disable=too-many-positional-arguments
def create_queue_trigger(trigger_name: str, process_name: str, queue_name: str, process_path: str,
                         process_args: str, is_git_repo: bool, is_blocking: bool,
                         min_batch_size: int, priority: int, scheduler_whitelist: list[str] | None = None,
                         git_branch: str | None = None) -> UUID:
    """Create a new queue trigger in the database.

    Args:
        trigger_name: The name of the trigger.
        process_name: The process name.
        queue_name: The name of the queue.
        process_path: The path of the process.
        process_args: The argument string of the process.
        is_git_repo: The is_git value of the process.
        is_blocking: The is_blocking value of the process.
        min_batch_size: The minimum number of queue elements before triggering.
        priority: The integer priority of the trigger.
        scheduler_whitelist: A list of names of schedulers the trigger may run on.
        git_branch: The specific git branch of the trigger.

    Returns:
        The id of the trigger that was created.
    """
    with _get_session() as session:
        trigger = QueueTrigger(
            trigger_name=trigger_name,
            process_name=process_name,
            process_path=process_path,
            process_args=process_args,
            is_git_repo=is_git_repo,
            is_blocking=is_blocking,
            queue_name=queue_name,
            min_batch_size=min_batch_size,
            priority=priority,
            scheduler_whitelist=scheduler_whitelist,
            git_branch=git_branch,
        )
        session.add(trigger)
        session.commit()
        return trigger.id


def begin_single_trigger(trigger_id: UUID | str) -> bool:
    """Set the status of a single trigger to 'running' and set the last run time.

    Args:
        trigger_id: The id of the trigger to begin.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        trigger = session.get(SingleTrigger, trigger_id)

        if not trigger:
            raise TriggerNotFoundError("No trigger with the given id was found.")

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()

        session.commit()
        return True


def get_pending_single_triggers() -> list[SingleTrigger]:
    """Get all single triggers that are ready to run."""
    with _get_session() as session:
        query = (
            select(SingleTrigger)
            .where(SingleTrigger.process_status == TriggerStatus.IDLE)
            .where(SingleTrigger.next_run <= datetime.now())
            .order_by(SingleTrigger.next_run)
        )
        return list(session.scalars(query))


def get_pending_scheduled_triggers() -> list[ScheduledTrigger]:
    """Get all scheduled triggers that are ready to run."""
    with _get_session() as session:
        query = (
            select(ScheduledTrigger)
            .where(ScheduledTrigger.process_status == TriggerStatus.IDLE)
            .where(ScheduledTrigger.next_run <= datetime.now())
            .order_by(ScheduledTrigger.next_run)
        )
        return list(session.scalars(query))


def begin_scheduled_trigger(trigger_id: UUID | str) -> bool:
    """Set the status of a scheduled trigger to 'running' and advance ``next_run``.

    Args:
        trigger_id: The id of the trigger to begin.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        trigger = session.get(ScheduledTrigger, trigger_id)

        if not trigger:
            raise TriggerNotFoundError("No trigger with the given id was found.")

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()
        trigger.next_run = next(CronSim(trigger.cron_expr, datetime.now()))

        session.commit()
        return True


def get_pending_queue_triggers() -> list[QueueTrigger]:
    """Get all queue triggers that are ready to run."""
    with _get_session() as session:
        sub_query = (
            select(alc_func.count())  # pylint: disable=not-callable
            .where(QueueElement.queue_name == QueueTrigger.queue_name)
            .where(QueueElement.status == QueueStatus.NEW)
            .scalar_subquery()
        )

        query = (
            select(QueueTrigger)
            .where(QueueTrigger.process_status == TriggerStatus.IDLE)
            .where(sub_query >= QueueTrigger.min_batch_size)
        )
        return list(session.scalars(query))


def begin_queue_trigger(trigger_id: UUID | str) -> bool:
    """Set the status of a queue trigger to 'running' and set the last run time.

    Args:
        trigger_id: The id of the trigger to begin.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        trigger = session.get(QueueTrigger, trigger_id)

        if not trigger:
            raise TriggerNotFoundError("No trigger with the given id was found.")

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()

        session.commit()
        return True


def set_trigger_status(trigger_id: UUID | str, status: TriggerStatus) -> None:
    """Set the status of a trigger.

    Args:
        trigger_id: The id of the trigger.
        status: The new status of the trigger.
    """
    if isinstance(trigger_id, str):
        trigger_id = UUID(trigger_id)

    with _get_session() as session:
        trigger = session.get(Trigger, trigger_id)

        if not trigger:
            raise TriggerNotFoundError("No trigger with the given id was found.")

        trigger.process_status = status
        session.commit()
