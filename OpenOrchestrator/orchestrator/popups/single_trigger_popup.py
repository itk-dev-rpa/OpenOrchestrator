"""This module is responsible for the layout and functionality of the 'New single Trigger' popup."""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from nicegui import ui

from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger, TriggerStatus
from OpenOrchestrator.orchestrator.popups import generic_popups

if TYPE_CHECKING:
    from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab

class SingleTriggerPopup():
    """A popup for creating/updating single triggers."""
    def __init__(self, trigger_tab: TriggerTab, trigger: SingleTrigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The Single Trigger to update if any.
        """
        self.trigger_tab = trigger_tab
        self.trigger = trigger
        title = 'Update Single Trigger' if trigger else 'New Single Trigger'

        with ui.dialog(value=True) as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")
            self.time_input = DatetimeInput("Trigger Time")
            self.path_input = ui.input("Process Path").classes("w-full")
            self.args_input = ui.input("Process Arguments").classes("w-full")
            self.git_check = ui.checkbox("Is Git Repo")
            self.blocking_check = ui.checkbox("Is blocking")

            if trigger:
                with ui.row():
                    ui.button("Enable", on_click=self._enable_trigger)
                    ui.button("Disable", on_click=self._disable_trigger)
                    ui.button("Delete", on_click=self._delete_trigger, color='red')
            else:
                self.dialog.props('persistent')

            with ui.row():
                ui.button("Save", on_click=self._create_trigger)
                ui.button("Cancel", on_click=self.dialog.close)

        if trigger:
            self._pre_populate()

    def _pre_populate(self):
        """Populate the form with values from an existing trigger"""
        self.trigger_input.value = self.trigger.trigger_name
        self.name_input.value = self.trigger.process_name
        self.time_input.set_datetime(self.trigger.next_run)
        self.path_input.value = self.trigger.process_path
        self.args_input.value = self.trigger.process_args
        self.git_check.value = self.trigger.is_git_repo
        self.blocking_check.value = self.trigger.is_blocking

    async def _create_trigger(self):
        """Creates a new single trigger in the database using the data entered in the UI.
        If an existing trigger was given when creating the popup it is updated instead.
        """
        trigger_name = self.trigger_input.value
        process_name = self.name_input.value
        next_run = self.time_input.get_datetime()
        path = self.path_input.value
        args = self.args_input.value
        is_git = self.git_check.value
        is_blocking = self.blocking_check.value

        if not trigger_name:
            ui.notify('Please enter a trigger name', type='negative')
            return

        if not process_name:
            ui.notify('Please enter a process name', type='negative')
            return

        if next_run < datetime.now():
            if not await generic_popups.question_popup(
                    "The selected datetime is in the past. Do you want to create the trigger anyway?",
                    "Create", "Cancel"):
                return

        if not path:
            ui.notify('Please enter a process path', type='negative')
            return

        if self.trigger is None:
            # Create new trigger in database
            db_util.create_single_trigger(trigger_name, process_name, next_run, path, args, is_git, is_blocking)
            ui.notify("Trigger created", type='positive')
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
            ui.notify("Trigger updated", type='positive')

        self.dialog.close()
        self.trigger_tab.update()

    async def _delete_trigger(self):
        if await generic_popups.question_popup(f"Delete trigger '{self.trigger.trigger_name}'?", "Delete", "Cancel"):
            db_util.delete_trigger(self.trigger.id)
            ui.notify("Trigger deleted", type='positive')
            self.dialog.close()
            self.trigger_tab.update()

    def _disable_trigger(self):
        db_util.set_trigger_status(self.trigger.id, TriggerStatus.PAUSED)
        ui.notify("Trigger status set to 'Paused'.", type='positive')
        self.trigger_tab.update()

    def _enable_trigger(self):
        db_util.set_trigger_status(self.trigger.id, TriggerStatus.IDLE)
        ui.notify("Trigger status set to 'Idle'.", type='positive')
        self.trigger_tab.update()
