"""Tests for running a process and setting the process to PAUSING, expecting status to go to PAUSED."""
import unittest
import time
import os
import subprocess

from OpenOrchestrator.database import db_util
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database.triggers import TriggerStatus
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from OpenOrchestrator.tests import db_test_util


class TestRunProcess(unittest.TestCase):
    """Tests for running a process."""

    @classmethod
    def setUpClass(cls) -> None:
        db_test_util.establish_clean_database()
        cls.connection = OrchestratorConnection("Process", os.environ["CONN_STRING"], crypto_util.get_key(), "Args")

    def test_run_process(self):
        """Test running and pausing a process."""
        # Create a process and trigger
        process_file = os.path.join(os.getcwd(), "OpenOrchestrator", "tests", "process_pause_util.py")
        trigger_id = db_util.create_queue_trigger(trigger_name=self.connection.process_name,
                                                  process_name=self.connection.process_name,
                                                  queue_name=self.connection.process_name,
                                                  process_path=process_file,
                                                  process_args="",
                                                  is_git_repo=False,
                                                  is_blocking=False,
                                                  min_batch_size=1)
        # Create initial queue for checking run works
        for _ in range(4):
            db_util.create_queue_element(self.connection.process_name)  # Each queue element takes 1 second

        # Start running process trigger
        trigger = db_util.get_trigger(trigger_id)
        db_util.begin_queue_trigger(trigger.id)

        conn_string = db_util.get_conn_string()
        crypto_key = crypto_util.get_key()

        venv_python = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'Scripts', 'python.exe')
        command_args = [venv_python, trigger.process_path, trigger.process_name, conn_string, crypto_key, trigger.process_args]
        try:
            with subprocess.Popen(command_args) as fake_scheduler:
                time.sleep(1)

                # Confirm process runs
                process_status = db_util.get_trigger(trigger.id).process_status
                self.assertTrue(process_status == TriggerStatus.RUNNING)

                # Confirm process ends within X time
                fake_scheduler.wait(10)
        except Exception:
            print(process_file)

        process_status = db_util.get_trigger(trigger.id).process_status
        self.assertTrue(process_status == TriggerStatus.IDLE)

        # Create queue elements for pausing test
        for _ in range(8):
            db_util.create_queue_element(self.connection.process_name)

        # Start running process
        with subprocess.Popen(command_args) as fake_scheduler:
            db_util.begin_queue_trigger(trigger.id)
            time.sleep(4)

            # Pause process
            db_util.set_trigger_status(trigger.id, TriggerStatus.PAUSING)
            fake_scheduler.wait(10)

        # Confirm process paused
        process_status = db_util.get_trigger(trigger.id).process_status
        self.assertTrue(process_status == TriggerStatus.PAUSED)


if __name__ == '__main__':
    unittest.main()
