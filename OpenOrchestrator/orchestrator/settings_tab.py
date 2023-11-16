"""This module is responsible for the layout and functionality of the Settings tab
in Orchestrator."""

from tkinter import ttk

from OpenOrchestrator.database import db_util
from OpenOrchestrator.common.connection_frame import ConnectionFrame


def create_tab(parent):
    """Create a new Setting tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    conn_frame = ConnectionFrame(tab)
    conn_frame.pack(fill='x')

    key_button = ttk.Button(tab, text="New key", command=conn_frame.new_key)
    key_button.pack()

    init_button = ttk.Button(tab, text='Initialize Database', command=db_util.initialize_database)
    init_button.pack()

    return tab
