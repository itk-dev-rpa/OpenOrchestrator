"""This module contains tests for OrchestratorConnection."""

import unittest
from datetime import datetime
from uuid import UUID
import os

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.database.queues import QueueStatus

from OpenOrchestrator.tests import db_test_util


class TestOrchestratorConnection(unittest.TestCase):
    """Tests for OrchestratorConnection."""
    @classmethod
    def setUpClass(cls) -> None:
        db_test_util.establish_clean_database()
        process_name = "Process"
        cls.trigger_id = db_util.create_single_trigger(trigger_name=process_name,
                                                       process_name=process_name,
                                                       next_run=datetime.now(),
                                                       process_path="",
                                                       process_args="",
                                                       is_git_repo=False,
                                                       is_blocking=False,
                                                       priority=0,
                                                       scheduler_whitelist=""
                                                       )
        cls.connection = OrchestratorConnection("Process", os.environ["CONN_STRING"], crypto_util.get_key(), "Args", cls.trigger_id)

    def test_trigger_pause(self):
        """Test pausing triggers."""
        self.assertFalse(self.connection.is_trigger_pausing())
        self.connection.pause_my_trigger()
        self.assertTrue(self.connection.is_trigger_pausing())

    def test_logging(self):
        """Test all three logging functions."""
        # Create some logs
        self.connection.log_trace(LogLevel.TRACE.value)
        self.connection.log_info(LogLevel.INFO.value)
        self.connection.log_error(LogLevel.ERROR.value)

        # Do the same test for each level
        for level in LogLevel:
            log = db_util.get_logs(0, 1, log_level=level)[0]
            self.assertIsNotNone(log)

            self.assertIsInstance(log.id, UUID)
            self.assertEqual(log.log_level, level)
            self.assertEqual(log.log_message, level.value)
            self.assertIsInstance(log.log_time, datetime)
            self.assertEqual(log.process_name, "Process")

        logs = db_util.get_logs(0, 100)
        self.assertEqual(len(logs), 3)

    def test_constants(self):
        """Test all things constants."""
        # Create a constant
        db_util.create_constant("Constant", "Value")

        # Get constant
        constant = self.connection.get_constant("Constant")
        self.assertIsNotNone(constant)
        self.assertEqual(constant.name, "Constant")
        self.assertEqual(constant.value, "Value")
        self.assertIsInstance(constant.changed_at, datetime)

        # Update constant
        self.connection.update_constant("Constant", "New Value")
        constant = self.connection.get_constant("Constant")
        self.assertEqual(constant.value, "New Value")

    def test_credentials(self):
        """Test all things credentials."""
        # Create credential
        db_util.create_credential("Credential", "Username", "Password")

        # Get credential
        credential = self.connection.get_credential("Credential")
        self.assertIsNotNone(credential)
        self.assertEqual(credential.name, "Credential")
        self.assertEqual(credential.username, "Username")
        self.assertEqual(credential.password, "Password")
        self.assertIsInstance(credential.changed_at, datetime)

        # Update credential
        self.connection.update_credential("Credential", "New Username", "New Password")
        credential = self.connection.get_credential("Credential")
        self.assertEqual(credential.username, "New Username")
        self.assertEqual(credential.password, "New Password")

    def test_queue_elements(self):
        """Test all things queue elements."""
        # Create elements
        self.connection.create_queue_element("Queue")
        self.connection.create_queue_element("Queue", reference="Ref", data="data", created_by="Me")

        self.connection.bulk_create_queue_elements(
            "Bulk Queue",
            references=(None,)*10,
            data=("data",)*10,
            created_by="Me"
        )

        # Get elements
        elements = self.connection.get_queue_elements("Queue")
        self.assertEqual(len(elements), 2)

        elements = self.connection.get_queue_elements("Queue", "Ref")
        self.assertEqual(len(elements), 1)

        # Get next
        element = self.connection.get_next_queue_element("Bulk Queue", set_status=False)
        self.assertIsNotNone(element)
        self.assertEqual(element.status, QueueStatus.NEW)

        element = self.connection.get_next_queue_element("Bulk Queue")
        self.assertIsNotNone(element)
        self.assertEqual(element.status, QueueStatus.IN_PROGRESS)

        element2 = self.connection.get_next_queue_element("Bulk Queue")
        self.assertNotEqual(element, element2)

        # Set status
        self.connection.set_queue_element_status(element.id, QueueStatus.DONE)
        elements = self.connection.get_queue_elements("Bulk Queue", status=QueueStatus.DONE)
        self.assertEqual(len(elements), 1)

        # Delete element
        self.connection.delete_queue_element(element.id)
        elements = self.connection.get_queue_elements("Bulk Queue")
        self.assertEqual(len(elements), 9)


if __name__ == '__main__':
    unittest.main()
