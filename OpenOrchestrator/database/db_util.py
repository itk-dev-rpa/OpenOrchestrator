"""This module handles the connection to the database in OpenOrchestrator."""

from datetime import datetime
from typing import Callable, TypeVar, ParamSpec

from croniter import croniter
from sqlalchemy import Engine, create_engine, select, insert, desc
from sqlalchemy import exc as alc_exc
from sqlalchemy import func as alc_func
from sqlalchemy.orm import Session, selectin_polymorphic
from nicegui import ui

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import logs, triggers, constants, queues
from OpenOrchestrator.database.logs import Log, LogLevel
from OpenOrchestrator.database.constants import Constant, Credential
from OpenOrchestrator.database.triggers import Trigger, SingleTrigger, ScheduledTrigger, QueueTrigger, TriggerStatus
from OpenOrchestrator.database.queues import QueueElement, QueueStatus

# Type hint helpers for decorators
T = TypeVar("T")
P = ParamSpec("P")

_connection_engine: Engine = None


def connect(conn_string: str) -> bool:
    """Connects to the database using the given connection string.

    Args:
        conn_string: The connection string.

    Returns:
        bool: True if successful.
    """
    global _connection_engine  # pylint: disable=global-statement

    try:
        engine = create_engine(conn_string)
        engine.connect()
        _connection_engine = engine
        return True
    except (alc_exc.InterfaceError, alc_exc.ArgumentError, alc_exc.OperationalError) as exc:
        _connection_engine = None
        ui.notify(str(exc), type='negative', timeout=0, close_button="Dismiss")

    return False


def disconnect() -> None:
    """Disconnect from the database."""
    global _connection_engine  # pylint: disable=global-statement
    _connection_engine.dispose()
    _connection_engine = None


def catch_db_error(func: Callable[P, T]) -> Callable[P, T]:
    """A decorator that catches errors in SQL calls."""
    def inner(*args, **kwargs) -> T:
        if _connection_engine is None:
            ui.notify("Not connected", type='negative')
            return None

        try:
            return func(*args, **kwargs)
        except alc_exc.ProgrammingError as exc:
            ui.notify(f"Query failed:\n{exc}", type='negative', timeout=0, close_button="Dismiss")

        return None

    return inner


def get_conn_string() -> str:
    """Get the connection string.

    Returns:
        str: The connection string if any.
    """
    try:
        return str(_connection_engine.url)
    except AttributeError:
        pass

    return None


@catch_db_error
def initialize_database() -> None:
    """Initializes the database with all the needed tables."""
    logs.create_tables(_connection_engine)
    triggers.create_tables(_connection_engine)
    constants.create_tables(_connection_engine)
    queues.create_tables(_connection_engine)
    ui.notify("Database has been initialized!", type='positive')


@catch_db_error
def get_trigger(trigger_id: str) -> Trigger:
    """Get the trigger with the given id.

    Args:
        trigger_id: The id of the trigger.

    Returns:
        Trigger: The trigger with the given id.
    """
    with Session(_connection_engine) as session:
        query = (
            select(Trigger)
            .where(Trigger.id == trigger_id)
            .options(selectin_polymorphic(Trigger, (ScheduledTrigger, QueueTrigger, SingleTrigger)))
        )
        return session.scalar(query)


@catch_db_error
def get_all_triggers() -> tuple[Trigger]:
    """Get all triggers in the database.

    Returns:
        A tuple of Trigger objects.
    """
    with Session(_connection_engine) as session:
        query = (
            select(Trigger)
            .options(selectin_polymorphic(Trigger, (ScheduledTrigger, QueueTrigger, SingleTrigger)))
        )
        return tuple(session.scalars(query))


@catch_db_error
def update_trigger(trigger: Trigger):
    """Updates an existing trigger in the database.

    Args:
        trigger: The trigger object with updated values.
    """
    with Session(_connection_engine) as session:
        session.add(trigger)
        session.commit()
        session.refresh(trigger)


