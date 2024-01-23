"""This module is responsible for the layout and functionality of the run tab
in Scheduler."""

import tkinter
from tkinter import ttk
import sys

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.scheduler import runner


def create_tab(parent: ttk.Notebook, app) -> ttk.Frame:
    """Create a new Run tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.
        app: The Scheduler application object.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    status_label = ttk.Label(tab, text="State: Paused")
    status_label.pack()

    ttk.Button(tab, text="Run", command=lambda: run(app, status_label)).pack()
    ttk.Button(tab, text="Pause", command=lambda: pause(app, status_label)).pack()

    # Text area
    text_frame = tkinter.Frame(tab)
    text_frame.pack()

    text_area = tkinter.Text(text_frame, state='disabled', wrap='none')
    sys.stdout.write = lambda s: print_text(text_area, s)

    text_yscroll = ttk.Scrollbar(text_frame, orient='vertical', command=text_area.yview)
    text_yscroll.pack(side='right', fill='y')
    text_area.configure(yscrollcommand=text_yscroll.set)

    text_xscroll = ttk.Scrollbar(text_frame, orient='horizontal', command=text_area.xview)
    text_xscroll.pack(side='bottom', fill='x')
    text_area.configure(xscrollcommand=text_xscroll.set)

    text_area.pack()

    return tab


def run(app, status_label: ttk.Label) -> None:
    """Starts the Scheduler and sets the app's status to 'running'.

    Args:
        app: The Scheduler application object.
        status_label: The label showing the current status.
    """
    if db_util.get_conn_string() is None:
        print("Can't start without a valid connection string. Go to the settings tab to configure the connection string")
        return
    if crypto_util.get_key() is None:
        print("Can't start without a valid encryption key. Go to the settings tab to configure the encryption key")
        return

    if not app.running:
        status_label.configure(text='State: Running')
        print('Running...\n')
        app.running = True

        # Only start loop if it's not already running
        if app.tk.call('after', 'info') == '':
            app.after(0, loop, app)


def pause(app, status_label: ttk.Label):
    """Stops the Scheduler and sets the app's status to 'paused'.

    Args:
        app: The Scheduler application object.
        status_label: The label showing the current status.
    """
    if app.running:
        status_label.configure(text="State: Paused")
        print('Paused... Please wait for all processes to stop before closing the application\n')
        app.running = False


def print_text(text_widget: tkinter.Text, string: str) -> None:
    """Appends text to the text area.
    Is used to replace the functionality of sys.stdout.write (print).

    Args:
        print_text: The text area object.
        string: The string to append.
    """
    text_widget.configure(state='normal')
    text_widget.insert('end', string)
    text_widget.see('end')
    text_widget.configure(state='disabled')


def loop(app) -> None:
    """The main loop function of the Scheduler.
    Checks heartbeats, check triggers, and schedules the next loop.

    Args:
        app: The Scheduler Application object.
    """
    check_heartbeats(app)

    if app.running:
        check_triggers(app)

    if len(app.running_jobs) == 0:
        print("Doing cleanup...")
        runner.clear_repo_folder()

    # Schedule next loop
    if app.running or len(app.running_jobs) > 0:
        print('Waiting 6 seconds...\n')
        app.after(6_000, loop, app)
    else:
        print("Scheduler is paused and no more processes are running.")


def check_heartbeats(app) -> None:
    """Check if any running jobs are still running, failed or done.

    Args:
        app: The Scheduler Application object.
    """
    print('Checking heartbeats...')
    for job in app.running_jobs:
        if job.process.poll() is not None:
            app.running_jobs.remove(job)

            if job.process.returncode == 0:
                print(f"Process '{job.trigger.process_name}' is done")
                runner.end_job(job)
            else:
                print(f"Process '{job.trigger.process_name}' failed. Check process log for more info.")
                runner.fail_job(job)

        else:
            print(f"Process '{job.trigger.process_name}' is still running")


def check_triggers(app) -> None:
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
        job = runner.poll_triggers(app)

        if job is not None:
            app.running_jobs.append(job)
