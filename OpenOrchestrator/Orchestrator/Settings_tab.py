"""This module is responsible for the layout and functionality of the Settings tab
in Orchestrator."""

from tkinter import ttk

from OpenOrchestrator.Common import db_util, crypto_util, ui_util


def create_tab(parent):
    """Create a new Setting tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    conn_frame = ui_util.create_connection_frame(tab)
    conn_frame.pack(fill='x')

    key_frame, key_entry = ui_util.create_encryption_key_frame(tab)
    key_frame.pack(fill='x')

    key_button = ttk.Button(tab, text="New key", command=lambda: new_key(key_entry))
    key_button.pack()

    init_button = ttk.Button(tab, text='Initialize Database', command=db_util.initialize_database)
    init_button.pack()

    return tab


def new_key(key_entry:ttk.Entry) -> None:
    """Creates a new valid AES crypto key
    and inserts in into the entry widget.

    Args:
        key_entry: The entry widget to insert the new key into.
    """
    key = crypto_util.generate_key()
    key_entry.delete(0, 'end')
    key_entry.insert(0, key)
