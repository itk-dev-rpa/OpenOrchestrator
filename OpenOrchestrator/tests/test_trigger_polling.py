"""This module contains tests for the trigger polling part of the Scheduler."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from OpenOrchestrator.scheduler import runner
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger
from OpenOrchestrator.tests import db_test_util


@patch("OpenOrchestrator.scheduler.util.get_scheduler_name", return_value="Machine")
class TestTriggerPolling(unittest.TestCase):
    """Test the trigger polling functionality of the Scheduler."""
    def setUp(self) -> None:
        db_test_util.establish_clean_database()

    def test_poll_triggers_single(self, *_):
        """Test polling single triggers."""
        mock_app = setup_mock_app(has_running_jobs=False, is_exclusive=False)

        # Test with no triggers
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        # Test with idle trigger
        db_util.create_single_trigger("Future single trigger", "", datetime(2100, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        # Test with overdue trigger
        db_util.create_single_trigger("Past single trigger", "", datetime(2020, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsInstance(trigger, SingleTrigger)
        self.assertEqual(trigger.trigger_name, "Past single trigger")

    def test_poll_triggers_priority(self, *_):
        """Test polling triggers with priorities set."""
        mock_app = setup_mock_app(has_running_jobs=False, is_exclusive=False)

        db_util.create_single_trigger("Low", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        db_util.create_single_trigger("High", "", datetime(2000, 1, 1), "", "", False, False, 100, [])

        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "High")

        db_util.create_single_trigger("Higher Future", "", datetime(2100, 1, 1), "", "", False, False, 200, [])

        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "High")

    def test_poll_triggers_mixed(self, *_):
        """Test mixed trigger types with priorities set.
        Equal priorities should be prioritied by trigger type:
        Single > Scheduled > Queue
        """
        mock_app = setup_mock_app(has_running_jobs=False, is_exclusive=False)

        db_util.create_queue_trigger("Queue", "", "Queue", "", "", False, False, 1, 0, [])
        db_util.create_queue_element("Queue")
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Queue")

        db_util.create_scheduled_trigger("Scheduled", "", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Scheduled")

        db_util.create_single_trigger("Single", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Single")

        db_util.create_queue_trigger("Queue High", "", "Queue", "", "", False, False, 1, 1, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Queue High")

        db_util.create_scheduled_trigger("Scheduled High", "", "", datetime(2000, 1, 1), "", "", False, False, 1, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Scheduled High")

        db_util.create_single_trigger("Single High", "", datetime(2000, 1, 1), "", "", False, False, 1, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Single High")

    def test_poll_triggers_blocking(self, *_):
        """Test polling triggers when other jobs are running."""
        mock_app = setup_mock_app(has_running_jobs=True, is_exclusive=False)

        db_util.create_single_trigger("Single Blocking", "", datetime(2000, 1, 1), "", "", False, True, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        db_util.create_single_trigger("Single Non-blocking", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Single Non-blocking")

    def test_poll_triggers_whitelist_non_exclusive(self, *_):
        """Test polling whitelisted triggers when Scheduler is not exclusive."""
        mock_app = setup_mock_app(has_running_jobs=False, is_exclusive=False)

        db_util.create_single_trigger("Single non machine", "", datetime(2000, 1, 1), "", "", False, False, 0, ["Non machine"])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        db_util.create_single_trigger("Single no whitelist", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Single no whitelist")

    def test_poll_triggers_whitelist_exclusive(self, *_):
        """Test polling whitelisted triggers when Scheduler is exclusive."""
        mock_app = setup_mock_app(has_running_jobs=False, is_exclusive=True)

        db_util.create_single_trigger("Single non machine", "", datetime(2000, 1, 1), "", "", False, False, 0, ["Non machine"])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        db_util.create_single_trigger("Single no whitelist", "", datetime(2000, 1, 1), "", "", False, False, 0, [])
        trigger = runner.poll_triggers(mock_app)
        self.assertIsNone(trigger)

        db_util.create_single_trigger("Single whitelist", "", datetime(2000, 1, 1), "", "", False, False, 0, ["Machine"])
        trigger = runner.poll_triggers(mock_app)
        self.assertEqual(trigger.trigger_name, "Single whitelist")


def setup_mock_app(*, has_running_jobs: bool, is_exclusive: bool) -> MagicMock:
    """Create a mock Application object to be used in tests.

    Args:
        has_running_jobs: If the app should simulate having running jobs.
        is_exclusive: If the app should simulate only running whitelisted triggers.

    Returns:
        A mock Application object.
    """
    mock_app = MagicMock()
    mock_app.running_jobs = [None] if has_running_jobs else []
    mock_app.settings_tab_.whitelist_value.get.return_value = is_exclusive
    return mock_app


if __name__ == '__main__':
    unittest.main()
