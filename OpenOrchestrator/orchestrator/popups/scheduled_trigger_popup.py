"""This module is responsible for the layout and functionality of the 'New Scheduled Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=R0801

import tkinter
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser

import croniter

from OpenOrchestrator.common import db_util


def show_popup() -> tkinter.Toplevel:
    """Creates and shows a popup to create a new Scheduled trigger.

    Returns:
        tkinter.TopLevel: The created Toplevel object (Popup Window).
    """
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Single Trigger")
    window.geometry("300x300")

    ttk.Label(window, text="Process Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Cron Expression:").pack()
    cron_entry = ttk.Entry(window)
    cron_entry.pack()

    help_label = ttk.Label(window, text='Cron Help', cursor='hand2', foreground='blue')
    help_label.bind('<Button-1>', lambda e: webbrowser.open('crontab.guru'))
    help_label.pack()

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
        create_trigger(window, name_entry, cron_entry, path_entry, args_entry, git_check, blocking_check)
    ttk.Button(window, text='Create', command=create_command).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    return window


def create_trigger(window: tkinter.Toplevel,
                   name_entry: ttk.Entry, cron_entry: ttk.Entry,
                   path_entry: ttk.Entry, args_entry: ttk.Entry,
                   git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    """Creates a new scheduled trigger in the database
    using the data entered in the UI.

    Args:
        window: The popup window.
        name_entry: The name entry.
        cron_entry: The cron entry.
        path_entry: The path entry.
        args_entry: The args entry.
        git_check: The intvar holding the 'is_git' value.
        blocking_check: The intvar holding the 'blocking' value.
    """

    name = name_entry.get()
    cron_string = cron_entry.get()
    path = path_entry.get()
    args = args_entry.get()
    is_git = git_check.get()
    is_blocking = blocking_check.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    try:
        cron_iter = croniter.croniter(cron_string, datetime.now())
        date = cron_iter.get_next(datetime)
    except croniter.CroniterBadCronError as exc:
        messagebox.showerror('Error', 'Please enter a valid cron expression\n'+str(exc))
        return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return

    # Create trigger in database
    db_util.create_scheduled_trigger(name, cron_string, date, path, args, is_git, is_blocking)

    window.destroy()
