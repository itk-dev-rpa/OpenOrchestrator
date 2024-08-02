"""This module is responsible for the layout and functionality of the Queues tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.orchestrator import test_helper


QUEUE_COLUMNS = [
    {'name': "Queue Name", 'label': "Queue Name", 'field': "Queue Name", 'align': 'left', 'sortable': True},
    {'name': "New", 'label': "New", 'field': "New", 'align': 'left', 'sortable': True},
    {'name': "In Progress", 'label': "In Progress", 'field': "In Progress", 'align': 'left', 'sortable': True},
    {'name': "Done", 'label': "Done", 'field': "Done", 'align': 'left', 'sortable': True},
    {'name': "Failed", 'label': "Failed", 'field': "Failed", 'align': 'left', 'sortable': True},
    {'name': "Abandoned", 'label': "Abandoned", 'field': "Abandoned", 'align': 'left', 'sortable': True}
]

ELEMENT_COLUMNS = [
    {'name': "Reference", 'label': "Reference", 'field': "Reference", 'align': 'left', 'sortable': True},
    {'name': "Status", 'label': "Status", 'field': "Status", 'align': 'left', 'sortable': True},
    {'name': "Data", 'label': "Data", 'field': "Data", 'align': 'left', 'sortable': True},
    {'name': "Message", 'label': "Message", 'field': "Message", 'align': 'left', 'sortable': True},
    {'name': "Created Date", 'label': "Created Date", 'field': "Created Date", 'align': 'left', 'sortable': True},
    {'name': "Start Date", 'label': "Start Date", 'field': "Start Date", 'align': 'left', 'sortable': True},
    {'name': "End Date", 'label': "End Date", 'field': "End Date", 'align': 'left', 'sortable': True},
    {'name': "Created By", 'label': "Created By", 'field': "Created By", 'align': 'left', 'sortable': True},
    {'name': "ID", 'label': "ID", 'field': "ID", 'align': 'left', 'sortable': True}
]


# pylint: disable-next=too-few-public-methods
class QueueTab():
    """The 'Queues' tab object. It contains tables and buttons for dealing with queues."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            self.queue_table = ui.table(title="Queues", columns=QUEUE_COLUMNS, rows=[], row_key='Queue Name', pagination={'rowsPerPage': 50, 'sortBy': 'Queue Name'}).classes("w-full")
            self.queue_table.on("rowClick", self._row_click)
        test_helper.set_automation_ids(self, "queues_tab")

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
                "Failed": count.get(QueueStatus.FAILED, 0),
                "Abandoned": count.get(QueueStatus.ABANDONED, 0),
            }
            rows.append(row)

        self.queue_table.update_rows(rows)

    def _row_click(self, event):
        row = event.args[1]
        queue_name = row["Queue Name"]
        QueuePopup(queue_name)


# pylint: disable-next=too-few-public-methods
class QueuePopup():
    """A popup that displays queue elements in a queue."""
    def __init__(self, queue_name) -> None:
        self.queue_name = queue_name

        with ui.dialog(value=True).props('full-width full-height') as dialog, ui.card():
            with ui.row().classes("w-full"):
                self.from_input = DatetimeInput("From Date", on_change=self._update, allow_empty=True).style('margin-left: 1rem')
                self.to_input = DatetimeInput("To Date", on_change=self._update, allow_empty=True)

                self.limit_select = ui.select(
                    options=[100, 200, 500, 1000, "All"],
                    label="Limit",
                    value=100,
                    on_change=self._update).classes("w-24")

                ui.space()

                ui.switch("Dense", on_change=lambda e: self._dense_table(e.value))
                self._create_column_filter()
                ui.button(icon='refresh', on_click=self._update)
                self.close_button = ui.button(icon="close", on_click=dialog.close)
            with ui.scroll_area().classes("h-full"):
                self.table = ui.table(columns=ELEMENT_COLUMNS, rows=[], row_key='ID', title=queue_name, pagination=100).classes("w-full")

        self._update()
        test_helper.set_automation_ids(self, "queue_popup")

    def _dense_table(self, value: bool):
        """Change if the table is dense or not."""
        if value:
            self.table.props("dense")
        else:
            self.table.props(remove="dense")

    def _create_column_filter(self):
        """Create a menu with switches for toggling columns on and off."""
        def toggle(column: dict, visible: bool) -> None:
            column['classes'] = '' if visible else 'hidden'
            column['headerClasses'] = '' if visible else 'hidden'
            self.table.update()

        with ui.button("Columns", icon="menu"):
            with ui.menu(), ui.column().classes('gap-0 p-2'):
                for column in ELEMENT_COLUMNS:
                    ui.switch(column['label'], value=True, on_change=lambda e, column=column: toggle(column, e.value))

    def _update(self):
        """Update the table with values from the database."""
        limit = self.limit_select.value
        if limit == 'All':
            limit = 1_000_000_000

        from_date = self.from_input.get_datetime()
        to_date = self.to_input.get_datetime()

        queue_elements = db_util.get_queue_elements(self.queue_name, limit=limit, from_date=from_date, to_date=to_date)
        rows = [element.to_row_dict() for element in queue_elements]
        self.table.update_rows(rows)
