import time
import sys

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import TriggerStatus


def run_queue_elements(conn: OrchestratorConnection):
    # Get queue elements
    queue_elements = db_util.get_queue_elements(conn.process_name, status=QueueStatus.NEW)
    # Iterate through queue and check for pausing
    for queue_element in queue_elements:
        time.sleep(1)
        db_util.set_queue_element_status(queue_element.id, QueueStatus.DONE)
        if conn.is_process_pausing():
            conn.pause_my_triggers()
            return False
    return True
    # End


if __name__ == "__main__":
    oc = OrchestratorConnection(process_name=sys.argv[1], connection_string=sys.argv[2], crypto_key=sys.argv[3], process_arguments="")
    trigger = db_util.get_triggers(oc.process_name)[0]
    db_util.set_trigger_status(trigger.id, TriggerStatus.RUNNING)
    if run_queue_elements(oc):
        db_util.set_trigger_status(trigger.id, TriggerStatus.IDLE)
