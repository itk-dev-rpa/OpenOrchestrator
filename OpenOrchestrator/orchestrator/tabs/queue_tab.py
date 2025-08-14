"""This module is responsible for the layout and functionality of the Queues tab
in Orchestrator."""
from datetime import datetime

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.orchestrator.popups.queue_popup import QueueElementPopup


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
    {'name': "Data", 'label': "Data", 'field': "Data", 'align': 'left', 'sortable': True, 'style': 'max-width: 200px; overflow: hidden; text-overflow: ellipsis;'},
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

        for row in rows:
            for date_field in ['Created Date', 'Start Date', 'End Date']:
                if row.get(date_field):
                    row[date_field] = datetime.strptime(row[date_field], '%d-%m-%Y %H:%M:%S')

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
        self.order_by = "Created Date"
        self.order_descending = False
        self.page = 1
        self.rows_per_page = 25
        self.queue_count = 100

        with ui.dialog(value=True).props('full-width full-height') as dialog, ui.card():
            with ui.row().classes("w-full"):
                self.ref_search = ui.input(label='Search', placeholder="Reference", on_change=self._update).style('margin-left: 1rem')
                self.status_select = ui.select(
                    options= {'All': 'All'} | {status.name: status.value for status in QueueStatus},
                    label="Status",
                    value="All",
                    on_change=self._update).classes("w-24")
                self.from_input = DatetimeInput("From Date", on_change=self._update, allow_empty=True)
                self.to_input = DatetimeInput("To Date", on_change=self._update, allow_empty=True)

                ui.space()

                ui.switch("Dense", on_change=lambda e: self._dense_table(e.value))
                self._create_column_filter()
                ui.button(icon='refresh', on_click=self._update)
                self.close_button = ui.button(icon="close", on_click=dialog.close)
            with ui.scroll_area().classes("h-full"):
                self.table = ui.table(columns=ELEMENT_COLUMNS, rows=[], row_key='ID', title=queue_name, pagination={'rowsPerPage': 5, 'rowsNumber': 100}).classes("w-full sticky-header h-[calc(100vh-200px)] overflow-auto")
                self.table.on('rowClick', lambda e: QueueElementPopup(e.args[1]))
                self.table.on('request', self._on_table_request)

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
        ref_search = self.ref_search.value.strip()
        if len(ref_search) == 0:
            ref_search = None
        status = None if self.status_select.value == "All" else self.status_select.value.strip()

        from_date = self.from_input.get_datetime()
        to_date = self.to_input.get_datetime()
        offset = (self.page - 1) * self.rows_per_page
        order_by = str(self.order_by).lower().replace(" ", "_")

        queue_elements, queue_count = db_util.get_queue_elements(self.queue_name, status=status, limit=self.rows_per_page, from_date=from_date, to_date=to_date, order_by=order_by, order_desc=self.order_descending, offset=offset, search_term=ref_search, include_count=True)
        self._update_pagination(queue_count)
        rows = [element.to_row_dict() for element in queue_elements]
        self.table.update_rows(rows)

    def _filter_status(self, status: QueueStatus, dropdown: ui.dropdown_button):
        """Show only elements of the selected status, and update the status dropdown.

        Args:
            status: QueueStatus to show.
        """
        dropdown.text = status.value

    def _on_table_request(self, e):
        """Called when updating table pagination and sorting, to handle these manually and allow for server side pagination.

        Args:
            e: The event triggering the request.
        """
        pagination = e.args['pagination']
        self.page = pagination.get('page')
        self.rows_per_page = pagination.get('rowsPerPage')
        self.order_by = pagination.get('sortBy')
        self.order_descending = pagination.get('descending', False)
        self._update()

    def _update_pagination(self, queue_count):
        """Update pagination element.

        Args:
            queue_count: The element count of the current filtered table.
        """
        self.queue_count = queue_count
        self.table.pagination = {"rowsNumber": self.queue_count, "page": self.page, "rowsPerPage": self.rows_per_page, "sortBy": self.order_by, "descending": self.order_descending}
