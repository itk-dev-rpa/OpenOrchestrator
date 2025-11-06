"""This module is responsible for the layout and functionality of the 'New constant' popup."""

from __future__ import annotations
from typing import TYPE_CHECKING

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.constants import Credential
from OpenOrchestrator.orchestrator.popups.generic_popups import question_popup
from OpenOrchestrator.orchestrator import test_helper

if TYPE_CHECKING:
    from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class CredentialPopup():
    """A popup for creating/updating queue triggers."""
    def __init__(self, constant_tab: ConstantTab, credential: Credential | None = None):
        """Create a new popup.
        If a credential is given it will be updated instead of creating a new credential.

        Args:
            constant_tab: The tab that is opening this popup.
            credential: The credential to update if any.
        """
        self.constant_tab = constant_tab
        self.credential = credential
        title = 'Update Credential' if credential else 'New Credential'
        button_text = "Update" if credential else "Create"

        with ui.dialog(value=True).props('persistent') as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.name_input = ui.input("Credential Name").classes("w-full")
            self.username_input = ui.input("Username").classes("w-full")
            self.password_input = ui.input("Password").classes("w-full")

            with ui.row():
                self.save_button = ui.button(button_text, on_click=self._save_credential)
                self.cancel_button = ui.button("Cancel", on_click=self.dialog.close)

                if credential:
                    self.delete_button = ui.button("Delete", color='red', on_click=self._delete_credential)

        self._define_validation()
        self._pre_populate()
        test_helper.set_automation_ids(self, "credential_popup")

    def _define_validation(self):
        """Define validation functions for ui elements."""
        self.name_input._validation = {"Please enter a name": bool}  # pylint: disable=protected-access
        self.username_input._validation = {"Please enter a username": bool}  # pylint: disable=protected-access
        self.password_input._validation = {"Please enter a password": bool}  # pylint: disable=protected-access

    def _pre_populate(self):
        """Pre populate the inputs with an existing credential."""
        if self.credential:
            self.name_input.value = self.credential.name
            self.name_input.disable()
            self.username_input.value = self.credential.username

    def _save_credential(self):
        """Create or update a credential in the database using the data from the UI."""
        self.name_input.validate()
        self.username_input.validate()
        self.password_input.validate()

        if self.name_input.error or self.username_input.error or self.password_input.error:
            return

        name = self.name_input.value
        username = self.username_input.value
        password = self.password_input.value

        if self.credential:
            db_util.update_credential(name, username, password)
        else:
            # Check if credential already exists
            try:
                db_util.get_credential(name, decrypt_password=False)
                exists = True
            except ValueError:
                exists = False

            if exists:
                ui.notify("A credential with that name already exists.", type='negative')
                return

            db_util.create_credential(name, username, password)

        self.dialog.close()
        self.constant_tab.update()

    async def _delete_credential(self):
        """Delete the selected credential."""
        if not self.credential:
            return
        if await question_popup(f"Delete credential '{self.credential.name}'?", "Delete", "Cancel", color1='red'):
            db_util.delete_credential(self.credential.name)
            self.dialog.close()
            self.constant_tab.update()
