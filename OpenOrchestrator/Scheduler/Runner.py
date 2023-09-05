from datetime import datetime
import subprocess
from croniter import croniter
from OpenOrchestrator.Scheduler import DB_util, Crypto_util

class Job():
    def __init__(self, process, trigger_id, process_name, blocking, type):
        self.process = process
        self.trigger_id = trigger_id
        self.process_name = process_name
        self.blocking = blocking
        self.type = type

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
    next_single_trigger = DB_util.get_next_single_trigger()

    if next_single_trigger is not None:
        name, next_run, id, process_path, is_git_repo, blocking = next_single_trigger

        if  next_run < datetime.now() and not (blocking and other_processes_running):
            return run_single_trigger(app, name, id, process_path, is_git_repo, blocking)

    # Email/Queue triggers

    # Scheduled triggers
    next_scheduled_trigger = DB_util.get_next_scheduled_trigger()

    if next_scheduled_trigger is not None:
        name, next_run, id, process_path, is_git_repo, blocking, cron_expr = next_scheduled_trigger

        if next_run < datetime.now() and not (blocking and other_processes_running):
            return run_scheduled_trigger(app, name, id, process_path, is_git_repo, blocking, cron_expr, next_run)


    return None

def run_single_trigger(app, name, id, process_path, is_git_repo, blocking):
    print('Running process: ', name, id, process_path)

    # Mark trigger as running
    DB_util.begin_single_trigger(id)

    if is_git_repo:
        grab_git_repo(process_path)
        ...
        #TODO: Run main.*
    else:
        process = run_process(process_path, name, DB_util.get_conn_string(), Crypto_util.get_key())

    return Job(process, id, name, blocking, 'Single')

def run_scheduled_trigger(app, name, id, process_path, is_git_repo, blocking, cron_expr, next_run):
    print('Running process: ', name, id, process_path)

    next_run = croniter(cron_expr, next_run).get_next(datetime)
    DB_util.begin_scheduled_trigger(id, next_run)

    if is_git_repo:
        grab_git_repo(process_path)
        ...
        #TODO: Run main.*
    else:
        process = run_process(process_path, name, DB_util.get_conn_string(), Crypto_util.get_key())
    
    return Job(process, id, name, blocking, 'Scheduled')


def grab_git_repo(path):
    ...

def end_job(job: Job):
    if job.type == 'Single':
        DB_util.set_single_trigger_status(job.trigger_id, 3)
    elif job.type == 'Scheduled':
        DB_util.set_scheduled_trigger_status(job.trigger_id, 0)
    elif job.type == 'Queue':
        ...

def fail_job(job: Job):
    if job.type == 'Single':
        DB_util.set_single_trigger_status(job.trigger_id, 2)
    elif job.type == 'Scheduled':
        DB_util.set_scheduled_trigger_status(job.trigger_id, 2)
    elif job.type == 'Queue':
        ...

def run_process(path:str, process_name, conn_string:str, crypto_key:str):
    if path.endswith(".py"):
        return subprocess.Popen(['python', path, process_name, conn_string, crypto_key])
    elif path.endswith(".bat"):
        return subprocess.Popen([path, process_name, conn_string, crypto_key])
    
    raise ValueError("The process path didn't point to a valid file. Supported files are .py and .bat. Path: "+path)
