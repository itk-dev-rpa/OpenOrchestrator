"""This module contains helper functions for automated tests."""

from nicegui import ui


def set_automation_ids(container, prefix: str):
    """Set automation ids for automated tests.
    Iterate though all attributes of the container and set 'auto-id'
    on any ui-elements.

    Args:
        container: The object that contains a number of ui-elements.
        prefix: The prefix to add to the automation ids for all elements.
    """
    for name, obj in container.__dict__.items():
        if isinstance(obj, (ui.button, ui.input, ui.checkbox, ui.number, ui.table, ui.tab, ui.select, ui.input_chips)):
            obj.props(f"auto-id={prefix}_{name}")
