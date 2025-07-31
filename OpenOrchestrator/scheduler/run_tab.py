"""This module is responsible for the layout and functionality of the run tab
in Scheduler."""

from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter
from tkinter import ttk
import sys

from sqlalchemy import exc as alc_exc

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.scheduler import runner, util

if TYPE_CHECKING:
    from OpenOrchestrator.scheduler.application import Application


# pylint: disable-next=too-many-ancestors
class RunTab(ttk.Frame):
    """A ttk.frame object containing the functionality of the run tab in Scheduler."""
    def __init__(self, parent: ttk.Notebook, app: Application):
        super().__init__(parent)
        self.pack(fill='both', expand=True)

        self.app = app

        s = ttk.Style()
        s.configure('my.TButton', font=('Helvetica Bold', 24))
        self.button = ttk.Button(self, text="Run", command=self.button_click, style='my.TButton')
        self.button.pack()

        # Text area
        text_frame = tkinter.Frame(self)
        text_frame.pack()

        self.text_area = tkinter.Text(text_frame, state='disabled', wrap='none')

        # Redirect stdout to the text area instead of console
        sys.stdout.write = self.print_text

        # Add scroll bars to text area
        text_yscroll = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_area.yview)
        text_yscroll.pack(side='right', fill='y')
        self.text_area.configure(yscrollcommand=text_yscroll.set)

        text_xscroll = ttk.Scrollbar(text_frame, orient='horizontal', command=self.text_area.xview)
        text_xscroll.pack(side='bottom', fill='x')
        self.text_area.configure(xscrollcommand=text_xscroll.set)

        self.text_area.pack()

    def button_click(self):
        """Callback for when the run/pause button is clicked."""
        if self.app.running:
            self.pause()
        else:
            self.run()

    def pause(self):
        """Stops the Scheduler and sets the app's status to 'paused'."""
        self.button.configure(text="Run")
        print('Paused... Please wait for all processes to stop before closing the application\n')
        self.app.running = False

    def run(self):
        """Starts the Scheduler and sets the app's status to 'running'."""
        if db_util.get_conn_string() is None:
            print("Can't start without a valid connection string. Go to the settings tab to configure the connection string")
            return
        if crypto_util.get_key() is None:
            print("Can't start without a valid encryption key. Go to the settings tab to configure the encryption key")
            return

        self.button.configure(text="Pause")
        print('Running...\n')
        self.app.running = True

        # Only start a new loop if it's not already running
        if self.app.tk.call('after', 'info') == '':
            self.app.after(0, loop, self.app)

    def print_text(self, text: str) -> None:
        """Appends text to the text area.
        Is used to replace the functionality of sys.stdout.write (print).

        Args:
            string: The string to append.
        """
        # Insert text at the end
        self.text_area.configure(state='normal')
        self.text_area.insert('end', text)

        # If the number of lines are above 1000 delete 10 lines from the top
        num_lines = int(self.text_area.index('end').split('.', maxsplit=1)[0])
        if num_lines > 1000:
            self.text_area.delete("1.0", "10.0")

        # Scroll to end
        self.text_area.see('end')
        self.text_area.configure(state='disabled')


def loop(app: Application) -> None:
    """The main loop function of the Scheduler.
    Checks heartbeats, check triggers, and schedules the next loop.

    Args:
        app: The Scheduler Application object.
    """
    try:
        send_ping_to_orchestrator()

        check_heartbeats(app)

        if app.running:
            check_triggers(app)

    except (alc_exc.OperationalError, alc_exc.ProgrammingError) as e:
        print(f"Couldn't connect to database. {e}")

    if len(app.running_jobs) == 0:
        print("Doing cleanup...")
        runner.clear_repo_folder()

    # Schedule next loop
    if app.running or len(app.running_jobs) > 0:
        print('Waiting 6 seconds...\n')
        app.after(6_000, loop, app)
    else:
        print("Scheduler is paused and no more processes are running.")


def check_heartbeats(app: Application) -> None:
    """Check if any running jobs are still running, failed or done.

    Args:
        app: The Scheduler Application object.
    """
    print('Checking heartbeats...')
    for job in app.running_jobs:
        if job.process.poll() is not None:
            if job.process.returncode == 0:
                print(f"Process '{job.trigger.process_name}' is done")
                runner.end_job(job)
            else:
                print(f"Process '{job.trigger.process_name}' failed. Check process log for more info.")
                runner.fail_job(job)

            app.running_jobs.remove(job)
        else:
            print(f"Process '{job.trigger.process_name}' is still running")


def check_triggers(app: Application) -> None:
    """Checks any process is blocking
    and if not checks if any trigger should be run.

    Args:
        app: The Scheduler Application object.
    """
    # Check if process is blocking
    blocking = False
    for job in app.running_jobs:
        if job.trigger.is_blocking:
            print(f"Process '{job.trigger.process_name}' is blocking\n")
            blocking = True

    # Check triggers
    if not blocking:
        print('Checking triggers...')
        trigger = runner.poll_triggers(app)

        if trigger:
            job = runner.run_trigger(trigger)

            if job:
                app.running_jobs.append(job)


def send_ping_to_orchestrator():
    """Send a ping to the connected Orchestrator with the Scheduler application's name."""
    db_util.send_ping_from_scheduler(util.get_scheduler_name())
