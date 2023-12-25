"""This module is responsible for the layout and functionality of the Queues tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueStatus


COLUMNS = (
    {'name': "Queue Name", 'label': "Queue Name", 'field': "Queue Name", 'align': 'left', 'sortable': True},
    {'name': "New", 'label': "New", 'field': "New", 'align': 'left', 'sortable': True},
    {'name': "In Progress", 'label': "In Progress", 'field': "In Progress", 'align': 'left', 'sortable': True},
    {'name': "Done", 'label': "Done", 'field': "Done", 'align': 'left', 'sortable': True},
    {'name': "Failed", 'label': "Failed", 'field': "Failed", 'align': 'left', 'sortable': True}
)


# pylint: disable-next=too-few-public-methods
class QueueTab():
    """The 'Queues' tab object. It contains tables and buttons for dealing with queues."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            self.queue_table = ui.table(title="Queues", columns=COLUMNS, rows=[], row_key='Queue Name').classes("w-full")

    def update(self):
        """Update the queue table with data from the database."""
        queue_count = db_util.get_queue_count()

        # Convert queue count to row elements
        rows = []
        for queue_name, count in queue_count.items():
            row = {
                "Queue Name": queue_name,
                "New": count.get(QueueStatus.NEW, 0),
                "In Progress": count.get(QueueStatus.IN_PROGRESS, 0),
                "Done": count.get(QueueStatus.DONE, 0),
                "Failed": count.get(QueueStatus.FAILED, 0)
            }
            rows.append(row)

        self.queue_table.update_rows(rows)
