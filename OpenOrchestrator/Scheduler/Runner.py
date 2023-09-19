"""This module is responsible for checking triggers and running processes."""

from datetime import datetime
import subprocess

from croniter import croniter

from OpenOrchestrator.Common import db_util, crypto_util

class Job():
    """An object that holds information about a running job."""    
    def __init__(self, process, trigger_id, process_name, blocking, job_type):
        self.process = process
        self.trigger_id = trigger_id
        self.process_name = process_name
        self.blocking = blocking
        self.type = job_type


def poll_triggers(app) -> Job:
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
        name, next_run, uuid, process_path, is_git_repo, blocking = next_single_trigger

        if  next_run < datetime.now() and not (blocking and other_processes_running):
            return run_single_trigger(name, uuid, process_path, is_git_repo, blocking)

    # Email/Queue triggers

    # Scheduled triggers
    next_scheduled_trigger = db_util.get_next_scheduled_trigger()

    if next_scheduled_trigger is not None:
        name, next_run, uuid, process_path, is_git_repo, blocking, cron_expr = next_scheduled_trigger

        if next_run < datetime.now() and not (blocking and other_processes_running):
            return run_scheduled_trigger(name, uuid, process_path, is_git_repo, blocking, cron_expr, next_run)


    return None


def run_single_trigger(name: str, uuid: str, process_path: str,
                       is_git_repo: bool, blocking: bool) -> Job:
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
        Job: A Job object describing the process.
    """
    print('Running process: ', name, uuid, process_path)

    # Mark trigger as running
    db_util.begin_single_trigger(uuid)

    if is_git_repo:
        clone_git_repo(process_path)
        #TODO: Run main.*
    else:
        process = run_process(process_path, name, db_util.get_conn_string(), crypto_util.get_key())

    return Job(process, uuid, name, blocking, 'Single')


def run_scheduled_trigger(name: str, uuid: str, process_path: str,
                          is_git_repo: bool, blocking: bool,
                          cron_expr: str, next_run: datetime) -> Job:
    """Mark a scheduled trigger as running in the database,
    calculate the next run datetime,
    grab the process from git (if needed)
    and start the process.

    Args:
        name: The name of the process.
        uuid: The UUID of the process.
        process_path: The path of the process.
        is_git_repo: Whether the path points to a git repo.
        blocking: Whether the process is blocking.
        cron_expr: The cron expression of the process.
        next_run: The next run datetime of the trigger.

    Returns:
        Job: A Job object describing the process.
    """
    print('Running process: ', name, uuid, process_path)

    next_run = croniter(cron_expr, next_run).get_next(datetime)
    db_util.begin_scheduled_trigger(uuid, next_run)

    if is_git_repo:
        clone_git_repo(process_path)
        #TODO: Run main.*
    else:
        process = run_process(process_path, name, db_util.get_conn_string(), crypto_util.get_key())

    return Job(process, uuid, name, blocking, 'Scheduled')


def clone_git_repo(path: str) -> str:
    """Clone the git repo at the path to the desktop.

    Args:
        path: Path/URL to the git repo to clone.

    Returns:
        str: The path to the repo on the desktop.
    """
    raise NotImplementedError("Clone git repo not implemented")


def end_job(job: Job) -> None:
    """Mark a job as ended in the triggers table
    in the database.
    If it's a single trigger it's marked as 'Done'
    else it's marked as 'Idle'.

    Args:
        job: The job whose trigger to mark as ended.
    """
    if job.type == 'Single':
        db_util.set_single_trigger_status(job.trigger_id, 3)
    elif job.type == 'Scheduled':
        db_util.set_scheduled_trigger_status(job.trigger_id, 0)
    elif job.type == 'Queue':
        ...


def fail_job(job: Job) -> None:
    """Mark a job as failed in the triggers table in the database.

    Args:
        job: The job whose trigger to mark as failed.
    """
    if job.type == 'Single':
        db_util.set_single_trigger_status(job.trigger_id, 2)
    elif job.type == 'Scheduled':
        db_util.set_scheduled_trigger_status(job.trigger_id, 2)
    elif job.type == 'Queue':
        ...


def run_process(path: str, process_name: str, conn_string: str, crypto_key: str) -> subprocess.Popen:
    """Runs the process at the given path with the necessary inputs:
    Process name
    Connection string
    Crypto key

    Supports .py and .bat files.

    Args:
        path: Path to the process script file.
        process_name: The name of the process (for logging).
        conn_string: The connection string to the database.
        crypto_key: The crypto key to the database.

    Raises:
        ValueError: If the path doesn't point to a valid file.

    Returns:
        subprocess.Popen: The Popen instance of the process.
    """
    if path.endswith(".py"):
        return subprocess.Popen(['python', path, process_name, conn_string, crypto_key])
    elif path.endswith(".bat"):
        return subprocess.Popen([path, process_name, conn_string, crypto_key])

    raise ValueError(f"The process path didn't point to a valid file. Supported files are .py and .bat. Path: '{path}'")
