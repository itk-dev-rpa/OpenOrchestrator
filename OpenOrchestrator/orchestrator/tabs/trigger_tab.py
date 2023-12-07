"""This module is responsible for the layout and functionality of the Trigger tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups.single_trigger import SingleTriggerPopup
from OpenOrchestrator.orchestrator.popups.queue_trigger import QueueTriggerPopup
from OpenOrchestrator.orchestrator.popups.scheduled_trigger import ScheduledTriggerPopup

COLUMNS = ("Trigger Name", "Type", "Status", "Process Name", "Last Run", "Path", "Arguments", "Is Git", "Is Blocking", "ID")


class TriggerTab():
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                ui.button("New Scheduled Trigger", icon="add", on_click=lambda e: ScheduledTriggerPopup())
                ui.button("New Queue Trigger", icon="add", on_click=lambda e: QueueTriggerPopup())
                ui.button("New Single Trigger", icon="add", on_click=lambda e: SingleTriggerPopup())

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in COLUMNS]
            self.trigger_table = ui.table(columns, [], title="Triggers", pagination=10, row_key='ID').classes("w-full")
            self.trigger_table.on('rowClick', self.row_click)

    def update_table(self):
        """Update the rows of the table."""
        triggers = db_util.get_all_triggers()
        self.trigger_table.rows = [t.to_row_dict() for t in triggers]
        self.trigger_table.update()

    def row_click(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        ui.notify(row)

    def update(self):
        self.update_table()
