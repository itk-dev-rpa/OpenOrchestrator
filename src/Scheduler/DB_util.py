import pyodbc
from tkinter import messagebox

def catch_db_error(func):
    """A decorator that catches errors in SQL queries"""
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except pyodbc.ProgrammingError as e:
            messagebox.showerror("Error", f"Query failed:\n{e}")
    return inner