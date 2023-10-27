"""This module is responsible for the layout and functionality of the 'New constant' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=R0801

import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util

def show_popup(name=None, value=None):
    """Creates and shows a popup to create a new constant.

    Returns:
        tkinter.TopLevel: The created Toplevel object (Popup Window).
    """
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Constant")
    window.geometry("300x300")

    ttk.Label(window, text="Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Value:").pack()
    value_entry = ttk.Entry(window)
    value_entry.pack()

    def create_command():
        create_constant(window, name_entry,value_entry)
    ttk.Button(window, text='Create', command=create_command ).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    if name:
        name_entry.insert('end', name)
    if value:
        value_entry.insert('end', value)

    return window

def create_constant(window, name_entry: ttk.Entry, value_entry: ttk.Entry):
    """Creates a new constant in the database using the data from the
    UI.

    Args:
        window: The popup window.
        name_entry: The name entry.
        value_entry: The value entry.
    """
    name = name_entry.get()
    value = value_entry.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a name')
        return

    if not value:
        messagebox.showerror('Error', 'Please enter a value')
        return

    constants = db_util.get_constants()
    exists = any(c[0].lower() == name.lower() for c in constants)

    if exists and not messagebox.askyesno('Error', 'A constant with that name already exists. Do you want to overwrite it?'):
        return

    db_util.delete_constant(name)

    db_util.create_constant(name, value)

    window.destroy()
