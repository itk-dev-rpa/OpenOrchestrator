"""Class for queue element popups."""
import json
from nicegui import ui

from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator.popups import generic_popups

# Styling constants
LABEL = 'text-subtitle2 text-grey-7'
VALUE = 'text-body1 gap-0'
SECTION = 'gap-0'


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class QueueElementPopup():
    """A popup to display queue element data.
    """
    def __init__(self, row_data: ui.row, on_dialog_close_callback):
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
                        ui.label("Reference:").classes(LABEL)
                        self.reference_text = ui.label(row_data.get('Reference', 'N/A')).classes('text-h5')
                    with ui.column().classes(SECTION + ' items-end'):
                        ui.label('Status').classes(LABEL)
                        self.status_text = ui.label(row_data.get('Status', 'N/A')).classes('text-h5')
                ui.separator()

                with ui.column().classes('gap-1'):

                    data_text = row_data.get('Data', None)
                    if data_text and len(data_text) > 0:
                        with ui.row().classes('w-full'):
                            ui.label('Data').classes(LABEL)
                            try:
                                data = json.loads(data_text)
                                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                                self.data_text = ui.code(formatted_data).classes('h-12.5rem w-full').style('max-width: 37.5rem;')
                            except (json.JSONDecodeError, TypeError):
                                self.data_text = ui.code(data_text).classes('h-12.5rem w-full').style('max-width: 37.5rem;')

                    message_text = row_data.get('Message')
                    if message_text and len(message_text) > 0:
                        with ui.row().classes('w-full mt-4'):
                            ui.label('Message').classes(LABEL)
                            self.message_text = ui.label(message_text).classes(VALUE)

                    with ui.row().classes('w-full mt-4'):
                        with ui.column().classes('flex-1'):
                            ui.label("Created Date:").classes(LABEL)
                            self.created_date = ui.label(row_data.get('Created Date', 'N/A')).classes(VALUE)
                        with ui.column().classes('flex-1'):
                            ui.label("Start Date:").classes(LABEL)
                            self.start_date = ui.label(row_data.get('Start Date', 'N/A')).classes(VALUE)
                        with ui.column().classes('flex-1'):
                            ui.label("End Date:").classes(LABEL)
                            self.end_date = ui.label(row_data.get('End Date', 'N/A')).classes(VALUE)

                    with ui.row().classes('w-full mt-4'):
                        ui.label("Created By:").classes(LABEL)
                        self.created_by = ui.label(row_data.get('Created By', 'N/A')).classes(VALUE)
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

    def _close_dialog(self):
        self.on_dialog_close_callback()
        self.dialog.close()

    async def _delete_element(self):
        if not self.row_data:
            return

        if await generic_popups.question_popup(f"Delete element '{self.row_data.get('ID')}'?", "Delete", "Cancel", color1='red'):
            db_util.delete_queue_element(self.row_data.get('ID'))
            ui.notify("Queue element deleted", type='positive')
            self.dialog.close()
            self.on_dialog_close_callback()
