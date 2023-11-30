"""This module is the entry point for the Orchestrator app. It contains a single class
that when created starts the application."""

from nicegui import ui

from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab
from OpenOrchestrator.orchestrator.tabs.settings_tab import SettingsTab

with ui.header().classes('justify-between'):
    with ui.tabs() as tabs:
        triggers_tab = ui.tab('Triggers')
        logging_tab = ui.tab('Logs')
        constants_tab = ui.tab('Constants')
        settings_tab = ui.tab('Settings')

    ui.button(icon='refresh').props('color=white text-color=primary')

with ui.tab_panels(tabs, value=settings_tab).classes('w-full'):
    TriggerTab(triggers_tab)
    with ui.tab_panel(logging_tab):
        ui.label('Logs')
    with ui.tab_panel(constants_tab):
        ui.label('Constants')
    SettingsTab(settings_tab)

ui.run(title="Orchestrator", favicon='🤖', native=False)
