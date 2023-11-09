"""This module is responsible for the layout and functionality of the 'New Queue Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=R0801

import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import QueueTrigger

# pylint: disable-next=too-many-instance-attributes
class QueueTriggerPopup(tkinter.Toplevel):
    """A popup for creating/updating scheduled triggers."""
    def __init__(self, trigger: QueueTrigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The Scheduled Trigger to update if any.
        """
        self.trigger = trigger
        title = 'Update Queue Trigger' if trigger else 'New Queue Trigger'

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

        ttk.Label(self, text="Queue Name:").pack()
        self.queue_entry = ttk.Entry(self)
        self.queue_entry.pack()

        ttk.Label(self, text="Min batch size:").pack()
        self.size_entry = ttk.Entry(self)
        self.size_entry.pack()

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

        if self.trigger is not None:
            self.pre_populate()

    def pre_populate(self):
        """Populate the form with values from an existing trigger"""
        self.trigger_entry.insert(0, self.trigger.trigger_name)
        self.name_entry.insert(0, self.trigger.process_name)
        self.queue_entry.insert(0, self.trigger.queue_name)
        self.size_entry.insert(0, self.trigger.min_batch_size)
        self.path_entry.insert(0, self.trigger.process_path)
        self.args_entry.insert(0, self.trigger.process_args)
        self.git_check.set(self.trigger.is_git_repo)
        self.blocking_check.set(self.trigger.is_blocking)

    def create_trigger(self):
        """Creates a new scheduled trigger in the database using the data entered in the UI.
        If an existing trigger was given when creating the popup it is updated instead.
        """
        trigger_name = self.trigger_entry.get()
        process_name = self.name_entry.get()
        queue_name = self.queue_entry.get()
        min_batch_size = self.size_entry.get()
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

        if not queue_name:
            messagebox.showerror("Error", "Please enter a queue name")

        try:
            min_batch_size = int(min_batch_size)
        except ValueError:
            messagebox.showerror("Error", "Please enter a integer value for min batch size")
            return

        if not path:
            messagebox.showerror('Error', 'Please enter a process path')
            return

        if self.trigger is None:
            # Create new trigger in database
            db_util.create_queue_trigger(trigger_name, process_name, queue_name, path, args, is_git, is_blocking, min_batch_size)
        else:
            # Update existing trigger
            self.trigger.trigger_name = trigger_name
            self.trigger.process_name = process_name
            self.trigger.queue_name = queue_name
            self.trigger.min_batch_size = min_batch_size
            self.trigger.process_path = path
            self.trigger.process_args = args
            self.trigger.is_git_repo = is_git
            self.trigger.is_blocking = is_blocking
            db_util.update_trigger(self.trigger)

        self.destroy()
