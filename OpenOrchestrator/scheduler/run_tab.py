"""This module is responsible for the layout and functionality of the run tab
in Scheduler."""

from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter
from tkinter import ttk
import sys
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import exc as alc_exc

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.scheduler import runner, util
from OpenOrchestrator.database.triggers import TriggerStatus

if TYPE_CHECKING:
    from OpenOrchestrator.scheduler.application import Application


# Consecutive DB-error ticks since the last successful one. Tk's after-loop
# is single-threaded so a module-level int is safe.
_consecutive_db_failures = 0

_BASE_TICK_MS = 6_000
_MAX_BACKOFF_MS = 600_000  # 10 minutes
_DESKTOP_LOG_NAME = "OpenOrchestrator_scheduler_errors.log"


def _backoff_delay_ms() -> int:
    """Compute the next-tick delay using exponential backoff.

    Returns:
        Delay in milliseconds: ``_BASE_TICK_MS * 2**_consecutive_db_failures``
        clamped to ``_MAX_BACKOFF_MS``.
    """
    return min(_BASE_TICK_MS * (2 ** _consecutive_db_failures), _MAX_BACKOFF_MS)


def _log_to_desktop(exc: BaseException, context: str = "") -> None:
    """Append a timestamped traceback to a desktop log file.

    Used to surface scheduler-loop crashes outside the Tk text widget so they
    survive across restarts. Never raises - if the log can't be written the
    failure is swallowed so the scheduler loop itself can continue.

    Args:
        exc: The exception to record.
        context: Optional short string identifying the code path that raised.
    """
    try:
        desktop = Path.home() / "Desktop"
        desktop.mkdir(parents=True, exist_ok=True)
        log_path = desktop / _DESKTOP_LOG_NAME
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as f:
            f.write("\n" + ("=" * 80) + "\n")
            f.write(f"[{ts}] {exc.__class__.__name__}: {exc}\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(("-" * 80) + "\n")
            f.write(traceback.format_exc())
            f.write(("=" * 80) + "\n")
    except Exception:  # pylint: disable=broad-except
        pass


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

        try:
            n = runner.reconcile_orphans()
            if n > 0:
                print(f"*** Failed {n} orphan trigger(s) from previous run ***\n")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Orphan reconciliation failed: {e.__class__.__name__}: {e}")
            _log_to_desktop(e, context="reconcile_orphans during run()")

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
    """Run one Scheduler tick: pings, heartbeats, triggers, and reschedule.

    The body is fully guarded: any uncaught exception in a tick would
    otherwise break Tk's ``after``-chain and leave the scheduler frozen
    (see issues #152, #106). The reschedule lives in ``finally`` so the next
    tick is always queued.

    DB-class errors (``SQLAlchemyError`` and the ``RuntimeError`` raised by
    ``_get_session`` when there is no engine) route through an exponential
    backoff capped at ``_MAX_BACKOFF_MS``. ``pool_pre_ping`` on the engine
    is responsible for actually re-establishing the connection on subsequent
    ticks; this function only needs to keep ticking.

    Args:
        app: The Scheduler Application object.
    """
    global _consecutive_db_failures  # pylint: disable=global-statement

    delay_ms = _BASE_TICK_MS

    try:
        try:
            send_ping_to_orchestrator()

            check_heartbeats(app)

            if app.running:
                check_triggers(app)

        except (alc_exc.SQLAlchemyError, RuntimeError) as e:
            _consecutive_db_failures += 1
            delay_ms = _backoff_delay_ms()
            print("\n!!! LOST DATABASE CONNECTION "
                  f"(consecutive failures: {_consecutive_db_failures}) !!!")
            print(f"Error: {e.__class__.__name__}: {e}")
            print(f"Retrying in {delay_ms // 1000} seconds...\n")
            _log_to_desktop(e, context="scheduler loop - DB error")

        except Exception as e:  # pylint: disable=broad-except
            print("\n!!! UNEXPECTED SCHEDULER ERROR !!!")
            print(f"{e.__class__.__name__}: {e}")
            print("Will continue on next tick.\n")
            _log_to_desktop(e, context="scheduler loop - unexpected error")

        else:
            if _consecutive_db_failures > 0:
                print(f"\n*** Database connection restored after "
                      f"{_consecutive_db_failures} failed attempt(s) ***\n")
                _consecutive_db_failures = 0

        if len(app.running_jobs) == 0:
            try:
                print("Doing cleanup...")
                runner.clear_repo_folder()
            except Exception as e:  # pylint: disable=broad-except
                print(f"Cleanup failed: {e.__class__.__name__}: {e}")
                _log_to_desktop(e, context="clear_repo_folder")

    finally:
        if app.running or len(app.running_jobs) > 0:
            print(f'Waiting {delay_ms // 1000} seconds...\n')
            app.after(delay_ms, loop, app)
        else:
            print("Scheduler is paused and no more processes are running.")


def check_heartbeats(app: Application) -> None:
    """Reconcile each running job's state against its subprocess and the DB.

    Each per-job check is wrapped so a DB failure on one job does not abort
    the whole sweep; if any DB error occurred, the first one is re-raised
    after the loop so :func:`loop` enters the backoff path on this tick.

    Args:
        app: The Scheduler Application object.
    """
    print('Checking heartbeats...')
    db_errors: list[BaseException] = []
    for job in list(app.running_jobs):
        try:
            if job.process.poll() is not None:
                if job.process.returncode == 0:
                    print(f"Process '{job.trigger.process_name}' is done")
                    runner.end_job(job)
                else:
                    print(f"Process '{job.trigger.process_name}' failed. Check process log for more info.")
                    runner.fail_job(job)

                app.running_jobs.remove(job)

            elif db_util.get_trigger(job.trigger.id).process_status == TriggerStatus.KILLING:
                runner.kill_job(job)
                print(f"Process '{job.trigger.process_name}' has been killed.")
                app.running_jobs.remove(job)

            else:
                print(f"Process '{job.trigger.process_name}' is still running")
        except (alc_exc.SQLAlchemyError, RuntimeError) as e:
            print(f"DB unavailable while checking '{job.trigger.process_name}': "
                  f"{e.__class__.__name__}. Will retry next tick.")
            db_errors.append(e)

    if db_errors:
        raise db_errors[0]


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
