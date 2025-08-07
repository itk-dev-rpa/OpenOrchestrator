"""This module contains tests of the functionality of db_util."""

import unittest
from datetime import datetime, timedelta
import time

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.database.triggers import TriggerStatus

from OpenOrchestrator.tests import db_test_util


class TestDBUtil(unittest.TestCase):
    """Test functionality of db_util."""
    def setUp(self) -> None:
        db_test_util.establish_clean_database()

    def test_logs(self):
        """Test creation of logs and retrieval by different filters."""
        # Create some logs
        creation_time = datetime.now() - timedelta(seconds=2)

        for i in range(3):
            db_util.create_log(f"Test {i}", LogLevel.TRACE, "Message")
            db_util.create_log(f"Test {i}", LogLevel.INFO, "Message")
            db_util.create_log(f"Test {i}", LogLevel.ERROR, "Message")

        # Get all logs
        logs = db_util.get_logs(0, 100)
        self.assertEqual(len(logs), 9)

        # Filter by level
        logs = db_util.get_logs(0, 100, log_level=LogLevel.TRACE)
        self.assertEqual(len(logs), 3)

        # Get unique processes
        process_names = db_util.get_unique_log_process_names()
        self.assertEqual(len(process_names), 3)

        # Filter by process
        logs = db_util.get_logs(0, 100, process_name=process_names[0])
        self.assertEqual(len(logs), 3)

        # Filter by process and level
        logs = db_util.get_logs(0, 100, log_level=LogLevel.INFO, process_name=process_names[1])
        self.assertEqual(len(logs), 1)

        # Filter by date
        logs = db_util.get_logs(0, 100, from_date=creation_time)
        self.assertEqual(len(logs), 9)

        logs = db_util.get_logs(0, 100, to_date=creation_time)
        self.assertEqual(len(logs), 0)

    def test_constants(self):
        """Test all things constants."""
        # Create some constants
        db_util.create_constant("Constant1", "Value1")
        db_util.create_constant("Constant2", "Value2")

        # Get all constants
        constants = db_util.get_constants()
        self.assertEqual(len(constants), 2)

        # Get specific constant
        constant = db_util.get_constant("Constant1")
        self.assertEqual(constant.value, "Value1")
        created_at = constant.changed_at
        self.assertIsInstance(created_at, datetime)

        # Update constant
        time.sleep(0.1)
        db_util.update_constant("Constant1", "New Value")
        constant = db_util.get_constant("Constant1")
        self.assertEqual(constant.value, "New Value")
        self.assertGreater(constant.changed_at, created_at)

        # Delete constant
        db_util.delete_constant("Constant1")
        with self.assertRaises(ValueError):
            db_util.get_constant("Constant1")

    def test_credentials(self):
        """Test all things credentials."""
        # Create some credentials
        db_util.create_credential("Cred1", "User1", "Pass")
        db_util.create_credential("Cred2", "User2", "Pass")

        # Get all credentials
        creds = db_util.get_credentials()
        self.assertEqual(len(creds), 2)

        # Check encryption salt
        self.assertNotEqual(creds[0].password, creds[1].password)

        # Get credential
        cred = db_util.get_credential("Cred1")
        self.assertEqual(cred.username, "User1")
        self.assertEqual(cred.password, "Pass")
        created_at = cred.changed_at
        self.assertIsInstance(created_at, datetime)

        # Update credential
        time.sleep(0.1)
        db_util.update_credential("Cred1", "New User", "New Pass")
        cred = db_util.get_credential("Cred1")
        self.assertEqual(cred.username, "New User")
        self.assertEqual(cred.password, "New Pass")
        self.assertGreater(cred.changed_at, created_at)

        # Delete credential
        db_util.delete_credential("Cred1")
        with self.assertRaises(ValueError):
            db_util.get_credential("Cred1")

    def test_queue_elements(self):
        """Test all things queue elements."""
        # Create some queue elements
        creation_time = datetime.now() - timedelta(seconds=2)

        db_util.create_queue_element("Queue")
        db_util.create_queue_element("Queue", reference="Ref", data="Data", created_by="Me")

        # Bulk create queue elements
        refs = tuple(f"Ref{i}" for i in range(10))
        data = (None,) * 10
        db_util.bulk_create_queue_elements("Bulk", references=refs, data=data)

        with self.assertRaises(ValueError):
            db_util.bulk_create_queue_elements("Bulk", ("Ref",), ())

        # Get elements
        elements = db_util.get_queue_elements("Queue")
        self.assertEqual(len(elements), 2)

        # Get next element
        element = db_util.get_next_queue_element("Queue", set_status=False)
        self.assertIsNotNone(element)
        self.assertEqual(element.status, QueueStatus.NEW)

        element = db_util.get_next_queue_element("Queue")
        self.assertIsNotNone(element)
        self.assertEqual(element.status, QueueStatus.IN_PROGRESS)

        element2 = db_util.get_next_queue_element("Queue")
        self.assertIsNotNone(element2)
        self.assertNotEqual(element, element2)

        # Update element
        db_util.set_queue_element_status(element.id, QueueStatus.DONE, "Message")

        # Filter elements
        elements = db_util.get_queue_elements("Queue", reference="Ref")
        self.assertEqual(len(elements), 1)

        elements = db_util.get_queue_elements("Queue", status=QueueStatus.DONE)
        self.assertEqual(len(elements), 1)

        elements = db_util.get_queue_elements("Foo")
        self.assertEqual(len(elements), 0)

        elements = db_util.get_queue_elements("Queue", reference="Foo")
        self.assertEqual(len(elements), 0)

        # Filter by date
        logs = db_util.get_queue_elements("Queue", from_date=creation_time)
        self.assertEqual(len(logs), 2)

        logs = db_util.get_queue_elements("Queue", to_date=creation_time)
        self.assertEqual(len(logs), 0)

        tomorrow = datetime.now() + timedelta(days=1)
        logs = db_util.get_queue_elements("Queue", from_date=creation_time, to_date=tomorrow)
        self.assertEqual(len(logs), 2)

        # Delete element
        db_util.delete_queue_element(element.id)
        elements = db_util.get_queue_elements("Queue")
        self.assertEqual(len(elements), 1)

        # Queue count
        count = db_util.get_queue_count()
        self.assertEqual(count["Bulk"][QueueStatus.NEW], 10)

        # Get element from empty queue
        element = db_util.get_next_queue_element("Empty Queue")
        self.assertIsNone(element)

    def test_triggers(self):
        """Test generic trigger functionality."""
        db_test_util.reset_triggers()

        # Get triggers
        triggers = db_util.get_single_triggers()
        self.assertEqual(len(triggers), 1)

        triggers = db_util.get_scheduled_triggers()
        self.assertEqual(len(triggers), 1)

        triggers = db_util.get_queue_triggers()
        self.assertEqual(len(triggers), 1)

        triggers = db_util.get_all_triggers()
        self.assertEqual(len(triggers), 3)

        trigger = db_util.get_trigger(triggers[0].id)
        self.assertIsNotNone(trigger)
        self.assertIsNotNone(trigger.id)

        # Update trigger
        trigger.process_path = "New path"
        db_util.update_trigger(trigger)
        trigger = db_util.get_trigger(trigger.id)
        self.assertEqual(trigger.process_path, "New path")

        # Delete trigger
        db_util.delete_trigger(trigger.id)
        with self.assertRaises(ValueError):
            db_util.get_trigger(trigger.id)

    def test_single_triggers(self):
        """Test running and updating single triggers."""
        db_test_util.reset_triggers()

        # Get next single trigger
        trigger = db_util.get_pending_single_triggers()[0]
        self.assertIsNotNone(trigger)

        # Begin trigger
        has_begun = db_util.begin_single_trigger(trigger.id)
        self.assertTrue(has_begun)

        # Begin already running trigger
        has_begun = db_util.begin_single_trigger(trigger.id)
        self.assertFalse(has_begun)

        # Check is running- and next run
        trigger = db_util.get_trigger(trigger.id)
        self.assertEqual(trigger.process_status, TriggerStatus.RUNNING)
        self.assertIsNotNone(trigger.last_run)

        # No new trigger when the other is running
        none_trigger = db_util.get_pending_single_triggers()
        self.assertEqual(len(none_trigger), 0)

        # Set status
        db_util.set_trigger_status(trigger.id, TriggerStatus.DONE)
        trigger = db_util.get_trigger(trigger.id)
        self.assertEqual(trigger.process_status, TriggerStatus.DONE)

    def test_scheduled_triggers(self):
        """Test running and updating scheduled triggers."""
        db_test_util.reset_triggers()

        # Get next trigger
        trigger = db_util.get_pending_scheduled_triggers()[0]
        self.assertIsNotNone(trigger)

        # Begin trigger
        run_time = trigger.next_run
        has_begun = db_util.begin_scheduled_trigger(trigger.id)
        self.assertTrue(has_begun)

        # Begin already running trigger
        has_begun = db_util.begin_scheduled_trigger(trigger.id)
        self.assertFalse(has_begun)

        # Check is running- and next run
        trigger = db_util.get_trigger(trigger.id)
        self.assertGreater(trigger.next_run, run_time)
        self.assertEqual(trigger.process_status, TriggerStatus.RUNNING)
        self.assertIsNotNone(trigger.last_run)

        # No new trigger when other is running
        trigger_list = db_util.get_pending_scheduled_triggers()
        self.assertEqual(len(trigger_list), 0)

    def test_queue_triggers(self):
        """Test running and updating queue triggers."""
        db_test_util.reset_triggers()

        # Test with empty queue
        trigger_list = db_util.get_pending_queue_triggers()
        self.assertEqual(len(trigger_list), 0)

        # Test with 1 item in queue (triggers on 2)
        db_util.create_queue_element("Trigger Queue")
        trigger_list = db_util.get_pending_queue_triggers()
        self.assertEqual(len(trigger_list), 0)

        # Test with 2 items in queue
        db_util.create_queue_element("Trigger Queue")
        trigger = db_util.get_pending_queue_triggers()[0]
        self.assertIsNotNone(trigger)

        # Begin trigger
        has_begun = db_util.begin_queue_trigger(trigger.id)
        self.assertTrue(has_begun)

        # Begin already running trigger
        has_begun = db_util.begin_queue_trigger(trigger.id)
        self.assertFalse(has_begun)

        # Check is running
        trigger = db_util.get_trigger(trigger.id)
        self.assertEqual(trigger.process_status, TriggerStatus.RUNNING)
        self.assertIsNotNone(trigger.last_run)

        # No new trigger when other is running
        trigger_list = db_util.get_pending_queue_triggers()
        self.assertEqual(len(trigger_list), 0)

    def test_log_truncation(self):
        """Create logs with various lengths and test if their length is as expected"""
        # Create some logs
        long_message = "HelloWorld"*1000
        medium_message = "a"*8000
        short_message = "HelloWorld"

        db_util.create_log("TruncateTest", LogLevel.TRACE, long_message)
        db_util.create_log("TruncateTest", LogLevel.INFO, medium_message)
        db_util.create_log("TruncateTest", LogLevel.ERROR, short_message)

        # Test long message
        logs = db_util.get_logs(0, 100, log_level=LogLevel.TRACE)
        self.assertEqual(len(logs[0].log_message), 8000)

        # Test medium message
        logs = db_util.get_logs(0, 100, log_level=LogLevel.INFO)
        self.assertEqual(len(logs[0].log_message), len(medium_message))

        # Test short message
        logs = db_util.get_logs(0, 100, log_level=LogLevel.ERROR)
        self.assertEqual(len(logs[0].log_message), len(short_message))

    def test_schedulers(self):
        """Make pings from imitated machines and verify that they are registered."""

        db_util.send_ping_from_scheduler("Machine1")

        # Test one ping
        schedulers = db_util.get_schedulers()
        self.assertEqual(len(schedulers), 1)

        # Test multiple pings
        db_util.send_ping_from_scheduler("Machine2")
        db_util.send_ping_from_scheduler("Machine3")
        schedulers = db_util.get_schedulers()
        self.assertEqual(len(schedulers), 3)

        # Test that a ping from a machine that pinged earlier doesn't change the amount of schedulers
        db_util.send_ping_from_scheduler("Machine1")
        schedulers = db_util.get_schedulers()
        self.assertEqual(len(schedulers), 3)

        # Test types in Scheduler
        test_scheduler = schedulers[0]
        self.assertIsInstance(test_scheduler.machine_name, str)
        self.assertIsInstance(test_scheduler.last_update, datetime)

        # Test trigger
        db_util.start_trigger_from_machine("Machine1", "Test Trigger")
        schedulers = db_util.get_schedulers()
        test_scheduler = schedulers[0]
        self.assertIsInstance(test_scheduler.latest_trigger, str)
        self.assertIsInstance(test_scheduler.latest_trigger_time, datetime)


if __name__ == '__main__':
    unittest.main()