@catch_db_error
def get_scheduled_triggers() -> tuple[ScheduledTrigger]:
    """Get all scheduled triggers from the database.

    Returns:
        tuple[ScheduledTrigger]: A list of all scheduled triggers in the database.
    """
    with Session(_connection_engine) as session:
        query = select(ScheduledTrigger)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def get_single_triggers() -> tuple[SingleTrigger]:
    """Get all single triggers from the database.

    Returns:
        tuple[SingleTrigger]: A list of all single triggers in the database.
    """
    with Session(_connection_engine) as session:
        query = select(SingleTrigger)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def get_queue_triggers() -> tuple[QueueTrigger]:
    """Get all queue triggers from the database.

    Returns:
        tuple[QueueTrigger]: A list of all queue triggers in the database.
    """
    with Session(_connection_engine) as session:
        query = select(QueueTrigger)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def delete_trigger(trigger_id: str) -> None:
    """Delete the given trigger from the database.

    Args:
        trigger_id: The id of the trigger to delete.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(Trigger, trigger_id)
        session.delete(trigger)
        session.commit()


@catch_db_error
def get_logs(offset: int, limit: int,
             from_date: datetime = None, to_date: datetime = None,
             process_name: str = None, log_level: LogLevel = None) -> tuple[Log]:
    """Get the logs from the database using filters and pagination.

    Args:
        offset: The index of the first log to get.
        limit: The number of logs to get.
        from_date: The datetime where the log time must be at or after. If none the filter is disabled.
        to_date: The datetime where the log time must be at or earlier. If none the filter is disabled.
        process_name: The process name to filter on. If none the filter is disabled.
        log_level: The log level to filter on. If none the filter is disabled.

    Returns:
        tuple[Log]: A list of logs matching the given filters.
    """
    query = (
            select(Log)
            .order_by(desc(Log.log_time))
            .offset(offset)
            .limit(limit)
        )

    if from_date:
        query = query.where(Log.log_time >= from_date)

    if to_date:
        query = query.where(Log.log_time <= to_date)

    if process_name:
        query = query.where(Log.process_name == process_name)

    if log_level:
        query = query.where(Log.log_level == log_level)

    with Session(_connection_engine) as session:
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def create_log(process_name: str, level: LogLevel, message: str) -> None:
    """Create a log in the logs table in the database.

    Args:
        process_name: The name of the process generating the log.
        level: The level of the log.
        message: The message of the log.
    """
    with Session(_connection_engine) as session:
        log = Log(
            log_level = level,
            process_name = process_name,
            log_message = message
        )
        session.add(log)
        session.commit()


@catch_db_error
def get_unique_log_process_names() -> tuple[str]:
    """Get a list of unique process names in the logs database.

    Returns:
        tuple[str]: A list of unique process names.
    """

    query = (
        select(Log.process_name)
        .distinct()
        .order_by(Log.process_name)
    )

    with Session(_connection_engine) as session:
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def create_single_trigger(trigger_name: str, process_name: str, next_run: datetime,
                          process_path: str, process_args: str, is_git_repo: bool, is_blocking: bool) -> None:
    """Create a new single trigger in the database.

    Args:
        trigger_name: The name of the trigger.
        process_name: The process name.
        next_run: The datetime when the trigger should run.
        process_path: The path of the process.
        process_args: The argument string of the process.
        is_git_repo: If the process_path points to a git repo.
        is_blocking: If the process should be blocking.
    """
    with Session(_connection_engine) as session:
        trigger = SingleTrigger(
            trigger_name= trigger_name,
            process_name = process_name,
            process_path = process_path,
            process_args = process_args,
            is_git_repo = is_git_repo,
            is_blocking = is_blocking,
            next_run = next_run
        )
        session.add(trigger)
        session.commit()


@catch_db_error
def create_scheduled_trigger(trigger_name: str, process_name: str, cron_expr: str, next_run: datetime,
                             process_path: str, process_args: str, is_git_repo: bool,
                             is_blocking: bool) -> None:
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
    """
    with Session(_connection_engine) as session:
        trigger = ScheduledTrigger(
            trigger_name= trigger_name,
            process_name = process_name,
            process_path = process_path,
            process_args = process_args,
            is_git_repo = is_git_repo,
            is_blocking = is_blocking,
            next_run = next_run,
            cron_expr = cron_expr
        )
        session.add(trigger)
        session.commit()


