"""This module is responsible for the layout and functionality of the Schedulers tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.orchestrator.tabs.logging_tab import LoggingTab

COLUMNS = [
    {'name': "job_id", 'label': "ID", 'field': "ID", 'headerClasses': 'hidden', 'classes': 'hidden'},
    {'name': "process_name", 'label': "Process Name", 'field': "Process Name", 'align': 'left', 'sortable': True},
    {'name': "scheduler_name", 'label': "Scheduler", 'field': "Scheduler", 'align': 'left', 'sortable': True},
    {'name': "trigger_time", 'label': "Trigger Time", 'field': "Trigger Time", 'align': 'left', 'sortable': True},
    {'name': "status", 'label': "Status", 'field': "Status", 'align': 'left', 'sortable': True},
    {'name': "logs", 'label': "Logs", 'field': "Logs", 'align': 'left', 'sortable': False},
]


class JobsTab():
    """A class for the jobs tab."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            self.jobs_table = ui.table(title="Jobs", columns=COLUMNS, rows=[], row_key='job_id', pagination=50).classes("w-full")
            self.jobs_table.on("rowClick", self._row_click)
        test_helper.set_automation_ids(self, "jobs_tab")
        self.logging_tab = None

    def set_log_tab(self, log_tab: LoggingTab):
        self.logging_tab = log_tab

    def update(self):
        """Updates the tables on the tab."""
        jobs = db_util.get_jobs()
        self.jobs_table.rows = [s.to_row_dict() for s in jobs]

    def _row_click(self, event):
        row = event.args[1]
        print(event.args)
        job_id = row["ID"]
        self.logging_tab.job_input = job_id
        self.logging_tab.update()
