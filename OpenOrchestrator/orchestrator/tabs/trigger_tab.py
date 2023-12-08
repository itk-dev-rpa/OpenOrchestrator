"""This module is responsible for the layout and functionality of the Trigger tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger, ScheduledTrigger, QueueTrigger
from OpenOrchestrator.orchestrator.popups.single_trigger_popup import SingleTriggerPopup
from OpenOrchestrator.orchestrator.popups.queue_trigger_popup import QueueTriggerPopup
from OpenOrchestrator.orchestrator.popups.scheduled_trigger_popup import ScheduledTriggerPopup

COLUMNS = ("Trigger Name", "Type", "Status", "Process Name", "Last Run", "Next Run", "ID")


class TriggerTab():
    """The 'Trigger' tab object. It contains tables and buttons for dealing with triggers."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                ui.button("New Single Trigger", icon="add", on_click=lambda e: SingleTriggerPopup(self))
                ui.button("New Scheduled Trigger", icon="add", on_click=lambda e: ScheduledTriggerPopup())
                ui.button("New Queue Trigger", icon="add", on_click=lambda e: QueueTriggerPopup())

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in COLUMNS]
            self.trigger_table = ui.table(columns, [], title="Triggers", pagination=10, row_key='ID').classes("w-full")
            self.trigger_table.on('rowClick', self._row_click)

    def _row_click(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        trigger_id = row["ID"]
        trigger = db_util.get_trigger(trigger_id)

        if isinstance(trigger, SingleTrigger):
            SingleTriggerPopup(self, trigger)

    def update(self):
        """Updates the tab and it's data."""
        triggers = db_util.get_all_triggers()
        self.trigger_table.rows = [t.to_row_dict() for t in triggers]
        self.trigger_table.update()
