"""This module provides an input element for entering a datetime."""

from datetime import datetime
from typing import Optional, Callable, Any

from nicegui import ui


class DatetimeInput(ui.input):
    """A datetime input with a button to show a date and time picker dialog."""
    PY_FORMAT = "%d-%m-%Y %H:%M"
    VUE_FORMAT = "DD-MM-YYYY HH:mm"

    def __init__(self, label: str, on_change: Optional[Callable[..., Any]] = None, allow_empty: bool = False) -> None:
        """Create a new DatetimeInput.

        Args:
            label: The label for the input element.
            on_change: A callable to execute on change. Defaults to None.
            allow_empty: Whether to allow an empty input on validation. Defaults to False.
        """
        super().__init__(label, on_change=lambda: self._on_change(on_change))
        self.props("clearable")
        self.complete = False

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
        self.bind_value(time_input)

        self._define_validation(allow_empty)

        self.complete = True

    def _define_validation(self, allow_empty: bool):
        if not allow_empty:
            self._validation = {  # pylint: disable=protected-access
                "Please enter a datetime": bool,
                f"Invalid datetime: {self.PY_FORMAT}": lambda v: self.get_datetime() is not None
            }

        else:
            def validate(value: str):
                if not value:
                    return True

                return self.get_datetime() is not None

            self._validation = {f"Invalid datetime: {self.PY_FORMAT}": validate}  # pylint: disable=protected-access

    def get_datetime(self) -> datetime | None:
        """Get the text from the input as a datetime object, if
        the current text in the input is valid else None.

        Returns:
            datetime: The value as a datetime object if any.
        """
        try:
            return datetime.strptime(self.value, self.PY_FORMAT)
        except (TypeError, ValueError):
            return None

    def set_datetime(self, value: datetime) -> None:
        """Set the value of the datetime input.

        Args:
            value: The new datetime value.
        """
        self.value = value.strftime(self.PY_FORMAT)

    def _on_change(self, func: Optional[Callable[..., Any]]) -> None:
        """Wrapper for the input's on_change function.
        This avoids that the on_change function is called
        before the element is fully initialized.

        Args:
            func: The on_change function of the element.
        """
        if self.complete and func:
            func()
