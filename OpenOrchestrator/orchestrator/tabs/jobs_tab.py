"""This module is responsible for the layout and functionality of the Schedulers tab
in Orchestrator."""

from nicegui import ui
from typing import Callable

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator import test_helper

COLUMNS = [
    {'name': "job_id", 'label': "ID", 'field': "ID", 'headerClasses': 'hidden', 'classes': 'hidden'},
    {'name': "process_name", 'label': "Process Name", 'field': "Process Name", 'align': 'left', 'sortable': True},
    {'name': "scheduler_name", 'label': "Scheduler", 'field': "Scheduler", 'align': 'left', 'sortable': True},
    {'name': "start_time", 'label': "Start Time", 'field': "Start Time", 'align': 'left', 'sortable': True},
    {'name': "end_time", 'label': "End Time", 'field': "End Time", 'align': 'left', 'sortable': True},
    {'name': "status", 'label': "Status", 'field': "Status", 'align': 'left', 'sortable': True}
]


class JobsTab():
    """A class for the jobs tab."""
    def __init__(self, tab_name: str, on_job_click: Callable[[str], None]) -> None:
        with ui.tab_panel(tab_name):
            self.jobs_table = ui.table(title="Jobs", columns=COLUMNS, rows=[], row_key='job_id', pagination=50).classes("w-full")
            self.jobs_table.on("rowClick", self._row_click)
            self.add_column_colors()
        test_helper.set_automation_ids(self, "jobs_tab")
        self.on_job_click = on_job_click

    def update(self):
        """Updates the tables on the tab."""
        jobs = db_util.get_jobs()
        self.jobs_table.rows = [s.to_row_dict() for s in jobs]

    def _row_click(self, event):
        row = event.args[1]
        job_id = row["ID"]
        self.on_job_click(job_id)

    def add_column_colors(self):
        """Add custom coloring to the jobs table."""
        # Add coloring to the status column
        color_dict = "{Running: 'blue', Done: 'green', Failed: 'red', Killed: 'grey-9'}"

        self.jobs_table.add_slot(
            "body-cell-status",
            f'''
            <q-td key="status" :props="props">
                <q-badge v-if="{color_dict}[props.value]" :color="{color_dict}[props.value]">
                    {{{{props.value}}}}
                </q-badge>
                <p v-else>
                    {{{{props.value}}}}
                </p>
            </q-td>
            '''
        )
