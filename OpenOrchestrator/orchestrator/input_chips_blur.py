"""This module provides an input_chips component with blur event handling.

The InputChipsBlur component extends ui.input_chips to automatically add chips
when the user tabs out or clicks away from the input field (not just on Enter).

Usage:
    from OpenOrchestrator.orchestrator.input_chips_blur import InputChipsBlur

    chips = InputChipsBlur(label="Tags", new_value_mode='add-unique')

The component uses Quasar's 'popup-hide' event which fires when the dropdown closes
(on Tab, click away, Escape, etc.) to trigger adding the chip.
"""

from typing import List, Literal, Optional
from nicegui import ui
from nicegui.events import GenericEventArguments, Handler, ValueChangeEventArguments


class InputChipsBlur(ui.input_chips):
    """An input_chips component that automatically adds chips on blur (when losing focus).

    This extends the standard NiceGUI input_chips to add a chip when the user
    tabs out or clicks away from the input field, not just when pressing Enter.
    """

    def __init__(self,
                 label: Optional[str] = None,
                 *,
                 value: Optional[List[str]] = None,
                 on_change: Optional[Handler[ValueChangeEventArguments]] = None,
                 new_value_mode: Literal['add', 'add-unique', 'toggle'] = 'toggle',
                 clearable: bool = False,
                 validation: Optional[dict] = None,
                 ) -> None:
        """Create a new InputChipsBlur component.

        Args:
            label: the label to display above the selection
            value: the initial value
            on_change: callback to execute when selection changes
            new_value_mode: handle new values from user input (default: "toggle")
            clearable: whether to add a button to clear the selection
            validation: dictionary of validation rules or a callable that returns an optional error message
        """
        super().__init__(
            label=label,
            value=value,
            on_change=on_change,
            new_value_mode=new_value_mode,
            clearable=clearable,
            validation=validation
        )

        # Track current input value
        self._current_input_value = ''
        self._new_value_mode = new_value_mode

        # Listen to input-value event to track what user types
        self.on('input-value', self._handle_input_value_change)
        self.on('blur', self._handle_blur)

    def _handle_input_value_change(self, e: GenericEventArguments) -> None:
        """Track what user types in real-time.

        Args:
            e: Event containing the current input value
        """
        self._current_input_value = e.args if e.args else ''

    def _handle_blur(self) -> None:  # pylint: disable=unused-argument
        """Add chip when input loses focus.

        Args:
            e: The blur event (unused)
        """
        # Get trimmed value
        val = self._current_input_value.strip() if isinstance(self._current_input_value, str) else ''

        # Don't add empty values
        if not val:
            return

        # Get current value and new-value-mode
        current_value = self.value if self.value else []
        new_value_mode = self._new_value_mode

        # Apply new-value-mode logic
        if new_value_mode == 'add':
            # Always add the value
            new_value = current_value + [val]
        elif new_value_mode == 'add-unique':
            # Only add if not already present
            if val not in current_value:
                new_value = current_value + [val]
            else:
                return
        elif new_value_mode == 'toggle':
            # Add if not present, remove if present
            if val in current_value:
                new_value = [v for v in current_value if v != val]
            else:
                new_value = current_value + [val]
        else:
            return

        # Update value
        self.value = new_value

        # Clear the input field by resetting tracked value
        self._current_input_value = ''
