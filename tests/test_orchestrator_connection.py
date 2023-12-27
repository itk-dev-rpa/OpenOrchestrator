import unittest
from datetime import datetime
from uuid import UUID

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel

from tests import db_test_util


class TestOrchestratorConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        db_test_util.establish_clean_database()
        cls.connection = OrchestratorConnection("Process", db_test_util.CONNECTION_STRING, crypto_util.get_key(), "Args")

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
        pass

    def test_create_from_args(self):
        """I have no idea how to do this..."""
