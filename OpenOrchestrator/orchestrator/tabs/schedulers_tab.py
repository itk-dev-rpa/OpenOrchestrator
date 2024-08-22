from nicegui import ui

from OpenOrchestrator.database import db_util

CONSTANT_COLUMNS = ("Computer name", "Last Connection")


class SchedulerTab():

    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in CONSTANT_COLUMNS]
            self.schedulers_table = ui.table(title="Schedulers", columns=columns, rows=[], row_key='Computer Name', pagination=10).classes("w-full")

    def update(self):
        """Updates the tables on the tab."""
        schedulers = db_util.get_schedulers()
        self.schedulers_table
        for scheduler in schedulers:
