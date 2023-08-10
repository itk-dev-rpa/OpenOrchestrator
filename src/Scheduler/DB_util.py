import pyodbc
import os
from tkinter import messagebox

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
            func(*args, **kwargs)
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

def _load_sql_file(file_name):
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'SQL', file_name)
    with open(path) as file:
        command = file.read()
    return command

def begin_single_trigger(UUID):
    conn = _get_connection()
    command = _load_sql_file('Begin_Single_Trigger.sql')
    command = command.replace('{UUID}', UUID)
    conn.execute(command)
    conn.commit()

def set_single_trigger_status(UUID, status):
    conn = _get_connection()
    command = _load_sql_file('Set_Single_Trigger_Status.sql')
    command = command.replace('{STATUS}', status)
    command = command.replace('{UUID}', UUID)
    conn.execute(command)
    conn.commit()



def get_next_single_trigger():
    conn = _get_connection()
    command = _load_sql_file('Get_Next_Single_Trigger.sql')
    cursor = conn.execute(command)
    return cursor.fetchone()