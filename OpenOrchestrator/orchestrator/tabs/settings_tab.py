"""This module is responsible for the layout and functionality of the Settings tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.common.connection_frame import ConnectionFrame


# pylint: disable-next=too-few-public-methods
class SettingsTab():
    """The settings tab object for Orchestrator."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            conn_frame = ConnectionFrame()
            with ui.row().classes("w-full"):
                self.key_button = ui.button("Generate Key", on_click=conn_frame.new_key)
                self.init_button = ui.button("Initialize Database", on_click=self._init_database)

    def _init_database(self):
        db_util.initialize_database()
        ui.notify("Database initialized!", type='positive')
