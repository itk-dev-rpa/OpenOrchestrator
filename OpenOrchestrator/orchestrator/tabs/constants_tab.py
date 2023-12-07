"""This module is responsible for the layout and functionality of the Constants tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups.constant_popup import ConstantPopup
from OpenOrchestrator.orchestrator.popups.credential_popup import CredentialPopup

CONSTANT_COLUMNS = ("Constant Name", "Value", "Last Changed")
CREDENTIAL_COLUMNS = ("Credential Name", "Username", "Password", "Last Changed")

class ConstantTab():
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                ui.button("New Constant", icon='add', on_click=lambda e: ConstantPopup(self))
                ui.button("New Credential", icon='add', on_click=lambda e: CredentialPopup(self))

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in CONSTANT_COLUMNS]
            self.constants_table = ui.table(title="Constants", columns=columns, rows=[], row_key='Constant Name').classes("w-full")
            self.constants_table.on('rowClick', self.row_click_constant)

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in CREDENTIAL_COLUMNS]
            self.credentials_table = ui.table(title="Credentials", columns=columns, rows=[], row_key='Credential Name').classes("w-full")
            self.credentials_table.on('rowClick', self.row_click_credential)

    def row_click_constant(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        name = row['Constant Name']
        constant = db_util.get_constant(name)
        ConstantPopup(self, constant)

    def row_click_credential(self, event):
        """Callback for when a row is clicked in the table."""
        row = event.args[1]
        name = row['Credential Name']
        credential = db_util.get_credential(name)
        CredentialPopup(self, credential)

    def update(self):
        """Updates the tables on the tab."""
        constants = db_util.get_constants()
        self.constants_table.rows = [c.to_row_dict() for c in constants]
        self.constants_table.update()

        credentials = db_util.get_credentials()
        self.credentials_table.rows = [c.to_row_dict() for c in credentials]
        self.credentials_table.update()



# def update_tables(const_table: ttk.Treeview, cred_table: ttk.Treeview) -> None:
#     """Update the constant and credential tables with
#     new values from the database.

#     Args:
#         const_table: The constants table object.
#         cred_table: The credentials table object.
#     """

#     # Convert ORM objects to lists of values
#     const_list = [c.to_tuple() for c in db_util.get_constants()]
#     cred_list = [c.to_tuple() for c in db_util.get_credentials()]

#     table_util.update_table(const_table, const_list)
#     table_util.update_table(cred_table, cred_list)


# def delete_selected(const_table: ttk.Treeview, cred_table: ttk.Treeview) -> None:
#     """Deletes the currently selected constant or credential
#     from the database. Updates the tables afterwards.

#     Args:
#         const_table: The constants table object.
#         cred_table: The credentials table object.
#     """
#     if const_table.selection():
#         name = const_table.item(const_table.selection()[0], 'values')[0]
#         if not messagebox.askyesno('Delete constant?', f"Are you sure you want to delete constant '{name}'?"):
#             return
#         db_util.delete_constant(name)

#     elif cred_table.selection():
#         name = cred_table.item(cred_table.selection()[0], 'values')[0]
#         if not messagebox.askyesno('Delete credential?', f"Are you sure you want to delete credential '{name}'?"):
#             return
#         db_util.delete_credential(name)

#     else:
#         return

#     update_tables(const_table, cred_table)


# def show_constant_popup(on_close: callable, name: str=None, value: str=None) -> None:
#     """Shows the new constant popup.
#     Optionally populates the entry widgets in the popup with 'name' and 'value'.
#     Binds a callable to the popup's on_close event.

#     Args:
#         on_close: A function to be called when the popup closes.
#         name (optional): A value to pre-populate the name entry widget with. Defaults to None.
#         value (optional): A value to pre-populate the value entry widget with. Defaults to None.
#     """
#     popup = constant_popup.show_popup(name, value)
#     popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)


# def double_click_constant_table(event: tkinter.Event, const_table:ttk.Treeview, on_close:callable) -> None:
#     """This function is called whenever the constants table is double clicked.
#     It opens the new constant popup with pre-populated values.

#     Args:
#         event: The event of the double click.
#         const_table: The constants table.
#         on_close: A function to be called when the popup is closed.
#     """
#     row = const_table.identify_row(event.y)
#     if row:
#         name, value, *_ = const_table.item(row, 'values')
#         show_constant_popup(on_close, name, value)


# def double_click_credential_table(event: tkinter.Event, cred_table: ttk.Treeview, on_close: callable) -> None:
#     """This function is called whenever the credentials table is double clicked.
#     It opens the new credential popup with pre-populated values.

#     Args:
#         event: The event of the double click.
#         cred_table: The credentials table.
#         on_close: A function to be called when the popup is closed.
#     """
#     row = cred_table.identify_row(event.y)
#     if row:
#         name, value, *_ = cred_table.item(row, 'values')
#         show_credential_popup(on_close, name, value)


# def show_credential_popup(on_close: callable, name: str=None, username: str=None) -> None:
#     """Shows the new credential popup.
#     Optionally populates the entry widgets in the popup with 'name' and 'username'.
#     Binds a callable to the popup's on_close event.

#     Args:
#         on_close: A function to be called when the popup closes.
#         name (optional): A value to pre-populate the name entry widget with. Defaults to None.
#         username (optional): A value to pre-populate the username entry widget with. Defaults to None.
#     """
#     popup = credential_popup.show_popup(name, username)
#     popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)
