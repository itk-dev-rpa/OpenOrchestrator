"""This module is responsible for the layout and functionality of the Constants tab
in Orchestrator."""

import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator import table_util
from OpenOrchestrator.orchestrator.popups import constant_popup, credential_popup

def create_tab(parent: ttk.Notebook) -> ttk.Frame:
    """Create a new Constants tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    tab.columnconfigure(0, weight=1)
    tab.rowconfigure((0,2), weight=1, uniform='a')
    tab.rowconfigure((1,3), weight=6, uniform='a')
    tab.rowconfigure((4, 5), weight=1, uniform='a')

    #Constants table
    ttk.Label(tab, text="Constants").grid(row=0, column=0)
    const_table_frame = ttk.Frame(tab)
    const_table_frame.grid(row=1, column=0, sticky='nsew')
    const_table = table_util.create_table(const_table_frame, ('Name', 'Value', 'Change Date'))

    #Credentials table
    ttk.Label(tab, text="Credentials").grid(row=2, column=0)
    cred_table_frame = ttk.Frame(tab)
    cred_table_frame.grid(row=3, column=0, sticky='nsew')
    cred_table = table_util.create_table(cred_table_frame, ('Name', 'Username', 'Password', 'Change Date'))

    # Controls 1
    controls_frame = ttk.Frame(tab)
    controls_frame.grid(row=4, column=0)
    def update_command():
        update_tables(const_table, cred_table)

    update_button = ttk.Button(controls_frame, text='Update', command=update_command)
    update_button.pack(side='left')

    delete_button = ttk.Button(controls_frame, text='Delete', command=lambda: delete_selected(const_table, cred_table))
    delete_button.pack(side='left')

    # Controls 2
    controls_frame2 = ttk.Frame(tab)
    controls_frame2.grid(row=5, column=0)

    ttk.Button(controls_frame2, text='New constant', command=lambda: show_constant_popup(update_command)).pack(side='left')
    ttk.Button(controls_frame2, text='New credential', command=lambda: show_credential_popup(update_command)).pack(side='left')

    # Bindings
    const_table.bind('<FocusIn>', lambda e: table_util.deselect_tables(cred_table))
    const_table.bind('<Double-1>', lambda e: double_click_constant_table(e, const_table, update_command))

    cred_table.bind('<FocusIn>', lambda e: table_util.deselect_tables(const_table))
    cred_table.bind('<Double-1>', lambda e: double_click_credential_table(e, cred_table, update_command))

    tab.bind_all('<Delete>', lambda e: delete_selected(const_table, cred_table))

    return tab


def update_tables(const_table: ttk.Treeview, cred_table: ttk.Treeview) -> None:
    """Update the constant and credential tables with
    new values from the database.

    Args:
        const_table: The constants table object.
        cred_table: The credentials table object.
    """

    # Convert ORM objects to lists of values
    const_list = [[c.constant_name, c.constant_value, c.change_date] for c in db_util.get_constants()]
    cred_list = [[c.credential_name, c.credential_username, c.credential_password, c.change_date] for c in db_util.get_credentials()]

    table_util.update_table(const_table, const_list)
    table_util.update_table(cred_table, cred_list)


def delete_selected(const_table: ttk.Treeview, cred_table: ttk.Treeview) -> None:
    """Deletes the currently selected constant or credential
    from the database. Updates the tables afterwards.

    Args:
        const_table: The constants table object.
        cred_table: The credentials table object.
    """
    if const_table.selection():
        name = const_table.item(const_table.selection()[0], 'values')[0]
        if not messagebox.askyesno('Delete constant?', f"Are you sure you want to delete constant '{name}'?"):
            return
        db_util.delete_constant(name)

    elif cred_table.selection():
        name = cred_table.item(cred_table.selection()[0], 'values')[0]
        if not messagebox.askyesno('Delete credential?', f"Are you sure you want to delete credential '{name}'?"):
            return
        db_util.delete_credential(name)

    else:
        return

    update_tables(const_table, cred_table)


def show_constant_popup(on_close: callable, name: str=None, value: str=None) -> None:
    """Shows the new constant popup.
    Optionally populates the entry widgets in the popup with 'name' and 'value'.
    Binds a callable to the popup's on_close event.

    Args:
        on_close: A function to be called when the popup closes.
        name (optional): A value to pre-populate the name entry widget with. Defaults to None.
        value (optional): A value to pre-populate the value entry widget with. Defaults to None.
    """
    popup = constant_popup.show_popup(name, value)
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)


def double_click_constant_table(event: tkinter.Event, const_table:ttk.Treeview, on_close:callable) -> None:
    """This function is called whenever the constants table is double clicked.
    It opens the new constant popup with pre-populated values.

    Args:
        event: The event of the double click.
        const_table: The constants table.
        on_close: A function to be called when the popup is closed.
    """
    row = const_table.identify_row(event.y)
    if row:
        name, value, _ = const_table.item(row, 'values')
        show_constant_popup(on_close, name, value)


def double_click_credential_table(event: tkinter.Event, cred_table: ttk.Treeview, on_close: callable) -> None:
    """This function is called whenever the credentials table is double clicked.
    It opens the new credential popup with pre-populated values.

    Args:
        event: The event of the double click.
        cred_table: The credentials table.
        on_close: A function to be called when the popup is closed.
    """
    row = cred_table.identify_row(event.y)
    if row:
        name, value, _, _ = cred_table.item(row, 'values')
        show_credential_popup(on_close, name, value)


def show_credential_popup(on_close: callable, name: str=None, username: str=None) -> None:
    """Shows the new credential popup.
    Optionally populates the entry widgets in the popup with 'name' and 'username'.
    Binds a callable to the popup's on_close event.

    Args:
        on_close: A function to be called when the popup closes.
        name (optional): A value to pre-populate the name entry widget with. Defaults to None.
        username (optional): A value to pre-populate the username entry widget with. Defaults to None.
    """
    popup = credential_popup.show_popup(name, username)
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)
