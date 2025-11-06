"""This module is responsible for the layout and functionality of the Trigger tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger, ScheduledTrigger, QueueTrigger, TriggerType
from OpenOrchestrator.orchestrator.popups.trigger_popup import TriggerPopup
from OpenOrchestrator.orchestrator import test_helper

COLUMNS = [
    {'name': "Trigger Name", 'label': "Trigger Name", 'field': "Trigger Name", 'align': 'left', 'sortable': True},
    {'name': "Priority", 'label': "Priority", 'field': "Priority", 'align': 'left', 'sortable': True, ':sort': '(a, b, rowA, rowB) => b-a'},
    {'name': "Type", 'label': "Type", 'field': "Type", 'align': 'left', 'sortable': True},
    {'name': "Status", 'label': "Status", 'field': "Status", 'align': 'left', 'sortable': True},
    {'name': "Process Name", 'label': "Process Name", 'field': "Process Name", 'align': 'left', 'sortable': True},
    {'name': "Last Run", 'label': "Last Run", 'field': "Last Run", 'align': 'left', 'sortable': True},
    {'name': "Next_Run", 'label': "Next Run", 'field': "Next Run", 'align': 'left', 'sortable': True},
    {'name': "ID", 'label': "ID", 'field': "ID", 'align': 'left', 'sortable': True}
]


# pylint disable-next=too-few-public-methods
class TriggerTab():
    """The 'Trigger' tab object. It contains tables and buttons for dealing with triggers."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                self.single_button = ui.button("New Single Trigger", icon="add", on_click=lambda e: TriggerPopup(self, TriggerType.SINGLE))
                self.scheduled_button = ui.button("New Scheduled Trigger", icon="add", on_click=lambda e: TriggerPopup(self, TriggerType.SCHEDULED))
                self.queue_button = ui.button("New Queue Trigger", icon="add", on_click=lambda e: TriggerPopup(self, TriggerType.QUEUE))

            self.trigger_table = ui.table(columns=COLUMNS, rows=[], title="Triggers", pagination={'rowsPerPage': 50, 'sortBy': 'Trigger Name'}, row_key='ID').classes("w-full")
            self.trigger_table.on('rowClick', self._row_click)
            self.add_column_colors()

        test_helper.set_automation_ids(self, "trigger_tab")

    def _row_click(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        trigger_id = row["ID"]
        trigger = db_util.get_trigger(trigger_id)

        if isinstance(trigger, SingleTrigger):
            TriggerPopup(self, TriggerType.SINGLE, trigger)
        elif isinstance(trigger, ScheduledTrigger):
            TriggerPopup(self, TriggerType.SCHEDULED, trigger)
        elif isinstance(trigger, QueueTrigger):
            TriggerPopup(self, TriggerType.QUEUE, trigger)

    def update(self):
        """Updates the tab and it's data."""
        triggers = db_util.get_all_triggers()
        self.trigger_table.rows = [t.to_row_dict() for t in triggers]
        self.trigger_table.update()

    def add_column_colors(self):
        """Add custom coloring to the trigger table."""
        # Add coloring to the status column
        self.trigger_table.add_slot(
            "body-cell-Status",
            '''
            <q-td key="Status" :props="props">
                <q-badge v-if="{Running: 'green', Pausing: 'orange', Paused: 'orange', Failed: 'red'}[props.value]" :color="{Running: 'green', Pausing: 'orange', Paused: 'orange', Failed: 'red'}[props.value]">
                    {{props.value}}
                </q-badge>
                <p v-else>
                    {{props.value}}
                </p>
            </q-td>
            '''
        )

        # Add coloring to 'Next run' column
        # If the next run is in the past the value should be red.
        # Use a very ugly parser to create a date from a dd-MM-yyyy HH:mm:ss date string.
        self.trigger_table.add_slot(
            "body-cell-Next_Run",
            '''
            <q-td key="Next_Run" :props="props">
                {{props.value}}
                <q-badge v-if="new Date(+props.value.substr(6,4), +props.value.substr(3,2)-1, +props.value.substr(0,2), +props.value.substr(11,2), +props.value.substr(14,2)) < new Date()" color='red'>
                    Overdue
                </q-badge>
            </q-td>
            '''
        )
