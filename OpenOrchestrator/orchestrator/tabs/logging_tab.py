"""This module is responsible for the layout and functionality of the Logging tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.orchestrator import test_helper


COLUMNS = [
    {'name': "Log Time", 'label': "Log Time", 'field': "Log Time", 'align': 'left', 'sortable': True},
    {'name': "Process Name", 'label': "Process Name", 'field': "Process Name", 'align': 'left'},
    {'name': "Level", 'label': "Level", 'field': "Level", 'align': 'left'},
    {'name': "Message", 'label': "Message", 'field': "Message", 'align': 'left', ':format': 'value => value.length < 100 ? value : value.substring(0, 100)+"..."'},
    {'name': "ID", 'label': "ID", 'field': "ID", 'headerClasses': 'hidden', 'classes': 'hidden'}
]


# pylint: disable-next=too-few-public-methods
class LoggingTab():
    """The 'Logs' tab object."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                self.from_input = DatetimeInput("From Date", on_change=self.update, allow_empty=True)
                self.to_input = DatetimeInput("To Date", on_change=self.update, allow_empty=True)
                self.process_input = ui.select(["All"], label="Process Name", value="All", on_change=self.update).classes("w-48")
                self.level_input = ui.select(["All", "Trace", "Info", "Error"], value="All", label="Level", on_change=self.update).classes("w-48")
                self.limit_input = ui.select([100, 200, 500, 1000], value=100, label="Limit", on_change=self.update).classes("w-24")

            self.logs_table = ui.table(title="Logs", columns=COLUMNS, rows=[], row_key='ID', pagination=50).classes("w-full")
            self.logs_table.on("rowClick", self._row_click)

        test_helper.set_automation_ids(self, "logs_tab")

    def update(self):
        """Update the logs table and Process input list"""
        self._update_table()
        self._update_process_input()

    def _update_table(self):
        """Update the table with logs from the database applying the filters."""
        from_date = self.from_input.get_datetime()
        to_date = self.to_input.get_datetime()
        process_name = self.process_input.value if self.process_input.value != 'All' else None
        level = LogLevel(self.level_input.value) if self.level_input.value != "All" else None
        limit = self.limit_input.value

        logs = db_util.get_logs(0, limit=limit, from_date=from_date, to_date=to_date, log_level=level, process_name=process_name)
        self.logs_table.rows = [log.to_row_dict() for log in logs]

    def _update_process_input(self):
        """Update the process input with names from the database."""
        process_names = list(db_util.get_unique_log_process_names())
        process_names.insert(0, "All")
        self.process_input.options = process_names
        self.process_input.update()

    def _row_click(self, event):
        """Display a dialog with info on the clicked log."""
        row = event.args[1]
        with ui.dialog(value=True), ui.card():
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