@catch_db_error
def create_queue_trigger(trigger_name: str, process_name: str, queue_name: str, process_path: str,
                         process_args: str, is_git_repo: bool, is_blocking: bool,
                         min_batch_size: int) -> None:
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
    """
    with Session(_connection_engine) as session:
        trigger = QueueTrigger(
            trigger_name= trigger_name,
            process_name = process_name,
            process_path = process_path,
            process_args = process_args,
            is_git_repo = is_git_repo,
            is_blocking = is_blocking,
            queue_name = queue_name,
            min_batch_size = min_batch_size
        )
        session.add(trigger)
        session.commit()


@catch_db_error
def get_constant(name: str) -> Constant:
    """Get a constant from the database.

    Args:
        name: The name of the constant.

    Returns:
        Constant: The constant with the given name.

    Raises:
        ValueError: If no constant with the given name exists.
    """
    with Session(_connection_engine) as session:
        constant = session.get(Constant, name)
        if constant is None:
            raise ValueError(f"No constant with name '{name}' was found.")
        return constant


@catch_db_error
def get_constants() -> tuple[Constant]:
    """Get all constants in the database.

    Returns:
        tuple[Constants]: A list of constants.
    """
    with Session(_connection_engine) as session:
        query = select(Constant).order_by(Constant.name)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def create_constant(name: str, value: str) -> None:
    """Create a new constant in the database.

    Args:
        name: The name of the constant.
        value: The value of the constant.
    """
    with Session(_connection_engine) as session:
        constant = Constant(name = name, value = value)
        session.add(constant)
        session.commit()


@catch_db_error
def update_constant(name: str, new_value: str) -> None:
    """Updates an existing constant with a new value.

    Args:
        name: The name of the constant to update.
        new_value: The new value of the constant.
    """
    with Session(_connection_engine) as session:
        constant = session.get(Constant, name)
        constant.value = new_value
        session.commit()


@catch_db_error
def delete_constant(name: str) -> None:
    """Delete the constant with the given name from the database.

    Args:
        name: The name of the constant to delete.
    """
    with Session(_connection_engine) as session:
        constant = session.get(Constant, name)
        session.delete(constant)
        session.commit()


@catch_db_error
def get_credential(name: str) -> Credential:
    """Get a credential from the database.
    The password of the credential is decrypted.

    Args:
        name: The name of the credential.

    Returns:
        Credential: The credential with the given name.

    Raises:
        ValueError: If no credential with the given name exists.
    """
    with Session(_connection_engine) as session:
        credential = session.get(Credential, name)

    if credential is None:
        raise ValueError(f"No credential with name '{name}' was found.")

    credential.password = crypto_util.decrypt_string(credential.password)
    return credential


@catch_db_error
def get_credentials() -> tuple[Credential]:
    """Get all credentials in the database.
    The passwords of the credentials are encrypted.

    Returns:
        tuple[Credential]: A list of credentials.
    """
    with Session(_connection_engine) as session:
        query = select(Credential).order_by(Credential.name)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def create_credential(name: str, username: str, password: str) -> None:
    """Create a new credential in the database.
    The password is encrypted before sending it to the database.

    Args:
        name: The name of the credential.
        username: The username of the credential.
        password: The password of the credential.
    """

    password = crypto_util.encrypt_string(password)

    with Session(_connection_engine) as session:
        credential = Credential(
            name = name,
            username= username,
            password = password
        )
        session.add(credential)
        session.commit()


@catch_db_error
def update_credential(name: str, new_username: str, new_password: str) -> None:
    """Updates an existing credential with a new value.

    Args:
        name: The name of the credential to update.
        new_username: The new username of the credential.
        new_password: The new password of the credential.
    """
    new_password = crypto_util.encrypt_string(new_password)

    with Session(_connection_engine) as session:
        credential = session.get(Credential, name)
        credential.username = new_username
        credential.password = new_password
        session.commit()


@catch_db_error
def delete_credential(name: str) -> None:
    """Delete the credential with the given name from the database.

    Args:
        name: The name of the credential to delete.
    """
    with Session(_connection_engine) as session:
        constant = session.get(Credential, name)
        session.delete(constant)
        session.commit()


@catch_db_error
def begin_single_trigger(trigger_id: str) -> bool:
    """Set the status of a single trigger to 'running' and
    set the last run time to the current time.

    Args:
        trigger_id: The id of the trigger to begin.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(SingleTrigger, trigger_id)

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()

        session.commit()
        return True


