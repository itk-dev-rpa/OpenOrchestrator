"""Class for queue element popups."""
import json
from nicegui import ui
from typing import Callable
from datetime import datetime

from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups import generic_popups
from OpenOrchestrator.orchestrator.datetime_input import DatetimeInput
from OpenOrchestrator.database.queues import QueueStatus, QueueElement


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class QueueElementPopup():
    """A popup to display queue element data.
    """
    def __init__(self, queue_element: QueueElement | None, on_dialog_close_callback: Callable, queue_name: str):
        """Show a dialogue with details of the row selected.

        Args:
            row_data: Data from the row selected.
        """
        self.on_dialog_close_callback = on_dialog_close_callback
        self.queue_element = queue_element
        self.queue_name = queue_name
        with ui.dialog() as self.dialog:
            with ui.card().style('min-width:  37.5rem; max-width: 50rem'):

                with ui.row().classes('w-full justify-between items-start mb-4'):
                    with ui.column().classes('gap-0 mb-4'):
                        ui.label("ID:").classes('text-subtitle2 text-grey-7')
                        self.id_text = ui.label()
                        self.reference = ui.input("Reference")
                    with ui.column().classes('gap-0 items-end'):
                        ui.label("Created by:").classes('text-subtitle2 text-grey-7')
                        self.created_by = ui.label()
                        self.status = ui.select(options={status.name: status.value for status in QueueStatus}, label="Status").classes("w-32")

                with ui.column():
                    with ui.row().classes('w-full'):
                        self.data_field = ui.textarea("Data").classes('w-full mt-4')
                    with ui.row().classes('w-full mt-4').classes('w-full mt-4'):
                        self.message = ui.input('Message')
                    with ui.row().classes('w-full mt-4'):
                        with ui.column().classes('flex-1'):
                            self.created_date = DatetimeInput("Created Date", allow_empty=True)
                        with ui.column().classes('flex-1'):
                            self.start_date = DatetimeInput("Start Date", allow_empty=True)
                        with ui.column().classes('flex-1'):
                            self.end_date = DatetimeInput("End Date", allow_empty=True)

                with ui.row().classes('w-full mt-4'):
                    self.save_button = ui.button(text='Save', on_click=self._save_and_close).classes('mt-4')
                    self.close_button = ui.button('Close', on_click=self._close_dialog).classes('mt-4')
                    self.delete_button = ui.button(text='Delete', on_click=self._delete_element, color="negative").classes('mt-4')

        test_helper.set_automation_ids(self, "queue_element_popup")
        self.dialog.open()
        self._pre_populate()

    def _pre_populate(self):
        """Pre populate the inputs with an existing credential."""
        if self.queue_element:
            self.created_by.text = self.queue_element.created_by
            self.id_text.text = self.queue_element.id
            self.reference.value = self.queue_element.reference
            self.status.value = self.queue_element.status.name
            self.message.value = self.queue_element.message
            self.data_field.value = self._prettify_json(self.queue_element.data)
            self.created_date.set_datetime(self.queue_element.created_date)
            self.start_date.set_datetime(self.queue_element.start_date)
            self.end_date.set_datetime(self.queue_element.end_date)
        else:
            self.id_text.text = "NOT SAVED"
            self.created_by.text = "Orchestrator UI"
            self.status.value = "NEW"
            self.delete_button.visible = False

    def _convert_datetime(self, date_string):
        try:
            return datetime.strptime(date_string, "%d-%m-%Y %H:%M:%S")
        except ValueError:
            return None

    def _prettify_json(self, json_string: str) -> str:
        if not json_string:
            return None
        try:
            data = json.loads(json_string)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except ValueError:
            return json_string

    def _close_dialog(self):
        self.on_dialog_close_callback()
        self.dialog.close()

    async def _delete_element(self):
        if not self.queue_element:
            return
        if await generic_popups.question_popup(f"Delete element '{self.queue_element.id}'?", "Delete", "Cancel", color1='negative'):
            db_util.delete_queue_element(self.queue_element.id)
            ui.notify("Queue element deleted", type='positive')
            self._close_dialog()

    def _save_element(self):
        if not self.queue_element:
            self.queue_element = db_util.create_queue_element(self.queue_name)
            self.id_text.text = self.queue_element.id
            ui.notify("New queue element created", type="positive")
        db_util.update_queue_element(self.queue_element.id,
                                     reference=self.reference.value,
                                     status=self.status.value,
                                     data=self.data_field.value,
                                     message=self.message.value,
                                     created_by=self.created_by.text,
                                     created_date=self.created_date.get_datetime(),
                                     start_date=self.start_date.get_datetime(),
                                     end_date=self.end_date.get_datetime())

    def _save_and_close(self):
        self._save_element()
        self._close_dialog()
