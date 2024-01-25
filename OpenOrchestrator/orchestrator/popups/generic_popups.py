"""This module contains functions to generate generic popups for various use cases."""

from nicegui import ui


async def question_popup(question: str, option1: str, option2: str, color1: str = 'primary', color2: str = 'primary') -> bool:
    """Shows a popup with a question and two buttons with the given options.
    Example:
        result = await question_popup("Do you like candy", "YES!", "Not really")

    Args:
        question: The question to display.
        option1: The text on button 1.
        option2: The text on button 2.
        color1: The color of button 1.
        color2: The color of button 2.

    Returns:
        bool: True if button 1 is clicked, or False if button 2 is clicked.
    """
    with ui.dialog(value=True).props('persistent') as dialog, ui.card():
        ui.label(question).classes("text-lg")
        with ui.row():
            ui.button(option1, on_click=lambda e: dialog.submit(True), color=color1)
            ui.button(option2, on_click=lambda e: dialog.submit(False), color=color2)

        return await dialog
