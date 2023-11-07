"""This module is responsible for the layout and functionality of the 'New credential' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=R0801


import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util

def show_popup(name=None, username=None):
    """Creates and shows a popup to create a new credential.

    Returns:
        tkinter.TopLevel: The created Toplevel object (Popup Window).
    """
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Credential")
    window.geometry("300x300")

    ttk.Label(window, text="Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Username:").pack()
    username_entry = ttk.Entry(window)
    username_entry.pack()

    ttk.Label(window, text="Password:").pack()
    password_entry = ttk.Entry(window)
    password_entry.pack()

    def create_command():
        create_credential(window, name_entry,username_entry, password_entry)
    ttk.Button(window, text='Create', command=create_command).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    if name:
        name_entry.insert('end', name)
    if username:
        username_entry.insert('end', username)

    return window

def create_credential(window: tkinter.Toplevel, name_entry: ttk.Entry,
                      username_entry: ttk.Entry, password_entry:ttk.Entry):
    """Creates a new credential in the database using the data from the
    UI. The password is encrypted before sending it to the database.

    Args:
        window: The popup window.
        name_entry: The name entry.
        username_entry: The username entry.
        password_entry: The password entry.
    """
    name = name_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a name')
        return

    if not username:
        messagebox.showerror('Error', 'Please enter a username')
        return

    if not password:
        messagebox.showerror('Error', 'Please enter a password')
        return

    try:
        db_util.get_credential(name)
        exists = True
    except ValueError:
        exists = False

    if exists:
        if messagebox.askyesno('Error', 'A credential with that name already exists. Do you want to overwrite it?'):
            db_util.update_credential(name, username, password)
        else:
            return
    else:
        db_util.create_credential(name, username, password)

    window.destroy()
