"""This module is responsible for the layout and functionality of the 'New constant' popup."""

from __future__ import annotations
from typing import TYPE_CHECKING

from nicegui import ui

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.constants import Constant

if TYPE_CHECKING:
    from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab


# pylint: disable-next=too-few-public-methods
class ConstantPopup():
    """A popup for creating/updating queue triggers."""
    def __init__(self, constant_tab: ConstantTab, constant: Constant = None):
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
                ui.button(button_text, on_click=self.create_constant)
                ui.button("Cancel", on_click=self.dialog.close)

        if constant:
            self.pre_populate()

    def pre_populate(self):
        """Pre populate the inputs with an existing constant."""
        self.name_input.value = self.constant.name
        self.name_input.disable()
        self.value_input.value = self.constant.value

    def create_constant(self):
        """Creates a new constant in the database using the data from the
        UI.
        """
        name = self.name_input.value
        value = self.value_input.value

        if not name:
            ui.notify('Please enter a name', type='negative')
            return

        if not value:
            ui.notify('Please enter a value', type='negative')
            return

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
