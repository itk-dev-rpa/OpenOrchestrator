"""This module handles the connection to the database in OpenOrchestrator."""

from datetime import datetime
from tkinter import messagebox
import uuid

import pyodbc
from pypika import MSSQLQuery, Table, Order

from OpenOrchestrator.common import crypto_util

_connection_string: str
_connection: pyodbc.Connection

_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

def connect(conn_string: str) -> bool:
    """Connects to the database using the given connection string.

    Args:
        conn_string: The connection string.

    Returns:
        bool: True if successful.
    """
    global _connection, _connection_string #pylint: disable=global-statement

    try:
        conn = pyodbc.connect(conn_string)
        _connection = conn
        _connection_string = conn_string
        return True
    except pyodbc.InterfaceError as exc:
        _connection = None
        _connection_string = None
        messagebox.showerror("Connection failed", str(exc))

    return False


def catch_db_error(func: callable) -> callable:
    """A decorator that catches errors in SQL calls."""
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except pyodbc.ProgrammingError as exc:
            messagebox.showerror("Error", f"Query failed:\n{exc}")
        return result
    return inner


def _get_connection() -> pyodbc.Connection:
    """Get the open connection.
    If the connection is closed, try to reopen it.
    """
    global _connection #pylint: disable=global-statement

    if _connection:
        try:
            # Test if connection is still open
            _connection.cursor()
            return _connection
        except pyodbc.ProgrammingError as exc:
            if str(exc) != 'Attempt to use a closed connection.':
                messagebox.showerror("Connection Error", str(exc))

    try:
        _connection = pyodbc.connect(_connection_string)
    except pyodbc.InterfaceError as exc:
        messagebox.showerror("Error", f"Connection failed.\nGo to settings and enter a valid connection string.\n{exc}")

    return _connection


def get_conn_string() -> str:
    """Get the connection string.

    Returns:
        str: The connection string if any.
    """
    return _connection_string


@catch_db_error
def initialize_database() -> None:
    """Initializes the database with all the needed tables."""  
    messagebox.showinfo("Database initialized", "Initialization not implemented.")


