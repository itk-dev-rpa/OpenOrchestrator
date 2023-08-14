import pyodbc
from tkinter import messagebox
import os
from datetime import datetime

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

def _load_sql_file(file_name):
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'SQL', file_name)
    with open(path) as file:
        command = file.read()
    return command

def _fetch_all(file_name):
    conn = _get_connection()
    command = _load_sql_file(file_name)
    rows = conn.execute(command).fetchall()
    return rows

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
    return _fetch_all('Get_Scheduled_Triggers.sql')

@catch_db_error
def get_single_triggers():
    return _fetch_all('Get_Single_Triggers.sql')

@catch_db_error
def get_email_triggers():
    return _fetch_all('Get_Email_Triggers.sql')

@catch_db_error
def delete_trigger(UUID):
    conn = _get_connection()

    commands = _load_sql_file('Delete_Trigger.sql')
    commands = commands.replace('{UUID}', UUID)
    commands = commands.split(';')

    for command in commands:
        if command:
            conn.execute(command)
    
    conn.commit()

@catch_db_error
def get_logs(offset: int, fetch: int, from_date: datetime, to_date: datetime):
    conn = _get_connection()
    command = _load_sql_file('Get_Logs.sql')

    command = command.replace('{OFFSET}', str(offset))
    command = command.replace('{FETCH}', str(fetch))
    command = command.replace('{FROM_DATE}', from_date.strftime('%d-%m-%Y %H:%M:%S'))
    command = command.replace('{TO_DATE}', to_date.strftime('%d-%m-%Y %H:%M:%S'))
    
    logs = conn.execute(command).fetchall()
    return logs

@catch_db_error
def create_single_trigger(name:str, date:datetime, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    command = _load_sql_file('Create_Single_Trigger.sql')

    command = command.replace('{NAME}', str(name))
    command = command.replace('{DATE}', date.strftime('%d-%m-%Y %H:%M:%S'))
    command = command.replace('{PATH}', str(path))
    command = command.replace('{GIT}', str(is_git))
    command = command.replace('{BLOCKING}', str(is_blocking))

    conn.execute(command)
    conn.commit()

@catch_db_error
def create_scheduled_trigger(name:str, cron:str, date:datetime, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    command = _load_sql_file('Create_Scheduled_Trigger.sql')

    command = command.replace('{NAME}', str(name))
    command = command.replace('{CRON}', str(cron))
    command = command.replace('{DATE}', date.strftime('%d-%m-%Y %H:%M:%S'))
    command = command.replace('{PATH}', str(path))
    command = command.replace('{GIT}', str(is_git))
    command = command.replace('{BLOCKING}', str(is_blocking))

    conn.execute(command)
    conn.commit()

@catch_db_error
def create_email_trigger(name:str, folder:str, path:str, is_git:bool, is_blocking:bool):
    conn = _get_connection()
    command = _load_sql_file('Create_Email_Trigger.sql')

    command = command.replace('{NAME}', str(name))
    command = command.replace('{FOLDER}', str(folder))
    command = command.replace('{PATH}', str(path))
    command = command.replace('{GIT}', str(is_git))
    command = command.replace('{BLOCKING}', str(is_blocking))

    conn.execute(command)
    conn.commit()

@catch_db_error
def get_constants():
    return _fetch_all('Get_Constants.sql')

@catch_db_error
def get_credentials():
    return _fetch_all('Get_Credentials.sql')

@catch_db_error
def delete_constant(name: str):
    conn = _get_connection()
    command = _load_sql_file('Delete_Constant.sql')

    command = command.replace('{NAME}', str(name))

    conn.execute(command)
    conn.commit()

@catch_db_error
def delete_credential(name: str):
    conn = _get_connection()
    command = _load_sql_file('Delete_Credential.sql')

    command = command.replace('{NAME}', str(name))

    conn.execute(command)
    conn.commit()

@catch_db_error
def create_constant(name:str, value:str):
    conn = _get_connection()
    command = _load_sql_file('Create_Constant.sql')

    command = command.replace('{NAME}', str(name))
    command = command.replace('{VALUE}', str(value))

    conn.execute(command)
    conn.commit()

@catch_db_error
def create_credential(name:str, username:str, password:str):
    conn = _get_connection()
    command = _load_sql_file('Create_Credential.sql')

    command = command.replace('{NAME}', str(name))
    command = command.replace('{USERNAME}', str(username))
    command = command.replace('{PASSWORD}', str(password))

    print(command)

    conn.execute(command)
    conn.commit()