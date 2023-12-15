"""This module provides an input element for entering a datetime."""

from datetime import datetime

from nicegui import ui


class DatetimeInput(ui.input):
    """A datetime input with a button to show a date and time picker dialog."""
    PY_FORMAT = "%d-%m-%Y %H:%M"
    VUE_FORMAT = "DD-MM-YYYY HH:mm"

    def __init__(self, label: str) -> None:
        super().__init__(label)

        # Define dialog
        with ui.dialog() as self._dialog, ui.card():
            date_input = ui.date(mask=self.VUE_FORMAT).props("today-btn first-day-of-week=1")
            time_input = ui.time(mask=self.VUE_FORMAT).props("format24h")

        # Define input
        with self:
            ui.button(icon="event", on_click=self._dialog.open).props("flat")
            self.on("click", self._dialog.open)

        # Bind inputs together
        self.bind_value(date_input)
        date_input.bind_value(time_input)

    def get_datetime(self) -> datetime | None:
        """Get the text from the input as a datetime object, if
        the current text in the input is valid else None.

        Returns:
            datetime: The value as a datetime object if any.
        """
        try:
            return datetime.strptime(self.value,  self.PY_FORMAT)
        except (TypeError, ValueError):
            return None

    def set_datetime(self, value: datetime) -> None:
        """Set the value of the datetime input.

        Args:
            value: The new datetime value.
        """
        self.value = value.strftime(self.PY_FORMAT)
