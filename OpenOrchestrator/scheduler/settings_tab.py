"""This module is responsible for the layout and functionality of the settings tab
in Scheduler."""

from tkinter import ttk

from OpenOrchestrator.scheduler.connection_frame import ConnectionFrame


def create_tab(parent: ttk.Notebook) -> ttk.Frame:
    """Creates a new Settings tab object.

    Args:
        parent (ttk.Notebook): The ttk.Notebook that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    conn_frame = ConnectionFrame(tab)
    conn_frame.pack(fill='x')

    return tab
