from tkinter import messagebox
import os
import uuid
from datetime import datetime
import pyodbc
from pypika import MSSQLQuery, Table, Order

_connection_string = None
_connection = None

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
        except pyodbc.DatabaseError as e:
            messagebox.showerror("Database Error", f"Query failed:\n{e}")
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


@catch_db_error
def initialize_database():
    conn = _get_connection()
    commands = _load_sql_file('Initialize_Database.sql')
    commands = commands.split(";")

    for command in commands:
        if command:
            conn.execute(command)
    conn.commit()
    messagebox.showinfo("Database initialized", "Database tables successfully created.")

@catch_db_error
def get_scheduled_triggers():
    conn = _get_connection()

    triggers = Table("Scheduled_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery.from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .select(triggers.process_name, triggers.cron_expr, triggers.last_run, triggers.next_run, triggers.process_path, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .get_sql()
    )

    return conn.execute(command).fetchall()


@catch_db_error
def get_single_triggers():
    conn = _get_connection()

    triggers = Table("Single_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery.from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .select(triggers.process_name, triggers.last_run, triggers.next_run, triggers.process_path, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .get_sql()
    )

    return conn.execute(command).fetchall()

@catch_db_error
def get_email_triggers():
    conn = _get_connection()

    triggers = Table("Email_Triggers")
    status = Table("Trigger_Status")
    command = (
        MSSQLQuery.from_(triggers)
        .join(status)
        .on(triggers.process_status == status.id)
        .select(triggers.process_name, triggers.email_folder, triggers.last_run, triggers.process_path, status.status_text, triggers.is_git_repo, triggers.blocking, triggers.id)
        .get_sql()
    )

    return conn.execute(command).fetchall()

@catch_db_error
def delete_trigger(UUID):
    conn = _get_connection()

    Scheduled_Triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery.delete_from(Scheduled_Triggers)
        .where(Scheduled_Triggers.id == UUID)
        .get_sql()
    )
    conn.execute(command)

    Single_Triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery.delete_from(Single_Triggers)
        .where(Single_Triggers.id == UUID)
        .get_sql()
    )
    conn.execute(command)

    Email_Triggers = Table("Email_Triggers")
    command = (
        MSSQLQuery.delete_from(Email_Triggers)
        .where(Email_Triggers.id == UUID)
        .get_sql()
    )
    conn.execute(command)
   
    conn.commit()


@catch_db_error
def get_logs(offset:int, fetch:int, from_date:datetime, to_date:datetime):
    conn = _get_connection()
    
    logs = Table("Logs")
    command = (
        MSSQLQuery
        .select(logs.log_time, logs.log_level, logs.process_name, logs.log_message)
        .from_(logs)
        .where(from_date <= logs.log_time and logs.log_time <= to_date)
        .orderby(logs.log_time, order=Order.desc)
        .offset(offset)
        .limit(fetch)
        .get_sql()
    )
    
    return conn.execute(command).fetchall()
    

@catch_db_error
def create_single_trigger(name:str, date:datetime, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    
    triggers = Table("Single_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(), 
            name,
            None,
            date,
            path,
            0,
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_scheduled_trigger(name:str, cron:str, date:datetime, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    
    triggers = Table("Scheduled_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(), 
            name,
            cron,
            None,
            date,
            path,
            0,
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def create_email_trigger(name:str, folder:str, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    
    triggers = Table("Email_Triggers")
    command = (
        MSSQLQuery
        .into(triggers)
        .insert(
            uuid.uuid4(), 
            name,
            folder,
            None,
            path,
            0,
            is_git,
            is_blocking
        )
        .get_sql()
    )

    conn.execute(command)
    conn.commit()


@catch_db_error
def get_constants():
    conn = _get_connection()

    constants = Table("Constants")
    command = (
        MSSQLQuery
        .select(constants.constant_name, constants.constant_value)
        .from_(constants)
        .orderby(constants.constant_name)
        .get_sql()
    )

    return conn.execute(command).fetchall()

@catch_db_error
def get_credentials():
    conn = _get_connection()

    credentials = Table("Credentials")
    command = (
        MSSQLQuery
        .select(credentials.cred_name, credentials.cred_value)
        .from_(credentials)
        .orderby(credentials.cred_name)
        .get_sql()
    )

    return conn.execute(command).fetchall()

@catch_db_error
def delete_constant(name: str):
    conn = _get_connection()
    
    constants = Table("Constants")
    command = (
        MSSQLQuery
        .delete_from(constants)
        .where(constants.constant_name == name)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()

@catch_db_error
def delete_credential(name: str):
    conn = _get_connection()
    
    credentials = Table("Credentials")
    command = (
        MSSQLQuery
        .delete_from(credentials)
        .where(credentials.cred_name == name)
        .get_sql()
    )

    conn.execute(command)
    conn.commit()

@catch_db_error
def create_constant(name:str, value:str):
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
def create_credential(name:str, username:str, password:str):
    conn = _get_connection()
    
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