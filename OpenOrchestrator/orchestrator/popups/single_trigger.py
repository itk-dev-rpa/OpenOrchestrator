"""This module is responsible for the layout and functionality of the 'New single Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=duplicate-code

from datetime import datetime

from nicegui import ui

from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.orchestrator.datetime_input2 import DatetimeInput2
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger


class SingleTriggerPopup():
    """A popup for creating/updating single triggers."""
    def __init__(self, trigger: SingleTrigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The Single Trigger to update if any.
        """
        self.trigger = trigger
        title = 'Update Single Trigger' if trigger else 'New Single Trigger'

        with ui.dialog(value=True).props('persistent') as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")

            self.time_input = DatetimeInput("Trigger Time")
            self.time_input = DatetimeInput2("Trigger Time")

            self.path_input = ui.input("Process Path").classes("w-full")
            self.args_input = ui.input("Process Arguments").classes("w-full")
            self.git_check = ui.checkbox("Is Git Repo")
            self.blocking_check = ui.checkbox("Is blocking")

            with ui.row():
                ui.button("Save")
                ui.button("Cancel", on_click=self.dialog.close)

        if trigger is not None:
            pass
            # self.pre_populate()



    # def pre_populate(self):
    #     """Populate the form with values from an existing trigger"""
    #     self.trigger_entry.insert(0, self.trigger.trigger_name)
    #     self.name_entry.insert(0, self.trigger.process_name)
    #     self.date_entry.set_date(self.trigger.next_run)
    #     time_str = self.trigger.next_run.strftime("%H:%M")
    #     self.time_entry.insert(0, time_str)
    #     self.path_entry.insert(0, self.trigger.process_path)
    #     self.args_entry.insert(0, self.trigger.process_args)
    #     self.git_check.set(self.trigger.is_git_repo)
    #     self.blocking_check.set(self.trigger.is_blocking)

    # def create_trigger(self):
    #     """Creates a new single trigger in the database using the data entered in the UI.
    #     If an existing trigger was given when creating the popup it is updated instead.
    #     """
    #     trigger_name = self.trigger_entry.get()
    #     process_name = self.name_entry.get()
    #     date = self.date_entry.get_date()
    #     time = self.time_entry.get()
    #     path = self.path_entry.get()
    #     args = self.args_entry.get()
    #     is_git = self.git_check.get()
    #     is_blocking = self.blocking_check.get()

    #     if not trigger_name:
    #         messagebox.showerror('Error', 'Please enter a trigger name')
    #         return

    #     if not process_name:
    #         messagebox.showerror('Error', 'Please enter a process name')
    #         return

    #     try:
    #         hour, minute = time.split(":")
    #         hour, minute = int(hour), int(minute)
    #         next_run = datetime(date.year, date.month, date.day, hour, minute)
    #     except ValueError as exc:
    #         messagebox.showerror('Error', "Please enter a valid time in the format 'hh:mm'\n"+str(exc))

    #     if next_run < datetime.now():
    #         if not messagebox.askyesno('Warning', "The selected datetime is in the past. Do you want to create the trigger anyway?"):
    #             return

    #     if not path:
    #         messagebox.showerror('Error', 'Please enter a process path')
    #         return

    #     if self.trigger is None:
    #         # Create new trigger in database
    #         db_util.create_single_trigger(trigger_name, process_name, next_run, path, args, is_git, is_blocking)
    #     else:
    #         # Update existing trigger
    #         self.trigger.trigger_name = trigger_name
    #         self.trigger.process_name = process_name
    #         self.trigger.next_run = next_run
    #         self.trigger.process_path = path
    #         self.trigger.process_args = args
    #         self.trigger.is_git_repo = is_git
    #         self.trigger.is_blocking = is_blocking
    #         db_util.update_trigger(self.trigger)

    #     self.destroy()
