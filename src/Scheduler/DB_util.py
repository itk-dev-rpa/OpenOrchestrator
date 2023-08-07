import pyodbc
import os
from tkinter import messagebox

def catch_db_error(func):
    """A decorator that catches errors in SQL queries"""
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except pyodbc.ProgrammingError as e:
            messagebox.showerror("Error", f"Query failed:\n{e}")
    return inner

def load_sql_file(file_name: str) -> str:
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'SQL', file_name)
    with open(path) as file:
        command = file.read()
    return command