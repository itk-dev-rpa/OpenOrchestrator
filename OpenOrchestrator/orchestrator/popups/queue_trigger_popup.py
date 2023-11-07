"""This module is responsible for the layout and functionality of the 'New Queue Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=R0801

import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util

def show_popup():
    """Creates and shows a popup to create a new queue trigger.

    Returns:
        tkinter.TopLevel: The created Toplevel object (Popup Window).
    """
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Queue Trigger")
    window.geometry("300x350")

    ttk.Label(window, text="Trigger Name:").pack()
    trigger_entry = ttk.Entry(window)
    trigger_entry.pack()

    ttk.Label(window, text="Process Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Queue Name:").pack()
    queue_entry = ttk.Entry(window)
    queue_entry.pack()

    ttk.Label(window, text="Process Path:").pack()
    path_entry = ttk.Entry(window)
    path_entry.pack()

    ttk.Label(window, text="Arguments:").pack()
    args_entry = ttk.Entry(window)
    args_entry.pack()

    git_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Git Repo?", variable=git_check).pack()

    blocking_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Blocking?", variable=blocking_check).pack()

    def create_command():
        create_trigger(window, trigger_entry, name_entry, queue_entry, path_entry, args_entry, git_check, blocking_check)
    ttk.Button(window, text='Create', command=create_command).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    return window

def create_trigger(window: tkinter.Toplevel, trigger_entry: ttk.Entry,
                   name_entry: ttk.Entry, queue_entry: ttk.Entry,
                   path_entry: ttk.Entry, args_entry: ttk.Entry,
                   git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    """Creates a new queue trigger in the database
    using the data entered in the UI.

    Args:
        window: The popup window.
        name_entry: The name entry.
        folder_entry: The folder entry.
        path_entry: The path entry.
        args_entry: The args entry.
        git_check: The intvar holding the 'is_git' value.
        blocking_check: The intvar holding the 'blocking' value.
    """
    trigger_name = trigger_entry.get()
    name = name_entry.get()
    queue = queue_entry.get()
    path = path_entry.get()
    args = args_entry.get()
    is_git = git_check.get()
    is_blocking = blocking_check.get()

    if not trigger_name:
        messagebox.showerror('Error', 'Please enter a trigger name')
        return

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    if not queue:
        messagebox.showerror('Error', 'Please enter a queue name')
        return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return

    # Create trigger in database
    db_util.create_queue_trigger(trigger_name, name, queue, path, args, is_git, is_blocking)

    window.destroy()
