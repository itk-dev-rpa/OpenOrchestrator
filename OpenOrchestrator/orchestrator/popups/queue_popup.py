"""Class for queue element popups."""
import json
from nicegui import ui

from OpenOrchestrator.orchestrator import styling_constants as style


class QueueElementPopup():
    """A popup to display queue element data.
    """
    def __init__(self, row_data):
        """Show a dialogue with details of the row selected.

        Args:
            row_data: Data from the row selected.
        """
        with ui.dialog() as dialog:
            with ui.card().style('min-width: 600px; max-width: 800px'):

                with ui.row().classes('w-full justify-between items-start mb-4'):
                    with ui.column().classes(style.SECTION + ' mb-4'):
                        ui.label("Reference:").classes(style.LABEL)
                        ui.label(row_data.get('Reference', 'N/A')).classes('text-h5')
                    with ui.column().classes(style.SECTION + ' items-end'):
                        ui.label('Status').classes(style.LABEL)
                        ui.label(row_data.get('Status', 'N/A')).classes('text-h5')
                ui.separator()

                with ui.column().classes('gap-1'):

                    data_text = row_data.get('Data', '{}')
                    if data_text and len(data_text) > 0:
                        with ui.row().classes('w-full'):
                            ui.label('Data').classes(style.LABEL)
                            try:
                                data = json.loads(data_text)
                                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                                ui.code(formatted_data).classes('h-200px w-full').style('max-width: 750px;')
                            except (json.JSONDecodeError, TypeError):
                                ui.code(data_text).classes('h-200px w-full').style('max-width: 750px;')

                    message_text = row_data.get('Message')
                    if message_text and len(message_text) > 0:
                        with ui.row().classes('w-full mt-4'):
                            ui.label('Message').classes(style.LABEL)
                            ui.label(message_text).classes(style.VALUE)

                    with ui.row().classes('w-full mt-4'):
                        with ui.column().classes('flex-1'):
                            ui.label("Created Date:").classes(style.LABEL)
                            ui.label(row_data.get('Created Date', 'N/A')).classes(style.VALUE)
                        with ui.column().classes('flex-1'):
                            ui.label("Start Date:").classes(style.LABEL)
                            ui.label(row_data.get('Start Date', 'N/A')).classes(style.VALUE)
                        with ui.column().classes('flex-1'):
                            ui.label("End Date:").classes(style.LABEL)
                            ui.label(row_data.get('End Date', 'N/A')).classes(style.VALUE)

                    with ui.row().classes('w-full mt-4'):
                        ui.label("Created By:").classes(style.LABEL)
                        ui.label(row_data.get('Created By', 'N/A')).classes(style.VALUE)
                    with ui.row().classes('w-full'):
                        ui.label("ID:").classes(style.LABEL)
                        ui.label(row_data.get('ID', 'N/A')).classes(style.VALUE)

                ui.button('Close', on_click=dialog.close).classes('mt-4')
        dialog.open()
