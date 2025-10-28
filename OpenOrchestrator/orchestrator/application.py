"""This module is the entry point for the Orchestrator app. It contains a single class
that when created starts the application."""

import socket

from nicegui import ui, app

from OpenOrchestrator.orchestrator.tabs.trigger_tab import TriggerTab
from OpenOrchestrator.orchestrator.tabs.settings_tab import SettingsTab
from OpenOrchestrator.orchestrator.tabs.logging_tab import LoggingTab
from OpenOrchestrator.orchestrator.tabs.jobs_tab import JobsTab
from OpenOrchestrator.orchestrator.tabs.constants_tab import ConstantTab
from OpenOrchestrator.orchestrator.tabs.queue_tab import QueueTab
from OpenOrchestrator.orchestrator.tabs.schedulers_tab import SchedulerTab


class Application():
    """The main application of Orchestrator.
    It contains a header and the four tabs of the application.
    """
    def __init__(self, port: int | None = None, show: bool = True) -> None:
        with ui.header():
            with ui.tabs() as self.tabs:
                ui.tab('Triggers').props("auto-id=trigger_tab")
                ui.tab('Queues').props("auto-id=queues_tab")
                ui.tab('Schedulers').props("auto-id=schedulers_tab")
                ui.tab('Jobs').props("auto-id=jobs_tab")
                ui.tab('Logs').props("auto-id=logs_tab")
                ui.tab('Constants').props("auto-id=constants_tab")
                ui.tab('Settings').props("auto-id=settings_tab")

            ui.space()
            ui.button(icon="contrast", on_click=ui.dark_mode().toggle)
            ui.button(icon='refresh', on_click=self.update_tab).props("auto-id=refresh_button")

        with ui.tab_panels(self.tabs, value='Settings', on_change=self.update_tab).classes('w-full') as self.tab_panels:
            self.t_tab = TriggerTab('Triggers')
            self.q_tab = QueueTab("Queues")
            self.j_tab = JobsTab("Jobs")
            self.l_tab = LoggingTab("Logs")
            self.s_tab = SchedulerTab("Schedulers")
            self.c_tab = ConstantTab("Constants")
            self.j_tab.set_log_tab(self.l_tab)
            SettingsTab('Settings')

        self._define_on_close()

        app.on_connect(self.update_loop)
        app.on_exception(lambda exc: ui.notify(exc, type='negative'))
        ui.run(title="Orchestrator", favicon='🤖', native=False, port=port or get_free_port(), reload=False, show=show)

    def update_tab(self):
        """Update the date in the currently selected tab."""
        match self.tab_panels.value:
            case 'Triggers':
                self.t_tab.update()
            case 'Queues':
                self.q_tab.update()
            case 'Jobs':
                self.j_tab.update()
            case 'Logs':
                self.l_tab.update()
            case 'Schedulers':
                self.s_tab.update()
            case 'Constants':
                self.c_tab.update()

    async def update_loop(self):
        """Update the selected tab on a timer but only if the page is in focus."""
        try:
            in_focus = await ui.run_javascript("document.hasFocus()")
            if in_focus:
                self.update_tab()
        except TimeoutError:
            pass

        ui.timer(10, self.update_loop, once=True)

    def _define_on_close(self) -> None:
        """Tell the browser to ask for confirmation before leaving the page."""
        ui.add_body_html('''
            <script>
                window.addEventListener("beforeunload", (event) => event.preventDefault());
            </script>
            ''')


def get_free_port():
    """Get a free port by creating a new socket and bind it
    on port 0 allowing the os to select the port.
    https://docs.python.org/3/library/socket.html#socket.create_connection

    Returns:
        A port number that should be free to use.
    """
    with socket.socket() as sock:
        sock.bind(("", 0))
        port = sock.getsockname()[1]

    return port


if __name__ in {'__main__', '__mp_main__'}:
    Application()
