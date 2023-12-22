"""This module is responsible for the layout and functionality of the 'New single Trigger' popup."""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from nicegui import ui
from croniter import croniter, CroniterBadCronError

from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import Trigger, TriggerStatus, TriggerType
from OpenOrchestrator.orchestrator.popups import generic_popups

if TYPE_CHECKING:
    from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab


class TriggerPopup():
    """A popup for creating/updating single triggers."""
    def __init__(self, trigger_tab: TriggerTab, trigger_type: TriggerType, trigger: Trigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger: The Single Trigger to update if any.
        """
        self.trigger_tab = trigger_tab
        self.trigger_type = trigger_type
        self.trigger = trigger
        title = 'Update Single Trigger' if trigger else 'New Single Trigger'

        with ui.dialog(value=True) as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")
            self.time_input = DatetimeInput("Trigger Time")  # For single triggers
            self.cron_input = ui.input("Cron expression").classes("w-full")  # For scheduled triggers
            self.queue_input = ui.input("Queue Name").classes("w-full")  # For queue triggers
            self.batch_input = ui.number("Min Batch Size", value=1, min=1, precision=0, format="%.0f")  # For queue triggers
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
                # Dialog should only be persistent when a new trigger is being created
                self.dialog.props('persistent')

            with ui.row():
                ui.button("Save", on_click=self._create_trigger)
                ui.button("Cancel", on_click=self.dialog.close)

        self._disable_unused()

        if trigger:
            self._pre_populate()

    def _pre_populate(self):
        """Populate the form with values from an existing trigger"""
        self.trigger_input.value = self.trigger.trigger_name
        self.name_input.value = self.trigger.process_name
        self.path_input.value = self.trigger.process_path
        self.args_input.value = self.trigger.process_args
        self.git_check.value = self.trigger.is_git_repo
        self.blocking_check.value = self.trigger.is_blocking

        if self.trigger_type == TriggerType.SINGLE:
            self.time_input.set_datetime(self.trigger.next_run)

        elif self.trigger_type == TriggerType.SCHEDULED:
            self.cron_input.value = self.trigger.cron_expr

        elif self.trigger_type == TriggerType.QUEUE:
            self.queue_input.value = self.trigger.queue_name
            self.batch_input.value = self.trigger.min_batch_size

    def _disable_unused(self):
        """Disable all inputs that aren't being used by the current trigger type."""
        if self.trigger_type != TriggerType.SINGLE:
            self.time_input.visible = False

        if self.trigger_type != TriggerType.SCHEDULED:
            self.cron_input.visible = False

        if self.trigger_type != TriggerType.QUEUE:
            self.queue_input.visible = False
            self.batch_input.visible = False

    async def _create_trigger(self):
        """Creates a new single trigger in the database using the data entered in the UI.
        If an existing trigger was given when creating the popup it is updated instead.
        """
        trigger_name = self.trigger_input.value
        process_name = self.name_input.value
        next_run = self.time_input.get_datetime()
        cron_expr = self.cron_input.value
        queue_name = self.queue_input.value
        min_batch_size = self.batch_input.value
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

        if self.trigger_type == TriggerType.SINGLE:
            if next_run < datetime.now():
                if not await generic_popups.question_popup(
                        "The selected datetime is in the past. Do you want to create the trigger anyway?",
                        "Create", "Cancel"):
                    return

        if self.trigger_type == TriggerType.SCHEDULED:
            try:
                cron_iter = croniter(cron_expr, datetime.now())
                next_run = cron_iter.get_next(datetime)
            except CroniterBadCronError as exc:
                ui.notify(f"Please enter a valid cron expression: {exc}", type='negative', timeout=0, close_button='Dismiss')
                return

        if self.trigger_type == TriggerType.QUEUE:
            if not queue_name:
                ui.notify("Please enter a queue name.", type='negative')
                return

        if not path:
            ui.notify('Please enter a process path', type='negative')
            return

        if self.trigger is None:
            # Create new trigger in database
            if self.trigger_type == TriggerType.SINGLE:
                db_util.create_single_trigger(trigger_name, process_name, next_run, path, args, is_git, is_blocking)
            elif self.trigger_type == TriggerType.SCHEDULED:
                db_util.create_scheduled_trigger(trigger_name, process_name, cron_expr, next_run, path, args, is_git, is_blocking)
            elif self.trigger_type == TriggerType.QUEUE:
                db_util.create_queue_trigger(trigger_name, process_name, queue_name, path, args, is_git, is_blocking, min_batch_size)

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

            if self.trigger_type == TriggerType.SINGLE:
                self.trigger.next_run = next_run
            elif self.trigger_type == TriggerType.SCHEDULED:
                self.trigger.cron_expr = cron_expr
                self.trigger.next_run = next_run
            elif self.trigger_type == TriggerType.QUEUE:
                self.trigger.queue_name = queue_name
                self.trigger.min_batch_size = min_batch_size

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