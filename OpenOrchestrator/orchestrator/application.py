"""This module is the entry point for the Orchestrator app. It contains a single class
that when created starts the application."""

from nicegui import ui, app

from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab
from OpenOrchestrator.orchestrator.tabs.settings_tab import SettingsTab
from OpenOrchestrator.orchestrator.tabs.logging_tab import LoggingTab
from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab
from OpenOrchestrator.orchestrator.tabs.queue_tab import QueueTab


class Application():
    """The main application of Orchestrator.
    It contains a header and the four tabs of the application.
    """
    def __init__(self) -> None:
        with ui.header():
            with ui.tabs() as self.tabs:
                ui.tab('Triggers')
                ui.tab('Logs')
                ui.tab('Constants')
                ui.tab('Queues')
                ui.tab('Settings')

            ui.space()
            ui.button(icon='refresh', on_click=self.update_tab).props('color=white text-color=primary')

        with ui.tab_panels(self.tabs, value='Settings', on_change=self.update_tab).classes('w-full') as self.tab_panels:
            self.t_tab = TriggerTab('Triggers')
            self.l_tab = LoggingTab("Logs")
            self.c_tab = ConstantTab("Constants")
            self.q_tab = QueueTab("Queues")
            SettingsTab('Settings')

        ui.run(title="Orchestrator", favicon='🤖', native=False, port=23406)
        app.on_connect(self.update_loop)

    def update_tab(self):
        """Update the date in the currently selected tab."""
        match self.tab_panels.value:
            case 'Triggers':
                self.t_tab.update()
            case 'Logs':
                self.l_tab.update()
            case 'Constants':
                self.c_tab.update()
            case 'Queues':
                self.q_tab.update()

    async def update_loop(self):
        """Update the selected tab on a timer but only if the page is in focus."""
        in_focus = await ui.run_javascript("document.hasFocus()")
        if in_focus:
            self.update_tab()

        ui.timer(10, self.update_loop, once=True)


if __name__ in {'__main__', '__mp_main__'}:
    Application()
