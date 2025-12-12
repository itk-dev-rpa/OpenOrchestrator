"""This module is responsible for the layout and functionality of the Logging tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.orchestrator import test_helper


COLUMNS = [
    {'name': "Log Time", 'label': "Log Time", 'field': "Log Time", 'align': 'left', 'sortable': True},
    {'name': "Level", 'label': "Level", 'field': "Level", 'align': 'left'},
    {'name': "Short Job ID", 'label': "Job ID", 'field': "Short Job ID", 'align': 'left', 'sortable': True},
    {'name': "Process Name", 'label': "Process Name", 'field': "Process Name", 'align': 'left', 'sortable': True},
    {'name': "Message", 'label': "Message", 'field': "Message", 'align': 'left', ':format': 'value => value.length < 100 ? value : value.substring(0, 100)+"..."'},
    {'name': "Full Job ID", 'label': "Full Job ID", 'field': "Full Job ID", 'headerClasses': 'hidden', 'classes': 'hidden'},
    {'name': "ID", 'label': "ID", 'field': "ID", 'headerClasses': 'hidden', 'classes': 'hidden'}
]


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class LoggingTab():
    """The 'Logs' tab object."""
    def __init__(self, tab_name: str) -> None:
        self.current_job_id: str | None = None
        self.order_by = "Log Time"
        self.order_descending = True
        self.page = 1
        self.rows_per_page = 25
        self.log_count = 0

        with ui.tab_panel(tab_name):
            with ui.row().classes("w-full justify-between"):
                with ui.row():
                    self.from_input = DatetimeInput("From Date", on_change=self.update, allow_empty=True)
                    self.to_input = DatetimeInput("To Date", on_change=self.update, allow_empty=True)
                    self.level_input = ui.select(["All", "Trace", "Info", "Error"], value="All", label="Level", on_change=self.update).classes("w-48")
                    self.process_input = ui.select(["All"], label="Process Name", value="All", on_change=self.update).classes("w-48")
                    with ui.column().classes("items-end") as self.job_filter_container:
                        self.job_filter_label = ui.label("")
                        self.all_jobs_button = ui.button("Show all jobs", on_click=self._show_all_jobs)

                self.logs_table = ui.table(title="Logs", columns=COLUMNS, rows=[], row_key='ID',
                                           pagination={'rowsPerPage': self.rows_per_page,
                                                       'rowsNumber': self.log_count})
                self.logs_table.classes("w-full sticky-header h-[calc(100vh-200px)] overflow-auto")
                self.logs_table.props(":rows-per-page-options='[10, 25, 50, 100, 1000]' rows-per-page-label='Logs per page:'")
                self.logs_table.on("rowClick", self._row_click)
                self.logs_table.on('request', self._on_table_request)

            test_helper.set_automation_ids(self, "logs_tab")

    def update(self):
        """Update the logs table and Process input list"""
        self._update_table()
        self._update_process_input()
        self._update_job_filter_display()

    def _update_job_filter_display(self):
        """Update visibility and text of job filter."""
        if self.current_job_id:
            self.job_filter_label.set_text(f"Filtering by Job: {self.current_job_id}...")
            self.job_filter_container.set_visibility(True)
        else:
            self.job_filter_container.set_visibility(False)

    def _update_table(self):
        """Update the table with logs from the database applying the filters."""
        from_date = self.from_input.get_datetime()
        to_date = self.to_input.get_datetime()
        level = LogLevel(self.level_input.value) if self.level_input.value != "All" else None
        process_name = self.process_input.value if self.process_input.value != 'All' else None

        offset = (self.page - 1) * self.rows_per_page
        order_by = str(self.order_by).lower().replace(" ", "_")

        logs, count = db_util.get_logs(offset, limit=self.rows_per_page, from_date=from_date, to_date=to_date, log_level=level, process_name=process_name, job_id=self.current_job_id, order_by=order_by, order_desc=self.order_descending, include_count=True)
        self._update_pagination(count)
        self.logs_table.update_rows([log.to_row_dict() for log in logs])

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
        self._update_table()

    def _update_pagination(self, log_count):
        """Update pagination element.

        Args:
            log_count: The element count of the current filtered table.
        """
        self.log_count = log_count
        self.logs_table.pagination = {"rowsNumber": self.log_count,
                                      "page": self.page,
                                      "rowsPerPage": self.rows_per_page,
                                      "sortBy": self.order_by,
                                      "descending": self.order_descending}
        self.logs_table.update()

    def _update_process_input(self):
        """Update the process input with names from the database."""
        process_names = list(db_util.get_unique_log_process_names())
        process_names.insert(0, "All")
        self.process_input.options = process_names
        self.process_input.update()

    def set_job_filter(self, job_id: str | None):
        """Set filter to specific job."""
        self.current_job_id = job_id
        self.update()

    def _show_all_jobs(self):
        self.set_job_filter(None)

    def _row_click(self, event):
        """Display a dialog with info on the clicked log."""
        row = event.args[1]
        with ui.dialog(value=True) as dialog, ui.card():
            ui.label("Log ID:").classes("font-bold")
            ui.label(row['ID'])
            ui.label("Log Time:").classes("font-bold")
            ui.label(row['Log Time'])
            ui.label("Process Name:").classes("font-bold")
            ui.label(row['Process Name'])
            ui.label("Log Level:").classes("font-bold")
            ui.label(row['Level'])
            ui.label("Message:").classes("font-bold")
            ui.html(f"<pre>{row['Message']}</pre>")
            ui.label("Job ID:").classes("font-bold")
            ui.label(row['Full Job ID'])
            with ui.row():
                ui.button("Show job logs", on_click=lambda: [self.set_job_filter(row['Full Job ID']), dialog.close()]).set_enabled(row['Full Job ID'] is not None)
                ui.button("Close", on_click=dialog.close)
