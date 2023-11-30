"""This module is responsible for the layout and functionality of the Trigger tab
in Orchestrator."""

import uuid

from nicegui import ui

from OpenOrchestrator.orchestrator.popups.single_trigger import SingleTriggerPopup
from OpenOrchestrator.orchestrator.popups.queue_trigger import QueueTriggerPopup
from OpenOrchestrator.orchestrator.popups.scheduled_trigger import ScheduledTriggerPopup

COLUMNS = ("Trigger Name", "Type", "Status", "Process Name", "Last Run", "Path", "Arguments", "Is Git", "Is Blocking", "ID")

class TriggerTab():
    def __init__(self, tab: ui.tab) -> None:
        with ui.tab_panel(tab):
            with ui.row():
                ui.button("New Scheduled Trigger", icon="add", on_click=lambda e: ScheduledTriggerPopup())
                ui.button("New Queue Trigger", icon="add", on_click=lambda e: QueueTriggerPopup())
                ui.button("New Single Trigger", icon="add", on_click=lambda e: SingleTriggerPopup())

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in COLUMNS]
            self.trigger_table = ui.table(columns, [], title="Triggers", pagination=10, row_key='ID').classes("w-full")
            self.trigger_table.on('rowClick', self.row_click)

        self.update_table()

    def update_table(self):
        """Update the rows of the table."""
        rows = [
            {
                "Trigger Name": "Trigger"+str(i),
                "Type": ("Scheduled", "Queue", "Single")[hash(i) % 3],
                "Status": "Idle",
                "Process Name": "Process",
                "Last Run": "dd-mm-yyyy",
                "Path": "path to narnia",
                "Arguments": "Nop",
                "Is Git": "True",
                "Is Blocking": "False",
                "ID": uuid.uuid4()
            }
            for i in range(100)
        ]
        self.trigger_table.rows = rows

    def row_click(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        ui.notify(row)
