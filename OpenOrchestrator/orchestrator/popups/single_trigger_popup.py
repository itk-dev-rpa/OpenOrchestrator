"""This module is responsible for the layout and functionality of the 'New single Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=duplicate-code

from datetime import datetime
import tkinter
from tkinter import ttk, messagebox
import tkcalendar

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger

# pylint: disable-next=too-many-instance-attributes
class SingleTriggerPopup(tkinter.Toplevel):
    """A popup for creating/updating single triggers."""
    def __init__(self, trigger: SingleTrigger):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The Single Trigger to update if any.
        """
        self.trigger = trigger
        title = 'Update Single Trigger' if trigger else 'New Single Trigger'

        super().__init__()
        self.grab_set()
        self.title(title)
        self.geometry("300x350")

        ttk.Label(self, text="Trigger Name:").pack()
        self.trigger_entry = ttk.Entry(self)
        self.trigger_entry.pack()

        ttk.Label(self, text="Process Name:").pack()
        self.name_entry = ttk.Entry(self)
        self.name_entry.pack()

        ttk.Label(self, text="Trigger Date:").pack()
        self.date_entry = tkcalendar.DateEntry(self, date_pattern='dd/MM/yyyy')
        self.date_entry.pack()

        ttk.Label(self, text="Trigger Time:").pack()
        self.time_entry = ttk.Entry(self)
        if trigger is None:
            self.time_entry.insert(0, 'hh:mm')
        self.time_entry.pack()

        ttk.Label(self, text="Process Path:").pack()
        self.path_entry = ttk.Entry(self)
        self.path_entry.pack()

        ttk.Label(self, text="Arguments:").pack()
        self.args_entry = ttk.Entry(self)
        self.args_entry.pack()

        self.git_check = tkinter.IntVar()
        ttk.Checkbutton(self, text="Is Git Repo?", variable=self.git_check).pack()

        self.blocking_check = tkinter.IntVar()
        ttk.Checkbutton(self, text="Is Blocking?", variable=self.blocking_check).pack()

        button_text = 'Update' if trigger else 'Create'
        ttk.Button(self, text=button_text, command=self.create_trigger).pack()
        ttk.Button(self, text='Cancel', command=self.destroy).pack()

        if trigger is not None:
            self.pre_populate()

    def pre_populate(self):
        """Populate the form with values from an existing trigger"""
        self.trigger_entry.insert(0, self.trigger.trigger_name)
        self.name_entry.insert(0, self.trigger.process_name)
        self.date_entry.set_date(self.trigger.next_run)
        time_str = self.trigger.next_run.strftime("%H:%M")
        self.time_entry.insert(0, time_str)
        self.path_entry.insert(0, self.trigger.process_path)
        self.args_entry.insert(0, self.trigger.process_args)
        self.git_check.set(self.trigger.is_git_repo)
        self.blocking_check.set(self.trigger.is_blocking)

    def create_trigger(self):
        """Creates a new single trigger in the database using the data entered in the UI.
        If an existing trigger was given when creating the popup it is updated instead.
        """
        trigger_name = self.trigger_entry.get()
        process_name = self.name_entry.get()
        date = self.date_entry.get_date()
        time = self.time_entry.get()
        path = self.path_entry.get()
        args = self.args_entry.get()
        is_git = self.git_check.get()
        is_blocking = self.blocking_check.get()

        if not trigger_name:
            messagebox.showerror('Error', 'Please enter a trigger name')
            return

        if not process_name:
            messagebox.showerror('Error', 'Please enter a process name')
            return

        try:
            hour, minute = time.split(":")
            hour, minute = int(hour), int(minute)
            next_run = datetime(date.year, date.month, date.day, hour, minute)
        except ValueError as exc:
            messagebox.showerror('Error', "Please enter a valid time in the format 'hh:mm'\n"+str(exc))

        if next_run < datetime.now():
            if not messagebox.askyesno('Warning', "The selected datetime is in the past. Do you want to create the trigger anyway?"):
                return

        if not path:
            messagebox.showerror('Error', 'Please enter a process path')
            return

        if self.trigger is None:
            # Create new trigger in database
            db_util.create_single_trigger(trigger_name, process_name, next_run, path, args, is_git, is_blocking)
        else:
            # Update existing trigger
            self.trigger.trigger_name = trigger_name
            self.trigger.process_name = process_name
            self.trigger.next_run = next_run
            self.trigger.process_path = path
            self.trigger.process_args = args
            self.trigger.is_git_repo = is_git
            self.trigger.is_blocking = is_blocking
            db_util.update_trigger(self.trigger)

        self.destroy()
