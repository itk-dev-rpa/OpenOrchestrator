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
    """A popup for creating/updating triggers."""
    def __init__(self, trigger_tab: TriggerTab, trigger_type: TriggerType, trigger: Trigger = None):
        """Create a new popup.
        If a trigger is given it will be updated instead of creating a new trigger.

        Args:
            trigger_tab: The tab parent of the popup.
            trigger_type: The type of trigger popup to show.
            trigger: The Trigger to update if any.
        """
        self.trigger_tab = trigger_tab
        self.trigger_type = trigger_type
        self.trigger = trigger
        title = f'Update {trigger_type.value} Trigger' if trigger else f'New {trigger_type.value} Trigger'

        with ui.dialog(value=True) as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.trigger_input = ui.input("Trigger Name").classes("w-full")
            self.name_input = ui.input("Process Name").classes("w-full")
            self.cron_input = ui.input("Cron expression", on_change=self._cron_change).classes("w-full")  # For scheduled triggers
            self.time_input = DatetimeInput("Trigger Time")  # For scheduled/single triggers
            with self.cron_input:
                with ui.link(target="https://crontab.guru/", new_tab=True):
                    with ui.button(icon="help").props("flat dense"):
                        ui.tooltip("Help with cron: https://crontab.guru/")
            self.queue_input = ui.input("Queue Name").classes("w-full")  # For queue triggers
            self.batch_input = ui.number("Min Batch Size", value=1, min=1, precision=0, format="%.0f")  # For queue triggers
            self.path_input = ui.input("Process Path").classes("w-full")
            self.git_check = ui.checkbox("Is path a Git Repo?")
            self.args_input = ui.input("Process Arguments").classes("w-full")
            self.blocking_check = ui.checkbox("Is process blocking?")

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
        self._define_validation()

        if trigger:
            self._pre_populate()

    def _define_validation(self):
        self.trigger_input.validation = {"Please enter a trigger name.": bool}
        self.name_input.validation = {"Please enter a process name.": bool}
        self.path_input.validation = {"Please enter a process path.": bool}
        self.queue_input.validation = {"Please enter a queue name.": bool}

        def validate_cron(value: str):
            try:
                croniter(value)
                return True
            except CroniterBadCronError:
                return False

        self.cron_input.validation = {"Invalid cron expression.": validate_cron}

    def _pre_populate(self):
        """Populate the form with values from an existing trigger"""
        self.trigger_input.value = self.trigger.trigger_name
        self.name_input.value = self.trigger.process_name
        self.path_input.value = self.trigger.process_path
        self.args_input.value = self.trigger.process_args
        self.git_check.value = self.trigger.is_git_repo
        self.blocking_check.value = self.trigger.is_blocking

        if self.trigger_type == TriggerType.SCHEDULED:
            self.cron_input.value = self.trigger.cron_expr

        if self.trigger_type in (TriggerType.SINGLE, TriggerType.SCHEDULED):
            self.time_input.set_datetime(self.trigger.next_run)

        if self.trigger_type == TriggerType.QUEUE:
            self.queue_input.value = self.trigger.queue_name
            self.batch_input.value = self.trigger.min_batch_size

    def _disable_unused(self):
        """Disable all inputs that aren't being used by the current trigger type."""
        if self.trigger_type == TriggerType.QUEUE:
            self.time_input.visible = False

        if self.trigger_type != TriggerType.SCHEDULED:
            self.cron_input.visible = False

        if self.trigger_type != TriggerType.QUEUE:
            self.queue_input.visible = False
            self.batch_input.visible = False

    def _cron_change(self):
        if self.cron_input.validate():
            cron_iter = croniter(self.cron_input.value, datetime.now())
            self.time_input.set_datetime(cron_iter.next(datetime))

    async def _validate(self) -> bool:
        result = True

        result &= self.trigger_input.validate()
        result &= self.name_input.validate()
        result &= self.path_input.validate()

        if self.trigger_type in (TriggerType.SINGLE, TriggerType.SCHEDULED):
            result &= self.time_input.validate()

            next_run = self.time_input.get_datetime()
            if next_run and next_run < datetime.now():
                result &= await generic_popups.question_popup(
                        "The selected datetime is in the past. Do you want to create the trigger anyway?",
                        "Create", "Cancel")

        if self.trigger_type == TriggerType.SCHEDULED:
            result &= self.cron_input.validate()

        if self.trigger_type == TriggerType.QUEUE:
            result &= self.queue_input.validate()

        return result

    async def _create_trigger(self):
        """Creates a new single trigger in the database using the data entered in the UI.
        If an existing trigger was given when creating the popup it is updated instead.
        """
        if not await self._validate():
            ui.notify("Please fill out required information.", type='warning')
            return

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
        if await generic_popups.question_popup(f"Delete trigger '{self.trigger.trigger_name}'?", "Delete", "Cancel", color1='red'):
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
