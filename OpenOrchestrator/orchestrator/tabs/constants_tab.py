"""This module is responsible for the layout and functionality of the Constants tab
in Orchestrator."""

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups.constant_popup import ConstantPopup
from OpenOrchestrator.orchestrator.popups.credential_popup import CredentialPopup
from OpenOrchestrator.orchestrator import test_helper

CONSTANT_COLUMNS = ("Constant Name", "Value", "Last Changed")
CREDENTIAL_COLUMNS = ("Credential Name", "Username", "Password", "Last Changed")


class ConstantTab():
    """The 'Constants' tab object."""
    def __init__(self, tab_name: str) -> None:
        with ui.tab_panel(tab_name):
            with ui.row():
                self.constant_button = ui.button("New Constant", icon='add', on_click=lambda e: ConstantPopup(self))
                self.credential_button = ui.button("New Credential", icon='add', on_click=lambda e: CredentialPopup(self))

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in CONSTANT_COLUMNS]
            self.constants_table = ui.table(title="Constants", columns=columns, rows=[], row_key='Constant Name', pagination=10).classes("w-full")
            self.constants_table.on('rowClick', self.row_click_constant)

            columns = [{'name': label, 'label': label, 'field': label, 'align': 'left', 'sortable': True} for label in CREDENTIAL_COLUMNS]
            self.credentials_table = ui.table(title="Credentials", columns=columns, rows=[], row_key='Credential Name', pagination=10).classes("w-full")
            self.credentials_table.on('rowClick', self.row_click_credential)

        test_helper.set_automation_ids(self, "constants_tab")

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
        credential = db_util.get_credential(name, False)
        CredentialPopup(self, credential)

    def update(self):
        """Updates the tables on the tab."""
        constants = db_util.get_constants()
        self.constants_table.rows = [c.to_row_dict() for c in constants]
        self.constants_table.update()

        credentials = db_util.get_credentials()
        self.credentials_table.rows = [c.to_row_dict() for c in credentials]
        self.credentials_table.update()