@catch_db_error
def get_next_single_trigger() -> SingleTrigger | None:
    """Get the single trigger that should trigger next.

    Returns:
        SingleTrigger | None: The next single trigger to run if any.
    """
    with Session(_connection_engine) as session:
        query = (
            select(SingleTrigger)
            .where(SingleTrigger.process_status == TriggerStatus.IDLE)
            .where(SingleTrigger.next_run <= datetime.now())
            .order_by(SingleTrigger.next_run)
            .limit(1)
        )
        return session.scalar(query)


@catch_db_error
def get_next_scheduled_trigger() -> ScheduledTrigger | None:
    """Get the scheduled trigger that should trigger next.

    Returns:
        ScheduledTrigger | None: The next scheduled trigger to run if any.
    """
    with Session(_connection_engine) as session:
        query = (
            select(ScheduledTrigger)
            .where(ScheduledTrigger.process_status == TriggerStatus.IDLE)
            .where(ScheduledTrigger.next_run <= datetime.now())
            .order_by(ScheduledTrigger.next_run)
            .limit(1)
        )
        return session.scalar(query)


@catch_db_error
def begin_scheduled_trigger(trigger_id: str) -> bool:
    """Set the status of a scheduled trigger to 'running',
    set the last run time to the current time,
    and set the next run time to the given datetime.

    Args:
        trigger_id: The id of the trigger to begin.
        next_run: The next datetime the trigger should run.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(ScheduledTrigger, trigger_id)

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()

        next_run = croniter(trigger.cron_expr, trigger.next_run).get_next(datetime)
        trigger.next_run = next_run

        session.commit()
        return True


@catch_db_error
def get_next_queue_trigger() -> QueueTrigger | None:
    """Get the next queue trigger to run.
    This functions loops through the queue triggers and checks
    if the number of queue elements with status 'New' is above
    the triggers min_batch_size.

    Returns:
        QueueTrigger | None: The next queue trigger to run if any.
    """

    with Session(_connection_engine) as session:

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
            .limit(1)
        )
        return session.scalar(query)


@catch_db_error
def begin_queue_trigger(trigger_id: str) -> None:
    """Set the status of a queue trigger to 'running' and
    set the last run time to the current time.

    Args:
        trigger_id: The id of the trigger to begin.

    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(QueueTrigger, trigger_id)

        if trigger.process_status != TriggerStatus.IDLE:
            return False

        trigger.process_status = TriggerStatus.RUNNING
        trigger.last_run = datetime.now()

        session.commit()
        return True


