"""This module is responsible for the layout and functionality of the 'New Scheduled Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=duplicate-code

from datetime import datetime

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import ScheduledTrigger


class ScheduledTriggerPopup():
    """A popup for creating/updating scheduled triggers."""
    def __init__(self, trigger: ScheduledTrigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The trigger to update if any.
        """
        self.trigger = trigger
        title = 'Update Scheduled Trigger' if trigger else 'New Scheduled Trigger'

        with ui.dialog(value=True).props('persistent') as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")
            self.cron_input = ui.input("Cron expression").classes("w-full")
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
    #     self.cron_entry.insert(0, self.trigger.cron_expr)
    #     self.path_entry.insert(0, self.trigger.process_path)
    #     self.args_entry.insert(0, self.trigger.process_args)
    #     self.git_check.set(self.trigger.is_git_repo)
    #     self.blocking_check.set(self.trigger.is_blocking)

    # def create_trigger(self):
    #     """Creates a new scheduled trigger in the database using the data entered in the UI.
    #     If an existing trigger was given when creating the popup it is updated instead.
    #     """
    #     trigger_name = self.trigger_entry.get()
    #     process_name = self.name_entry.get()
    #     cron_string = self.cron_entry.get()
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
    #         cron_iter = croniter.croniter(cron_string, datetime.now())
    #         next_run = cron_iter.get_next(datetime)
    #     except croniter.CroniterBadCronError as exc:
    #         messagebox.showerror('Error', 'Please enter a valid cron expression\n'+str(exc))
    #         return

    #     if not path:
    #         messagebox.showerror('Error', 'Please enter a process path')
    #         return

    #     if self.trigger is None:
    #         # Create new trigger in database
    #         db_util.create_scheduled_trigger(trigger_name, process_name, cron_string, next_run, path, args, is_git, is_blocking)
    #     else:
    #         # Update existing trigger
    #         self.trigger.trigger_name = trigger_name
    #         self.trigger.process_name = process_name
    #         self.trigger.cron_expr = cron_string
    #         self.trigger.next_run = next_run
    #         self.trigger.process_path = path
    #         self.trigger.process_args = args
    #         self.trigger.is_git_repo = is_git
    #         self.trigger.is_blocking = is_blocking
    #         db_util.update_trigger(self.trigger)

    #     self.destroy()