@catch_db_error
def get_scheduled_triggers() -> list[list[str]]:
    """Get all scheduled triggers from the database.
    The format of each trigger is as follows:
    [process_name, cron_expr, last_run, next_run, process_path, process_args, status_text, is_git_repo, blocking, id]

    Returns:
        list[list[str]]: A list of all scheduled triggers in the database as lists of strings.
    """
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery
        .select(triggers.process_name, triggers.cron_expr, triggers.last_run, triggers.next_run, triggers.process_path, triggers.process_args, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def get_single_triggers() -> list[list[str]]:
    """Get all single triggers from the database.
    The format of each trigger is as follows:
    [process_name, last_run, next_run, process_path, process_args, status_text, is_git_repo, blocking, id]

    Returns:
        list[list[str]]: A list of all single triggers in the database as lists of strings.
    """
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery
        .select(triggers.process_name, triggers.last_run, triggers.next_run, triggers.process_path, triggers.process_args, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def get_email_triggers() -> list[list[str]]:
    """Get all email triggers from the database.
    The format of each trigger is as follows:
    [process_name, email_folder, last_run, process_path, process_args, status_text, is_git_repo, blocking, id]trigger_id

    Returns:
        list[list[str]]: A list of all email triggers in the database as lists of strings.
    """
    conn = _get_connection()

    triggers = Table("Email_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery
        .select(triggers.process_name, triggers.email_folder, triggers.last_run, triggers.process_path, triggers.process_args, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def delete_trigger(trigger_id: str) -> None:
    """Delete a trigger with the given UUID.
    The trigger can be of any type.

    Args:
        UUID: The unique identifier of the trigger.
    """
    conn = _get_connection()

    scheduled_triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .from_(scheduled_triggers)
        .delete()
        .where(scheduled_triggers.id == trigger_id)
        .get_sql()
    )
    conn.execute(command)

    single_triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .from_(single_triggers)
        .delete()
        .where(single_triggers.id == trigger_id)
        .get_sql()
    )
    conn.execute(command)

    email_triggers = Table("Email_Triggers")
    command = (
        MSSQLQuery
        .from_(email_triggers)
        .delete()
        .where(email_triggers.id == trigger_id)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def get_logs(offset: int, fetch: int,
             from_date: datetime, to_date: datetime,
             process_name: str, log_level: str) -> list[list[str]]:
    """Get the logs from the database using filters and pagination.
    The format of the logs is as follows:
    [log_time, level_text, process_name, log_message]

    Args:
        offset: The index of the first log to get.
        fetch: The number of logs to get.
        from_date: The datetime where the log time must be at or after.
        to_date: The datetime where the log time must be at or earlier.
        process_name: The process name to filter on. If none the filter is disabled.
        log_level: The log level to filter on. If none the filter is disabled.

    Returns:
        list[list[str]]: A list of logs as lists of strings.
    """
    conn = _get_connection()

    logs = Table("Logs")
    levels = Table("Log_Level")
    command = (
        MSSQLQuery
        .select(logs.log_time, levels.level_text, logs.process_name, logs.log_message)
        .from_(logs)
        .join(levels)
        .on(logs.log_level == levels.id)
        .where(from_date <= logs.log_time)
        .where(logs.log_time <= to_date)
        .orderby(logs.log_time, order=Order.desc)
        .offset(offset)
        .limit(fetch)
    )

    if process_name:
        command = command.where(logs.process_name == process_name)

    if log_level:
        log_level = {"Trace": 0, "Info": 1, "Error": 2}[log_level]
        command = command.where(logs.log_level == log_level)

    command = command.get_sql()

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def get_unique_log_process_names() -> list[str]:
    """Get a list of unique process names in the logs database.

    Returns:
        list[str]: A list of unique process names.
    """
    conn = _get_connection()

    logs = Table("Logs")
    command = (
        MSSQLQuery
        .select(logs.process_name)
        .distinct()
        .from_(logs)
        .orderby(logs.process_name)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [r[0] for r in rows]


@catch_db_error
def create_single_trigger(name: str, date: datetime, path: str,
                          args: str, is_git: bool, is_blocking: bool) -> None:
    """Create a new single trigger in the database.

    Args:
        name: The process name.
        date: The datetime when the trigger should run.
        path: The path of the process.
        args: The argument string of the process.
        is_git: The is_git value.
        is_blocking: The is_blocking value.
    """
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(),
            name,
            None, # Last run
            date,
            path,
            args,
            0, # Status = Idle
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_scheduled_trigger(name: str, cron: str, date: datetime,
                             path: str, args: str, is_git: bool,
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
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(),
            name,
            cron,
            None, # Last run
            date,
            path,
            args,
            0, # Status = Idle
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_email_trigger(name: str, folder: str, path: str,
                         args: str, is_git: bool, is_blocking: bool) -> None:
    """Create a new email trigger in the database.

    Args:
        name: The process name.
        folder: The email folder of the trigger.
        path: The path of the process.
        args: The argument string of the process.
        is_git: The is_git value of the process.
        is_blocking: The is_blocking value of the process.
    """
    conn = _get_connection()

    triggers = Table("Email_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(),
            name,
            folder,
            None, # Last run
            path,
            args,
            0, # Status = Idle
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def get_constants() -> list[list[str]]:
    """Get all constants in the database.
    The format of the constants are as follows:
    [constant_name, constant_value]

    Returns:
        list[list[str]]: A list of constants as lists of strings.
    """
    conn = _get_connection()

    constants = Table("Constants")
    command = (
        MSSQLQuery
        .select(constants.constant_name, constants.constant_value)
        .from_(constants)
        .orderby(constants.constant_name)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def get_credentials() -> list[list[str]]:
    """Get all credentials in the database.
    The format of the credentials are as follows:
    [cred_name, cred_username, cred_password]

    Returns:
        list[list[str]]: A list of credentials as lists of strings.
    """
    conn = _get_connection()

    credentials = Table("Credentials")
    command = (
        MSSQLQuery
        .select(credentials.cred_name, credentials.cred_username, credentials.cred_password)
        .from_(credentials)
        .orderby(credentials.cred_name)
        .get_sql()
    )

    rows = conn.execute(command).fetchall()
    return [list(r) for r in rows]


@catch_db_error
def delete_constant(name: str) -> None:
    """Delete the constant with the given name from the database.

    Args:
        name: The name of the constant to delete.
    """
    conn = _get_connection()

    constants = Table("Constants")
    command = (
        MSSQLQuery
        .from_(constants)
        .delete()
        .where(constants.constant_name == name)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def delete_credential(name: str) -> None:
    """Delete the credential with the given name from the database.

    Args:
        name: The name of the credential to delete.
    """
    conn = _get_connection()

    credentials = Table("Credentials")
    command = (
        MSSQLQuery
        .from_(credentials)
        .delete()
        .where(credentials.cred_name == name)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_constant(name: str, value: str) -> None:
    """Create a new constant in the database.

    Args:
        name: The name of the constant.
        value: The value of the constant.
    """
    conn = _get_connection()

    constants = Table("Constants")
    command = (
        MSSQLQuery
        .into(constants)
        .insert(
            name,
            value
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_credential(name: str, username: str, password: str) -> None:
    """Create a new credential in the database.
    The password is encrypted before sending it to the database.

    Args:
        name: The name of the credential.
        username: The username of the credential.
        password: The password of the credential.
    """
    conn = _get_connection()

    password = crypto_util.encrypt_string(password)

    credentials = Table("Credentials")
    command = (
        MSSQLQuery
        .into(credentials)
        .insert(
            name,
            username,
            password
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def begin_single_trigger(trigger_id: str) -> bool:
    """Set the status of a single trigger to 'running' and 
    set the last run time to the current time.

    Args:
        UUID: The UUID of the trigger to begin.
    
    Returns:
        bool: True if the trigger was 'idle' and now 'running'.
    """
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, 1)
        .set(triggers.last_run, datetime.now().strftime(_DATETIME_FORMAT))
        .where(triggers.id == trigger_id)
        .where(triggers.process_status == 0)
        .get_sql()
    )

    cursor = conn.execute(command)
    if cursor.rowcount == 0:
        return False

    conn.commit()
    return True


@catch_db_error
def set_single_trigger_status(trigger_id: str, status: int) -> None:
    """Set the status of a single trigger.
    Status codes are:
    0: Idle
    1: Running
    2: Error
    3: Done

    Args:
        UUID: The UUID of the trigger.
        status: The new status of the trigger.
    """
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, status)
        .where(triggers.id == trigger_id)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def get_next_single_trigger() -> list[str]:
    """Get the single trigger that should trigger next.
    A trigger returned by this is not necessarily ready to trigger.
    The format of the trigger is:
    [process_name, next_run, id, process_path, is_git_repo, blocking]

    Returns:
        list[str]: The next single trigger to run, if any.
    """
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .select(triggers.process_name, triggers.next_run, triggers.id, triggers.process_path, triggers.is_git_repo, triggers.blocking)
        .from_(triggers)
        .where(triggers.process_status == 0)
        .orderby(triggers.next_run)
        .limit(1)
        .get_sql()
    )

    trigger = conn.execute(command).fetchone()
    return list[trigger]


@catch_db_error
def get_next_scheduled_trigger() -> list[str]:
    """Get the scheduled trigger that should trigger next.
    A trigger returned by this is not necessarily ready to trigger.
    The format of the trigger is:
    [process_name, next_run, id, process_path, is_git_repo, blocking, cron_expr]

    Returns:
        list[str]: The next scheduled trigger to run, if any.
    """
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .select(triggers.process_name, triggers.next_run, triggers.id, triggers.process_path, triggers.is_git_repo, triggers.blocking, triggers.cron_expr)
        .from_(triggers)
        .where(triggers.process_status == 0)
        .orderby(triggers.next_run)
        .limit(1)
        .get_sql()
    )

    trigger = conn.execute(command).fetchone()
    return list[trigger]


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
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, 1)
        .set(triggers.last_run, datetime.now().strftime(_DATETIME_FORMAT))
        .set(triggers.next_run, next_run.strftime(_DATETIME_FORMAT))
        .where(triggers.id == trigger_id)
        .where(triggers.process_status == 0)
        .get_sql()
    )

    cursor = conn.execute(command)
    if cursor.rowcount == 0:
        return False

    conn.commit()
    return True


@catch_db_error
def set_scheduled_trigger_status(trigger_id: str, status: int) -> None:
    """Set the status of a scheduled trigger.
    Status codes are:
    0: Idle
    1: Running
    2: Error
    3: Done

    Args:
        UUID: The UUID of the trigger.
        status: The new status of the trigger.
    """
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, status)
        .where(triggers.id == trigger_id)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()
