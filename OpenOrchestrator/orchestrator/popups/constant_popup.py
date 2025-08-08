"""This module is responsible for the layout and functionality of the 'New constant' popup."""

from __future__ import annotations
from typing import TYPE_CHECKING

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.constants import Constant
from OpenOrchestrator.orchestrator.popups.generic_popups import question_popup
from OpenOrchestrator.orchestrator import test_helper

if TYPE_CHECKING:
    from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class ConstantPopup():
    """A popup for creating/updating queue triggers."""
    def __init__(self, constant_tab: ConstantTab, constant: Constant | None = None):
        """Create a new popup.
        If a constant is given it will be updated instead of creating a new constant.

        Args:
            constant: The constant to update if any.
        """
        self.constant_tab = constant_tab
        self.constant = constant
        title = 'Update Constant' if constant else 'New Constant'
        button_text = "Update" if constant else "Create"

        with ui.dialog(value=True).props('persistent') as self.dialog, ui.card().classes('w-full'):
            ui.label(title).classes("text-xl")
            self.name_input = ui.input("Constant Name").classes("w-full")
            self.value_input = ui.input("Constant Value").classes("w-full")

            with ui.row():
                self.save_button = ui.button(button_text, on_click=self._create_constant)
                self.cancel_button = ui.button("Cancel", on_click=self.dialog.close)

                if constant:
                    self.delete_button = ui.button("Delete", color='red', on_click=self._delete_constant)

        self._define_validation()
        self._pre_populate()
        test_helper.set_automation_ids(self, "constant_popup")

    def _define_validation(self):
        """Define validation rules for input elements."""
        self.name_input._validation = {"Please enter a name": bool}  # pylint: disable=protected-access
        self.value_input._validation = {"Please enter a value": bool}  # pylint: disable=protected-access

    def _pre_populate(self):
        """Pre populate the inputs with an existing constant."""
        if self.constant:
            self.name_input.value = self.constant.name
            self.name_input.disable()
            self.value_input.value = self.constant.value

    def _create_constant(self):
        """Creates a new constant in the database using the data from the
        UI.
        """
        self.name_input.validate()
        self.value_input.validate()

        if self.name_input.error or self.value_input.error:
            return

        name = self.name_input.value
        value = self.value_input.value

        if self.constant:
            db_util.update_constant(name, value)
        else:
            # Check if constant already exists
            try:
                db_util.get_constant(name)
                exists = True
            except ValueError:
                exists = False

            if exists:
                ui.notify("A constant with that name already exists.", type='negative')
                return

            db_util.create_constant(name, value)

        self.dialog.close()
        self.constant_tab.update()

    async def _delete_constant(self):
        if not self.constant:
            return
        if await question_popup(f"Delete constant '{self.constant.name}?", "Delete", "Cancel", color1='red'):
            db_util.delete_constant(self.constant.name)
            self.dialog.close()
            self.constant_tab.update()
