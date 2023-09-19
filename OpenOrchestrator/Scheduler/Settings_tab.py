"""This module is responsible for the layout and functionality of the settings tab
in Scheduler."""

from tkinter import ttk

from OpenOrchestrator.Common import ui_util

def create_tab(parent: ttk.Notebook) -> ttk.Frame:
    """Creates a new Settings tab object.

    Args:
        parent (ttk.Notebook): The ttk.Notebook that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    conn_frame = ui_util.create_connection_frame(tab)
    conn_frame.pack(fill='x')

    key_frame, _ = ui_util.create_encryption_key_frame(tab)
    key_frame.pack(fill='x')

    return tab
