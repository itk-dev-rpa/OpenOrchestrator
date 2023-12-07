"""This module is the entry point for the Orchestrator app. It contains a single class
that when created starts the application."""

from nicegui import ui

from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab
from OpenOrchestrator.orchestrator.tabs.settings_tab import SettingsTab
from OpenOrchestrator.orchestrator.tabs.logging_tab import LoggingTab
from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab

with ui.header().classes('justify-between'):
    with ui.tabs() as tabs:
        ui.tab('Triggers')
        ui.tab('Logs')
        ui.tab('Constants')
        ui.tab('Settings')

    ui.button(icon='refresh', on_click=lambda e: update_tab(tab_panels.value)).props('color=white text-color=primary')

with ui.tab_panels(tabs, value='Settings').classes('w-full') as tab_panels:
    t_tab = TriggerTab('Triggers')
    l_tab = LoggingTab("Logs")
    c_tab = ConstantTab("Constants")
    SettingsTab('Settings')


def update_tab(tab: str):
    match tab:
        case 'Triggers':
            t_tab.update()
        case 'Logs':
            l_tab.update()
        case 'Constants':
            c_tab.update()

    ui.notify("Refreshed", type='positive')


ui.run(title="Orchestrator", favicon='🤖', native=False)
