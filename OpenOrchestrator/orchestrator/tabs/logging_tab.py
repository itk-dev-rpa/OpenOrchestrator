"""This module is responsible for the layout and functionality of the Logging tab
in Orchestrator."""


from datetime import datetime
from ast import literal_eval

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput


COLUMNS = (
    {'name': "Log Time", 'label': "Log Time", 'field': "Log Time", 'align': 'left', 'sortable': True},
    {'name': "Process Name", 'label': "Process Name", 'field': "Process Name", 'align': 'left'},
    {'name': "Level", 'label': "Level", 'field': "Level", 'align': 'left'},
    {'name': "Message", 'label': "Message", 'field': "Message", 'align': 'left', ':format': 'value => value.length < 100 ? value : value.substring(0, 100)+"..."'},
    {'name': "ID", 'label': "ID", 'field': "ID", 'headerClasses': 'hidden', 'classes': 'hidden'}
)


class LoggingTab():
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                self.from_input = DatetimeInput("From Date")
                self.to_input = DatetimeInput("To Date")
                self.process_input = ui.select([], label="Process Name").classes("w-48")
                self.level_input = ui.select(["", "Trace", "Info", "Error"], label="Level").classes("w-48")
                ui.button("Update", on_click=self.update)

            self.logs_table = ui.table(title="Logs", columns=COLUMNS, rows=[], row_key='ID').classes("w-full")
            self.logs_table.on("rowClick", self._row_click)

    def update(self):
        """Update the logs table and Process input list"""
        self._update_table()
        self._update_process_input()

    def _update_table(self):
        from_date = self.from_input.get_datetime()
        to_date = self.to_input.get_datetime()
        process_name = self.process_input.value
        level = self.level_input.value

        logs = db_util.get_logs(0, 100, from_date=from_date, to_date=to_date, log_level=level, process_name=process_name)
        self.logs_table.rows = [log.to_row_dict() for log in logs]

    def _update_process_input(self):
        process_names = list(db_util.get_unique_log_process_names())
        process_names.insert(0, "")
        self.process_input.options = process_names
        self.process_input.update()

    def _row_click(self, event):
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
            for line in row['Message'].splitlines():
                ui.label(line)
