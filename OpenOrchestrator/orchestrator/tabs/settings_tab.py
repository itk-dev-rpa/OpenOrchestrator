"""This module is responsible for the layout and functionality of the Settings tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.common.connection_frame import ConnectionFrame


class SettingsTab():
    def __init__(self, tab: ui.tab) -> None:
        with ui.tab_panel(tab):
            conn_frame = ConnectionFrame()
            with ui.row().classes("w-full"):
                self.key_button = ui.button("Generate Key", on_click=conn_frame.new_key)
                self.init_button = ui.button("Initialize Database")

# def create_tab(paren):
#     """Create a new Setting tab object.

#     Args:
#         parent: The ttk.Notebook object that this tab is a child of.

#     Returns:
#         ttk.Frame: The created tab object as a ttk.Frame.
#     """
#     tab = ttk.Frame(parent)
#     tab.pack(fill='both', expand=True)

#     conn_frame = ConnectionFrame(tab)
#     conn_frame.pack(fill='x')

#     key_button = ttk.Button(tab, text="New key", command=conn_frame.new_key)
#     key_button.pack()

#     init_button = ttk.Button(tab, text='Initialize Database', command=db_util.initialize_database)
#     init_button.pack()

#     return tab
