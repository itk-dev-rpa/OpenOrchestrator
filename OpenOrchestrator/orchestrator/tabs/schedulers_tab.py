"""This module is responsible for the layout and functionality of the Schedulers tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator import test_helper

COLUMNS = [
    {'name': "machine_name", 'label': "Machine Name", 'field': "Machine Name", 'align': 'left', 'sortable': True},
    {'name': "last_connection", 'label': "Last Connection", 'field': "Last Connection", 'align': 'left', 'sortable': True},
    {'name': "latest_trigger", 'label': "Latest Trigger", 'field': "Latest Trigger", 'align': 'left', 'sortable': True},
    {'name': "latest_trigger_time", 'label': "Latest Trigger Time", 'field': "Latest Trigger Time", 'align': 'left', 'sortable': True},
]


class SchedulerTab():
    """A class for the scheduler tab."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            self.schedulers_table = ui.table(title="Schedulers", columns=COLUMNS, rows=[], row_key='Machine Name', pagination=50).classes("w-full")
            self.add_column_colors()
        test_helper.set_automation_ids(self, "schedulers_tab")

    def update(self):
        """Updates the tables on the tab."""
        schedulers = db_util.get_schedulers()
        self.schedulers_table.rows = [s.to_row_dict() for s in schedulers]
        self.schedulers_table.update()

    def add_column_colors(self):
        """Add red coloring to the scheduler if more than a minute has passed since last ping."""
        self.schedulers_table.add_slot(
            "body-cell-last_connection",
            '''
            <q-td key="last_connection" :props="props">
                <q-badge v-if="(new Date() - new Date(+props.value.substr(6,4), +props.value.substr(3,2)-1, +props.value.substr(0,2), +props.value.substr(11,2), +props.value.substr(14,2))) > 60 * 1000" color='red'>
                    {{props.value}}
                </q-badge>
                <p v-else>
                    {{props.value}}
                </p>
            </q-td>
            '''
        )
