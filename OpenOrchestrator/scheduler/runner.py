"""This module is responsible for checking triggers and running processes."""

import os
from datetime import datetime
import subprocess
from dataclasses import dataclass
import uuid

from croniter import croniter

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util

SCHEDULED = 'Scheduled'
SINGLE = 'Single'
QUEUE = 'Queue'


@dataclass
class Job():
    """An object that holds information about a running job."""
    process: subprocess.Popen
    trigger_id: str
    process_name: str
    is_git: bool
    blocking: bool
    type: str


def poll_triggers(app) -> Job | None:
    """Checks if any triggers are waiting to run. If any the first will be run and a
    corresponding job object will be returned.

    Args:
        app: The Application object of the Scheduler app.

    Returns:
        Job: A job object describing the job that has been launched, if any else None.
    """

    other_processes_running = len(app.running_jobs) != 0

    # Single triggers
    next_single_trigger = db_util.get_next_single_trigger()

    if next_single_trigger is not None:
        name, next_run, trigger_id, process_path, is_git_repo, blocking = next_single_trigger

        if  next_run < datetime.now() and not (blocking and other_processes_running):
            return run_single_trigger(name, trigger_id, process_path, is_git_repo, blocking)

    # Email/Queue triggers

    # Scheduled triggers
    next_scheduled_trigger = db_util.get_next_scheduled_trigger()

    if next_scheduled_trigger is not None:
        name, next_run, trigger_id, process_path, is_git_repo, blocking, cron_expr = next_scheduled_trigger

        if next_run < datetime.now() and not (blocking and other_processes_running):
            return run_scheduled_trigger(name, trigger_id, process_path, is_git_repo, blocking, cron_expr, next_run)

    return None


def run_single_trigger(name: str, trigger_id: str, process_path: str,
                       is_git_repo: bool, blocking: bool) -> Job | None:
    """Mark a single trigger as running in the database,
    grab the process from git (if needed)
    and start the process.

    Args:
        name: The name of the process.
        uuid: The UUID of the process.
        process_path: The path of the process.
        is_git_repo: Whether the path points to a git repo.
        blocking: Whether the process is blocking.

    Returns:
        Job: A Job object describing the process if successful.
    """

    print('Running process: ', name, trigger_id, process_path)

    db_util.begin_single_trigger(trigger_id)

    process = run_process(trigger_id, process_path, name, is_git_repo)

    if process is None:
        return None

    return Job(process, trigger_id, name, is_git_repo, blocking, SINGLE)


def run_scheduled_trigger(name: str, trigger_id: str, process_path: str,
                          is_git_repo: bool, blocking: bool,
                          cron_expr: str, next_run: datetime) -> Job | None:
    """Mark a scheduled trigger as running in the database,
    calculate the next run datetime,
    and start the process.

    Args:
        name: The name of the process.
        trigger_id: The UUID of the trigger.
        process_path: The path of the process.
        is_git_repo: Whether the path points to a git repo.
        blocking: Whether the process is blocking.
        cron_expr: The cron expression of the process.
        next_run: The next run datetime of the trigger.

    Returns:
        Job: A Job object describing the process if successful.
    """
    print('Running process: ', name, trigger_id, process_path)

    next_run = croniter(cron_expr, next_run).get_next(datetime)
    db_util.begin_scheduled_trigger(trigger_id, next_run)

    process = run_process(trigger_id, process_path, name, is_git_repo)

    if process is None:
        return None

    return Job(process, trigger_id, name, is_git_repo, blocking, SCHEDULED)


def clone_git_repo(repo_url: str) -> str:
    """Clone the git repo at the path to %USER%\\desktop\\Scheduler_Repos\\%UUID%.

    Args:
        repo_url: URL to the git repo to clone.

    Returns:
        str: The path to the cloned repo on the desktop.
    """
    desktop_path = os.path.expanduser("~\\Desktop")
    unique_id = str(uuid.uuid4())
    repo_path = os.path.join(desktop_path, "Scheduler_Repos", unique_id)

    os.makedirs(repo_path)
    try:
        subprocess.run(['git', 'clone', repo_url, repo_path], check=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Failed to clone git repo at {repo_url}.") from exc

    return repo_path


def find_main_file(folder_path: str) -> str:
    """Finds the file in the given folder with the name 'main.py' or 'main.bat'.
    The search checks subfolders recursively.
    Only the first found file is returned.

    Args:
        folder_path: The path to the folder.

    Returns:
        str: The path to the main.* file.
    """
    for dir_path, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            name, ext = os.path.splitext(file_name)
            if name == 'main' and ext in ('.py', '.bat'):
                return os.path.join(dir_path, file_name)

    raise ValueError("No 'main.*' file found in the folder or its subfolders.")


def end_job(job: Job) -> None:
    """Mark a job as ended in the triggers table
    in the database.
    If it's a single trigger it's marked as 'Done'
    else it's marked as 'Idle'.

    Args:
        job: The job whose trigger to mark as ended.
    """
    if job.type == SINGLE:
        db_util.set_trigger_status(job.trigger_id, 3)
    elif job.type == SCHEDULED:
        db_util.set_trigger_status(job.trigger_id, 0)
    elif job.type == QUEUE:
        ...


def fail_job(job: Job) -> None:
    """Mark a job as failed in the triggers table in the database.

    Args:
        job: The job whose trigger to mark as failed.
    """
    db_util.set_trigger_status(job.trigger_id, 2)



def run_process(trigger_id: str, process_path: str, process_name: str, is_git_repo: bool) -> subprocess.Popen | None:
    """Runs the process at the given path with the necessary inputs:
    Process name
    Connection string
    Crypto key

    If the process_path is pointing to a git repo the repo is cloned
    and the main.* file in the repo is found and run.

    Supports .py and .bat files.

    If any exceptions occur during launch the trigger will be marked as failed.

    Args:
        trigger_id: The UUID of the trigger.
        process_path: Path to the process script file.
        process_name: The name of the process (for logging).
        is_git_repo: If the process path points to a git repo.
        conn_string: The connection string to the database.
        crypto_key: The crypto key to the database.

    Returns:
        subprocess.Popen: The Popen instance of the process if successful.
    """
    try:
        if is_git_repo:
            git_folder_path = clone_git_repo(process_path)
            process_path = find_main_file(git_folder_path)

        if not os.path.isfile(process_path):
            raise ValueError(f"The process path didn't point to a file on the system. Path: '{process_path}'")

        conn_string = db_util.get_conn_string()
        crypto_key = crypto_util.get_key()

        if process_path.endswith(".py"):
            return subprocess.Popen(['python', process_path, process_name, conn_string, crypto_key])

        if process_path.endswith(".bat"):
            return subprocess.Popen([process_path, process_name, conn_string, crypto_key])

        raise ValueError(f"The process path didn't point to a valid file. Supported files are .py and .bat. Path: '{process_path}'")

    # pylint: disable=broad-exception-caught
    except Exception as exc:
        db_util.set_trigger_status(trigger_id, 2)
        error_msg = f"Scheduler couldn't launch the process:\n{exc.__class__.__name__}:\n{exc}"
        db_util.create_log(process_name, 2, error_msg)
        print(error_msg)

    return None
