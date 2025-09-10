"""Class for queue element popups."""
import json
from nicegui import ui
from typing import Callable
from datetime import datetime

from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups import generic_popups
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.database.queues import QueueStatus

# Styling constants
LABEL = 'text-subtitle2 text-grey-7'
VALUE = 'text-body1 gap-0'
SECTION = 'gap-0'


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class QueueElementPopup():
    """A popup to display queue element data.
    """
    def __init__(self, row_data: ui.row | None, on_dialog_close_callback: Callable):
        """Show a dialogue with details of the row selected.

        Args:
            row_data: Data from the row selected.
        """
        self.on_dialog_close_callback = on_dialog_close_callback
        self.row_data = row_data
        with ui.dialog() as self.dialog:
            with ui.card().style('min-width:  37.5rem; max-width: 50rem'):

                with ui.row().classes('w-full justify-between items-start mb-4'):
                    with ui.column().classes(SECTION + ' mb-4'):
                        self.reference = ui.input("Reference")
                    with ui.column().classes(SECTION + ' items-end'):
                        self.status = ui.select(options={status.name: status.value for status in QueueStatus}, label="Status")

                with ui.column().classes('gap-1'):

                    data_text = row_data.get('Data', None)
                    if data_text and len(data_text) > 0:
                        with ui.row().classes('w-full'):
                            ui.label('Data').classes(LABEL)
                            try:
                                self.data_field = ui.json_editor({'content': {'json': ""}})
                            except (json.JSONDecodeError, TypeError):
                                self.data_field = ui.json_editor({'content': {'text': ""}})

                    with ui.row().classes('w-full mt-4'):
                        self.message = ui.input('Message')

                    with ui.row().classes('w-full mt-4'):
                        with ui.column().classes('flex-1'):
                            self.created_date = DatetimeInput("Created Date", allow_empty=True)
                        with ui.column().classes('flex-1'):
                            self.start_date = DatetimeInput("Start Date", allow_empty=True)
                        with ui.column().classes('flex-1'):
                            self.end_date = DatetimeInput("End Date", allow_empty=True)

                    with ui.row().classes('w-full mt-4'):
                        self.created_by = ui.input("Created By")
                    with ui.row().classes('w-full'):
                        ui.label("ID:").classes(LABEL)
                        self.id_text = ui.label(row_data.get('ID', 'N/A')).classes(VALUE)

                with ui.row().classes('w-full mt-4'):
                    ui.button(
                            icon='delete',
                            on_click=self._delete_element,
                            color="red"
                        ).classes('mt-4')
                    ui.button('Close', on_click=self._close_dialog).classes('mt-4')
        test_helper.set_automation_ids(self, "queue_element_popup")
        self.dialog.open()
        self._pre_populate()

    def _pre_populate(self):
        """Pre populate the inputs with an existing credential."""
        if self.row_data:
            self.reference.value = self.row_data.get('Reference', 'N/A')
            self.status.value = self.row_data.get('Status', 'New').upper().replace(" ", "_")  # Hackiddy hack
            self.message.value = self.row_data.get('Message', 'N/A')
            self._set_data(self.row_data.get('Data', ""))
            self.created_date.value = self._convert_datetime(self.row_data.get('Created Date', None))
            self.start_date.value = self._convert_datetime(self.row_data.get('Start Date', None))
            self.end_date.value = self._convert_datetime(self.row_data.get('End Date', None))
            self.created_by.value = self.row_data.get('Created By', 'N/A')

    async def _get_data(self) -> None:
        data = await self.data_field.run_editor_method('get')
        ui.notify(data)

    async def _set_data(self, data) -> None:
        try:
            data = json.loads(data)
        except ValueError:
            pass
        await self.data_field.run_editor_method('update', data)
        ui.notify(f"Set data: {data}")

    def _convert_datetime(self, date_string):
        try:
            return datetime.strptime(date_string, "%d-%m-%Y %H:%M:%S").strftime("%d-%m-%Y %H:%M")
        except ValueError:
            return None

    def _close_dialog(self):
        self.on_dialog_close_callback()
        self.dialog.close()

    async def _delete_element(self):
        if not self.row_data:
            return
        if await generic_popups.question_popup(f"Delete element '{self.row_data.get('ID')}'?", "Delete", "Cancel", color1='red'):
            db_util.delete_queue_element(self.row_data.get('ID'))
            ui.notify("Queue element deleted", type='positive')
            self.on_dialog_close_callback()
            self.dialog.close()
