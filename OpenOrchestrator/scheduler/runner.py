"""This module is responsible for checking triggers and running processes."""

import os
import subprocess
from dataclasses import dataclass
import uuid

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import Trigger, SingleTrigger, ScheduledTrigger, QueueTrigger, TriggerStatus
from OpenOrchestrator.database.logs import LogLevel


@dataclass
class Job():
    """An object that holds information about a running job."""
    process: subprocess.Popen
    trigger: Trigger
    process_folder: str | None


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

    if next_single_trigger and not (next_single_trigger.is_blocking and other_processes_running):
        return run_single_trigger(next_single_trigger)

    # Scheduled triggers
    next_scheduled_trigger = db_util.get_next_scheduled_trigger()

    if next_scheduled_trigger and not (next_scheduled_trigger.is_blocking and other_processes_running):
        return run_scheduled_trigger(next_scheduled_trigger)

    # Queue triggers
    next_queue_trigger = db_util.get_next_queue_trigger()

    if next_queue_trigger and not (next_queue_trigger.is_blocking and other_processes_running):
        return run_queue_trigger(next_queue_trigger)

    return None


def run_single_trigger(trigger: SingleTrigger) -> Job | None:
    """Mark a single trigger as running in the database
    and start the process.

    Args:
        trigger: The trigger to run.

    Returns:
        Job: A Job object describing the process if successful.
    """

    print('Running trigger: ', trigger.trigger_name)

    if db_util.begin_single_trigger(trigger.id):
        return run_process(trigger)

    return None


def run_scheduled_trigger(trigger: ScheduledTrigger) -> Job | None:
    """Mark a scheduled trigger as running in the database,
    calculate the next run datetime,
    and start the process.

    Args:
        trigger: The trigger to run.

    Returns:
        Job: A Job object describing the process if successful.
    """
    print('Running trigger: ', trigger.trigger_name)

    if db_util.begin_scheduled_trigger(trigger.id):
        return run_process(trigger)

    return None


def run_queue_trigger(trigger: QueueTrigger) -> Job | None:
    """Mark a queue trigger as running in the database
    and start the process.

    Args:
        trigger: The trigger to run.

    Returns:
        Job: A Job object describing the process if successful.
    """
    print('Running trigger: ', trigger.trigger_name)

    if db_util.begin_queue_trigger(trigger.id):
        return run_process(trigger)

    return None


def clone_git_repo(repo_url: str) -> str:
    """Clone the git repo at the path to %USER%\\desktop\\Scheduler_Repos\\%UUID%.

    Args:
        repo_url: URL to the git repo to clone.

    Returns:
        str: The path to the cloned repo on the desktop.
    """
    repo_folder = get_repo_folder_path()
    unique_id = str(uuid.uuid4())
    repo_path = os.path.join(repo_folder, unique_id)

    os.makedirs(repo_path)
    try:
        subprocess.run(['git', 'clone', repo_url, repo_path], check=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Failed to clone git repo at {repo_url}.") from exc

    return repo_path


def clear_repo_folder() -> None:
    """Completely remove the repos folder."""
    repo_folder = get_repo_folder_path()
    clear_folder(repo_folder)


def get_repo_folder_path() -> str:
    """Gets the path to the folder where robot repos should be saved.

    Returns:
        str: The absolute path to the repo folder.
    """
    user_path = os.path.expanduser("~")
    repo_path = os.path.join(user_path, "Desktop", "Scheduler_Repos")
    return repo_path


def clear_folder(folder_path: str) -> None:
    """Clear a folder on the system.

    Args:
        folder_path: The folder to remove.
    """
    subprocess.run(['rmdir', '/s', '/q', folder_path], check=False, shell=True, capture_output=True)


def find_main_file(folder_path: str) -> str:
    """Finds the file in the given folder with the name 'main.py'.
    The search checks subfolders recursively.
    Only the first found file is returned.

    Args:
        folder_path: The path to the folder.

    Returns:
        str: The path to the main.py file.
    """
    for dir_path, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            if file_name == 'main.py':
                return os.path.join(dir_path, file_name)

    raise ValueError("No 'main.py' file found in the folder or its subfolders.")


def end_job(job: Job) -> None:
    """Mark a job as ended in the triggers table
    in the database.
    If it's a single trigger it's marked as 'Done'
    else it's marked as 'Idle' or 'Paused'.

    Args:
        job: The job whose trigger to mark as ended.
    """
    if isinstance(job.trigger, SingleTrigger):
        db_util.set_trigger_status(job.trigger.id, TriggerStatus.DONE)

    elif isinstance(job.trigger, (ScheduledTrigger, QueueTrigger)):
        current_status = db_util.get_trigger(job.trigger.id).process_status
        if current_status == TriggerStatus.PAUSING:
            db_util.set_trigger_status(job.trigger.id, TriggerStatus.PAUSED)
        elif current_status == TriggerStatus.RUNNING:
            db_util.set_trigger_status(job.trigger.id, TriggerStatus.IDLE)

    if job.process_folder:
        clear_folder(job.process_folder)


def fail_job(job: Job) -> None:
    """Mark a job as failed in the triggers table in the database.

    Args:
        job: The job whose trigger to mark as failed.
    """
    db_util.set_trigger_status(job.trigger.id, TriggerStatus.FAILED)
    _, error = job.process.communicate()
    error_msg = f"An uncaught error ocurred during the process:\n{error}"
    db_util.create_log(job.trigger.process_name, LogLevel.ERROR, error_msg)

    if job.process_folder:
        clear_folder(job.process_folder)


def run_process(trigger: Trigger) -> Job | None:
    """Runs the process of the given trigger with the necessary inputs:
    Process name
    Connection string
    Crypto key
    Process args

    If the trigger's process_path is pointing to a git repo the repo is cloned
    and the main.py file in the repo is found and run.

    Supports only .py files.

    If any exceptions occur during launch the trigger will be marked as failed.

    Args:
        trigger: The trigger whose process to run.

    Returns:
        Job: A Job object referencing the process if succesful.
    """
    process_path = trigger.process_path
    folder_path = None

    try:
        if trigger.is_git_repo:
            folder_path = clone_git_repo(process_path)
            process_path = find_main_file(folder_path)

        if not os.path.isfile(process_path):
            raise ValueError(f"The process path didn't point to a file on the system. Path: '{process_path}'")

        if not process_path.endswith(".py"):
            raise ValueError(f"The process path didn't point to a valid file. Supported files are [.py]. Path: '{process_path}'")

        conn_string = db_util.get_conn_string()
        crypto_key = crypto_util.get_key()

        command_args = ['python', process_path, trigger.process_name, conn_string, crypto_key, trigger.process_args]

        process = subprocess.Popen(command_args, stderr=subprocess.PIPE, text=True)  # pylint: disable=consider-using-with

        return Job(process, trigger, folder_path)

    # We actually want to catch any exception here
    # pylint: disable=broad-exception-caught
    except Exception as exc:
        db_util.set_trigger_status(trigger.id, TriggerStatus.FAILED)
        error_msg = f"Scheduler couldn't launch the process:\n{exc.__class__.__name__}:\n{exc}"
        db_util.create_log(trigger.process_name, LogLevel.ERROR, error_msg)
        print(error_msg)

    return None
