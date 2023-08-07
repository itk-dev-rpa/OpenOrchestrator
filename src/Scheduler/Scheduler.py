import DB_util
from datetime import datetime
import subprocess
import time

class Job():
    def __init__(self, process, trigger_id, process_name, blocking):
        self.process = process
        self.trigger_id = trigger_id
        self.process_name = process_name
        self.blocking = blocking

def poll_triggers(app):
    conn = app.get_db_connection()

    # Single triggers
    command = DB_util.load_sql_file('Get_Next_Single_Trigger.sql')
    cursor = conn.execute(command)
    next_single_trigger = cursor.fetchone()

    if next_single_trigger:
        name, next_run, id, process_path, is_git_repo, blocking = next_single_trigger

        if next_run < datetime.now():
            # TODO: Check if blocking
            return run_single_trigger(app, name, id, process_path, is_git_repo, blocking)

    # Email/Queue triggers

    # Scheduled triggers
    command = DB_util.load_sql_file('Get_Next_Scheduled_Trigger.sql')
    cursor = conn.execute(command)
    next_scheduled_trigger = cursor.fetchone()


    return None

def run_single_trigger(app, name, id, process_path, is_git_repo, blocking):
    print('Running process: ', name, id, process_path)

    # Mark trigger as running
    conn = app.get_db_connection()
    command = DB_util.load_sql_file('Begin_Single_Trigger.sql')
    command = command.replace('{UUID}', id)
    conn.execute(command)
    conn.commit()

    if is_git_repo:
        grab_git_repo(process_path)
        ...
        #TODO: Run main.*
    else:
        process = subprocess.Popen(process_path, shell=True)

    return Job(process, id, name, blocking)

def grab_git_repo(path):
    ...

