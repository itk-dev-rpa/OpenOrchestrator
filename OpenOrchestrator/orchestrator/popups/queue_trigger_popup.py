"""This module is responsible for the layout and functionality of the 'New Queue Trigger' popup."""

# Disable pylint duplicate code error since it
# mostly reacts to the layout code being similar.
# pylint: disable=duplicate-code

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import QueueTrigger


class QueueTriggerPopup():
    """A popup for creating/updating queue triggers."""
    def __init__(self, trigger: QueueTrigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The trigger to update if any.
        """
        self.trigger = trigger
        title = 'Update Queue Trigger' if trigger else 'New Queue Trigger'

        with ui.dialog(value=True).props('persistent') as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")
            self.queue_input = ui.input("Queue Name").classes("w-full")
            self.batch_input = ui.number("Min Batch Size", value=1, min=1, precision=0, format="%.0f")
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
    #     self.queue_entry.insert(0, self.trigger.queue_name)
    #     self.size_entry.insert(0, self.trigger.min_batch_size)
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
    #     queue_name = self.queue_entry.get()
    #     min_batch_size = self.size_entry.get()
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

    #     if not queue_name:
    #         messagebox.showerror("Error", "Please enter a queue name")

    #     try:
    #         min_batch_size = int(min_batch_size)
    #     except ValueError:
    #         messagebox.showerror("Error", "Please enter a integer value for min batch size")
    #         return

    #     if not path:
    #         messagebox.showerror('Error', 'Please enter a process path')
    #         return

    #     if self.trigger is None:
    #         # Create new trigger in database
    #         db_util.create_queue_trigger(trigger_name, process_name, queue_name, path, args, is_git, is_blocking, min_batch_size)
    #     else:
    #         # Update existing trigger
    #         self.trigger.trigger_name = trigger_name
    #         self.trigger.process_name = process_name
    #         self.trigger.queue_name = queue_name
    #         self.trigger.min_batch_size = min_batch_size
    #         self.trigger.process_path = path
    #         self.trigger.process_args = args
    #         self.trigger.is_git_repo = is_git
    #         self.trigger.is_blocking = is_blocking
    #         db_util.update_trigger(self.trigger)

    #     self.destroy()
