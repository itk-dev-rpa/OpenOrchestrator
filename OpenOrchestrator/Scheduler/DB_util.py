import os
from tkinter import messagebox
from datetime import datetime
from pypika import MSSQLQuery, Table
import pyodbc

_connection_string = None
_connection = None

_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

def connect(conn_string: str) -> bool:
    global _connection, _connection_string

    try:
        conn = pyodbc.connect(conn_string)
        _connection = conn
        _connection_string = conn_string
        return True
    except Exception as e:
        _connection = None
        _connection_string = None
        messagebox.showerror("Connection failed", str(e))
    
    return False

def catch_db_error(func):
    """A decorator that catches errors in SQL queries"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pyodbc.ProgrammingError as e:
            messagebox.showerror("Error", f"Query failed:\n{e}")
    return inner

def _get_connection():
    global _connection, _connection_string   
    
    if _connection:
        try:
            _connection.cursor()
            return _connection
        except pyodbc.ProgrammingError as e:
            if str(e) != 'Attempt to use a closed connection.':
                messagebox.showerror("Connection Error", str(e))
    
    try:
        _connection = pyodbc.connect(_connection_string)
        return _connection
    except pyodbc.InterfaceError as e:
        messagebox.showerror("Error", f"Connection failed.\nGo to settings and enter a valid connection string.\n{e}")


def get_conn_string():
    return _connection_string

@catch_db_error
def begin_single_trigger(UUID: str):
    conn = _get_connection()
    
    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, 1)
        .set(triggers.last_run, datetime.now().strftime(_DATETIME_FORMAT))
        .where(triggers.id == UUID)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()

@catch_db_error
def set_single_trigger_status(UUID: str, status: int):
    conn = _get_connection()
    
    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, status)
        .where(triggers.id == UUID)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()

@catch_db_error
def get_next_single_trigger():
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

    cursor = conn.execute(command)
    return cursor.fetchone()

@catch_db_error
def get_next_scheduled_trigger():
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

    cursor = conn.execute(command)
    return cursor.fetchone()

@catch_db_error
def begin_scheduled_trigger(UUID: str, next_run: datetime):
    conn = _get_connection()
    
    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, 1)
        .set(triggers.last_run, datetime.now().strftime(_DATETIME_FORMAT))
        .set(triggers.next_run, next_run.strftime(_DATETIME_FORMAT))
        .where(triggers.id == UUID)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()

@catch_db_error
def set_scheduled_trigger_status(UUID: str, status: int):
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .update(triggers)
        .set(triggers.process_status, status)
        .where(triggers.id == UUID)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()