@catch_db_error
def set_trigger_status(trigger_id: str, status: TriggerStatus) -> None:
    """Set the status of a trigger.

    Args:
        trigger_id: The id of the trigger.
        status: The new status of the trigger.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(Trigger, trigger_id)
        trigger.process_status = status
        session.commit()


@catch_db_error
def create_queue_element(queue_name: str, reference: str = None, data: str = None, created_by: str = None) -> QueueElement:
    """Adds a queue element to the given queue.

    Args:
        queue_name: The name of the queue to add the element to.
        reference (optional): The reference of the queue element.
        data (optional): The data of the queue element.
        created_by (optional): The name of the creator of the queue element.

    Returns:
        QueueElement: The created queue element.
    """
    with Session(_connection_engine) as session:
        q_element = QueueElement(
            queue_name = queue_name,
            data = data,
            reference = reference,
            created_by = created_by
        )
        session.add(q_element)
        session.commit()
        session.refresh(q_element)

    return q_element


@catch_db_error
def bulk_create_queue_elements(queue_name: str, references: tuple[str], data: tuple[str], created_by: str = None) -> None:
    """Insert multiple queue elements into a queue in an optimized manner.
    The lengths of both 'references' and 'data' must be equal to the number of elements to insert.

    Args:
        queue_name: The name of the queue to insert into.
        references: A tuple of reference strings for each queue element.
        data: A tuple of data strings for each queue element.
        created_by (Optional): The name of the creator of the queue elements.

    Raises:
        ValueError: If either 'references' or 'data' are empty, or if they are not equal in length.
    """
    if len(references) == 0:
        raise ValueError("No reference strings were given.")

    if len(data) == 0:
        raise ValueError("No data strings were given.")

    if len(references) != len(data):
        raise ValueError(f"The number of references and data strings don't match: {len(references)} != {len(data)}.")

    q_elements = (
        {
            "queue_name": queue_name,
            "reference": ref,
            "data": dat,
            "created_by": created_by
        }
        for ref, dat in zip(references, data)
    )

    with Session(_connection_engine) as session:
        session.execute(insert(QueueElement), q_elements)
        session.commit()


@catch_db_error
def get_next_queue_element(queue_name: str, reference: str = None, set_status: bool = True) -> QueueElement | None:
    """Gets the next queue element from the given queue that has the status 'new'.

    Args:
        queue_name: The name of the queue to retrieve from.
        reference (optional): The reference to filter on. If None the filter is disabled.
        set_status (optional): If true the queue element's status is set to 'in progress' and the start time is noted.

    Returns:
        QueueElement | None: The next queue element in the queue if any.
    """

    with Session(_connection_engine) as session:
        query = (
            select(QueueElement)
            .where(QueueElement.queue_name == queue_name)
            .where(QueueElement.status == QueueStatus.NEW)
            .order_by(QueueElement.created_date)
            .limit(1)
        )

        if reference is not None:
            query = query.where(QueueElement.reference == reference)

        q_element = session.scalar(query)

        if q_element and set_status:
            q_element.status = QueueStatus.IN_PROGRESS
            q_element.start_date = datetime.now()
            session.commit()
            session.refresh(q_element)

        return q_element


@catch_db_error
def get_queue_elements(queue_name: str, reference: str = None, status: QueueStatus = None,
                       offset: int = 0, limit: int = 100) -> tuple[QueueElement]:
    """Get multiple queue elements from a queue. The elements are ordered by created_date.

    Args:
        queue_name: The queue to get elements from.
        reference (optional): The reference to filter by. If None the filter is disabled.
        status (optional): The status to filter by if any. If None the filter is disabled.
        offset: The number of queue elements to skip.
        limit: The number of queue elements to get.

    Returns:
        tuple[QueueElement]: A tuple of queue elements.
    """
    with Session(_connection_engine) as session:
        query = (
            select(QueueElement)
            .where(QueueElement.queue_name == queue_name)
            .order_by(desc(QueueElement.created_date))
            .offset(offset)
            .limit(limit)
        )
        if reference is not None:
            query = query.where(QueueElement.reference == reference)

        if status is not None:
            query = query.where(QueueElement.status == status)

        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def get_queue_count() -> dict[str, dict[QueueStatus, int]]:
    """Count the number of queue elements of each status for every queue.

    Returns:
        A dict for each queue with the count for each status. E.g. result[queue_name][status] => count.
    """
    with Session(_connection_engine) as session:
        query = (
            select(QueueElement.queue_name, QueueElement.status, alc_func.count())  # pylint: disable=not-callable
            .group_by(QueueElement.queue_name)
            .group_by(QueueElement.status)
        )
        rows = session.execute(query)
        rows = tuple(rows)

    # Aggregate result into a dict
    result = {}
    for queue_name, status, count in rows:
        if queue_name not in result:
            result[queue_name] = {}
        result[queue_name][status] = count

    return result


@catch_db_error
def set_queue_element_status(element_id: str, status: QueueStatus, message: str = None) -> None:
    """Set the status of a queue element.
    If the new status is 'in progress' the start date is noted.
    If the new status is 'Done' or 'Failed' the end date is noted.

    Args:
        element_id: The id of the queue element to change status on.
        status: The new status of the queue element.
        message (Optional): The message to attach to the queue element. This overrides any existing messages.
    """
    with Session(_connection_engine) as session:
        q_element = session.get(QueueElement, element_id)
        q_element.status = status

        if message is not None:
            q_element.message = message

        match status:
            case QueueStatus.IN_PROGRESS:
                q_element.start_date = datetime.now()
            case QueueStatus.DONE | QueueStatus.FAILED:
                q_element.end_date = datetime.now()

        session.commit()


@catch_db_error
def delete_queue_element(element_id: str) -> None:
    """Delete a queue element from the database.

    Args:
        element_id: The id of the queue element.
    """
    with Session(_connection_engine) as session:
        q_element = session.get(QueueElement, element_id)
        session.delete(q_element)
        session.commit()
