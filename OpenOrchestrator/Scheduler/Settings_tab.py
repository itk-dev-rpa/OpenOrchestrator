"""This module is responsible for the layout and functionality of the settings tab
in Scheduler."""

from tkinter import ttk
import os

from OpenOrchestrator.Common import db_util, crypto_util

def create_tab(parent: ttk.Notebook) -> ttk.Frame:
    """Creates a new Settings tab object.

    Args:
        parent (ttk.Notebook): The ttk.Notebook that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    conn_label = ttk.Label(tab, text="Connection string:")
    conn_label.pack()

    conn_entry = ttk.Entry(tab)
    conn_entry.pack(fill='x')

    conn_button = ttk.Button(tab, text="Connect", command=lambda: connect(conn_entry, conn_button))
    conn_button.pack()

    ttk.Label(tab, text="Encryption Key:").pack()
    key_entry = ttk.Entry(tab, width=50, validate='key')
    reg = key_entry.register(validate_key(key_entry))
    key_entry.configure(validatecommand=(reg, '%P'))
    key_entry.pack()

    # TEMPORARY
    conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;")
    connect(conn_entry, conn_button)
    key_entry.insert(0, os.environ['OpenOrhcestratorKey'])

    return tab


def connect(conn_entry: ttk.Entry, conn_button: ttk.Button) -> None:
    """Connect using the connection string given in the UI.
    Change the label of the connect button if successful.

    Args:
        conn_entry: The connection string entry.
        conn_button: The connect button.
    """
    conn_string = conn_entry.get()

    if db_util.connect(conn_string):
        conn_button.configure(text="Connected!")
    else:
        conn_button.configure(text="Connect")


def validate_key(entry:ttk.Entry) -> callable:
    """Creates a validator function to validate if
    an AES key entered in the given entry is valid.
    Changes the color of the Entry widget according
    to the validity of the key.

    Args:
        entry: The entry widget to validate on.

    Returns:
        callable: The validator function.
    """
    def inner(text:str):
        if crypto_util.validate_key(text):
            entry.configure(foreground='black')
            crypto_util.set_key(text)
        else:
            entry.configure(foreground='red')
        return True
    return inner
