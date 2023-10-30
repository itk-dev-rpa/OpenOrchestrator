"""This module handles the connection to the database in OpenOrchestrator."""

from datetime import datetime
from tkinter import messagebox

from sqlalchemy import Engine, create_engine, select, text
from sqlalchemy import exc as alc_exc
from sqlalchemy.orm import Session

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import logs, triggers, constants
from OpenOrchestrator.database.logs import Log, LogLevel
from OpenOrchestrator.database.constants import Constant, Credential
from OpenOrchestrator.database.triggers import Trigger, SingleTrigger, ScheduledTrigger, QueueTrigger, TriggerStatus

_connection_engine: Engine
_connection_string: str


def connect(conn_string: str) -> bool:
    """Connects to the database using the given connection string.

    Args:
        conn_string: The connection string.

    Returns:
        bool: True if successful.
    """
    global _connection_engine, _connection_string # pylint: disable=global-statement

    try:
        engine = create_engine(conn_string)
        engine.connect()
        _connection_engine = engine
        _connection_string = conn_string
        return True
    except alc_exc.InterfaceError as exc:
        _connection_engine = None
        messagebox.showerror("Connection failed", str(exc))

    return False


def disconnect() -> None:
    """Disconnect from the database."""
    global _connection_engine #pylint: disable=global-statement
    _connection_engine.dispose()
    _connection_engine = None


def catch_db_error(func: callable) -> callable:
    """A decorator that catches errors in SQL calls."""
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except alc_exc.ProgrammingError as exc:
            messagebox.showerror("Error", f"Query failed:\n{exc}")
        return result
    return inner


def get_conn_string() -> str:
    """Get the connection string.

    Returns:
        str: The connection string if any.
    """
    return _connection_string


@catch_db_error
def initialize_database() -> None:
    """Initializes the database with all the needed tables."""
    logs.create_tables(_connection_engine)
    triggers.create_tables(_connection_engine)
    constants.create_tables(_connection_engine)
    messagebox.showinfo("Database initialized", "Database has been initialized!")


@catch_db_error
def get_scheduled_triggers() -> tuple[ScheduledTrigger]:
    """Get all scheduled triggers from the database.

    Returns:
        tuple(ScheduledTrigger): A list of all scheduled triggers in the database.
    """
    with Session(_connection_engine) as session:
        query = select(ScheduledTrigger)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def get_single_triggers() -> tuple[SingleTrigger]:
    """Get all single triggers from the database.

    Returns:
        tuple(SingleTrigger): A list of all single triggers in the database.
    """
    with Session(_connection_engine) as session:
        query = select(SingleTrigger)
        result = session.scalars(query).all()
        return tuple(result)


@catch_db_error
def get_queue_triggers() -> tuple[QueueTrigger]:
    """Get all queue triggers from the database.

    Returns:
        tuple(QueueTrigger): A list of all queue triggers in the database.
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
             from_date: datetime|None, to_date: datetime|None,
             process_name: str|None, log_level: LogLevel|None) -> tuple[Log]:
    """Get the logs from the database using filters and pagination.

    Args:
        offset: The index of the first log to get.
        limit: The number of logs to get.
        from_date: The datetime where the log time must be at or after. If none the filter is disabled.
        to_date: The datetime where the log time must be at or earlier. If none the filter is disabled.
        process_name: The process name to filter on. If none the filter is disabled.
        log_level: The log level to filter on. If none the filter is disabled.

    Returns:
        tuple(Log): A list of logs matching the given filters.
    """
    query = (
            select(Log)
            .order_by(Log.log_time)
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
        level: The level of the log (0,1,2).
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
        name: The process name.
        cron: The cron expression of the trigger.
        date: The date to first run the trigger.
        path: The path of the process.
        args: The argument string of the process.
        is_git: The is_git value of the process.
        is_blocking: The is_blocking value of the process.
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
                         min_batch_size: int=None, max_batch_size: int=None) -> None:
    """Create a new queue trigger in the database.

    Args:
        name: The process name.
        folder: The email folder of the trigger.
        path: The path of the process.
        args: The argument string of the process.
        is_git: The is_git value of the process.
        is_blocking: The is_blocking value of the process.
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
            min_batch_size = min_batch_size,
            max_batch_size = max_batch_size
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
        query = select(Constant).order_by(Constant.constant_name)
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
        constant = Constant(constant_name = name, constant_value = value)
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
        constant.constant_value = new_value
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

        credential.credential_password = crypto_util.decrypt_string(credential.credential_password)
        return credential


@catch_db_error
def get_credentials() -> tuple[Credential]:
    """Get all credentials in the database.
    The passwords of the credentials are encrypted.

    Returns:
        tuple[Credential]: A list of credentials.
    """
    with Session(_connection_engine) as session:
        query = select(Credential).order_by(Credential.credential_name)
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
            credential_name = name,
            credential_username= username,
            credential_password = password
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
        credential.credential_username = new_username
        credential.credential_password = new_password
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
        UUID: The UUID of the trigger to begin.
    
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
def begin_scheduled_trigger(trigger_id: str, next_run: datetime) -> None:
    """Set the status of a scheduled trigger to 'running', 
    set the last run time to the current time,
    and set the next run time to the given datetime.

    Args:
        UUID: The UUID of the trigger to begin.
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
        query = (
            select(QueueTrigger)
            .where(QueueTrigger.process_status == TriggerStatus.IDLE)
        )
        for trigger in session.scalars(query):
            query = text("SELECT COUNT(*) FROM :table WHERE Status='New'")
            count = session.scalar(query, {":table": trigger.queue_name})
            if count >= trigger.min_batch_size:
                return trigger

    return None


@catch_db_error
def set_trigger_status(trigger_id: str, status: TriggerStatus) -> None:
    """Set the status of a trigger.

    Args:
        UUID: The UUID of the trigger.
        status: The new status of the trigger.
    """
    with Session(_connection_engine) as session:
        trigger = session.get(Trigger, trigger_id)
        trigger.process_status = status
        session.commit()
