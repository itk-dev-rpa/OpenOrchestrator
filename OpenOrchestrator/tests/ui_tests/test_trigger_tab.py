"""Tests relating to the trigger tab in Orchestrator."""

import unittest
from datetime import datetime, timedelta
import time

from selenium.webdriver.common.by import By

from OpenOrchestrator.common import datetime_util
from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger, ScheduledTrigger, QueueTrigger, TriggerStatus
from OpenOrchestrator.tests.ui_tests import ui_util


class TestTriggerTab(unittest.TestCase):
    """Test functionality of the trigger tab ui."""
    def setUp(self) -> None:
        self.browser = ui_util.open_orchestrator()
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab]").click()
        ui_util.refresh_ui(self.browser)

    def tearDown(self) -> None:
        self.browser.quit()

    @ui_util.screenshot_on_error
    def test_single_trigger_creation(self):
        """Test creation of a single trigger."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab_single_button]").click()

        # Fill form
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_trigger_input]").send_keys("Trigger name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_name_input]").send_keys("Process name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_time_input]").send_keys("12-11-2020 12:34")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_path_input]").send_keys("Process Path")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_git_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_args_input]").send_keys("Process args")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_priority_input]").send_keys("5")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_whitelist_input]").send_keys("Scheduler1\nScheduler2\n")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_save_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button]").click()

        # Check result
        time.sleep(5)
        triggers = db_util.get_all_triggers()
        self.assertEqual(len(triggers), 1)
        trigger: SingleTrigger = triggers[0]
        self.assertIsInstance(trigger, SingleTrigger)

        self.assertEqual(trigger.trigger_name, "Trigger name")
        self.assertEqual(trigger.process_name, "Process name")
        self.assertEqual(trigger.next_run, datetime.strptime("12-11-2020 12:34", "%d-%m-%Y %H:%M"))
        self.assertEqual(trigger.process_path, "Process Path")
        self.assertEqual(trigger.is_git_repo, True)
        self.assertEqual(trigger.process_args, "Process args")
        self.assertEqual(trigger.is_blocking, True)
        self.assertEqual(trigger.priority, 5)
        self.assertEqual(trigger.scheduler_whitelist, '["Scheduler1", "Scheduler2"]')

    @ui_util.screenshot_on_error
    def test_scheduled_trigger_creation(self):
        """Test creation of a scheduled trigger."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab_scheduled_button]").click()

        # Fill form
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_trigger_input]").send_keys("Trigger name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_name_input]").send_keys("Process name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_cron_input]").send_keys("1 1 * * *")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_path_input]").send_keys("Process Path")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_git_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_args_input]").send_keys("Process args")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_blocking_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_priority_input]").send_keys("5")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_whitelist_input]").send_keys("Scheduler1\nScheduler2\n")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_save_button]").click()

        # Check result
        time.sleep(2)
        triggers = db_util.get_all_triggers()
        self.assertEqual(len(triggers), 1)
        trigger: ScheduledTrigger = triggers[0]
        self.assertIsInstance(trigger, ScheduledTrigger)

        self.assertEqual(trigger.trigger_name, "Trigger name")
        self.assertEqual(trigger.process_name, "Process name")
        self.assertEqual(trigger.cron_expr, "1 1 * * *")
        self.assertEqual(trigger.process_path, "Process Path")
        self.assertEqual(trigger.is_git_repo, True)
        self.assertEqual(trigger.process_args, "Process args")
        self.assertEqual(trigger.is_blocking, False)
        self.assertEqual(trigger.priority, 5)
        self.assertEqual(trigger.scheduler_whitelist, '["Scheduler1", "Scheduler2"]')

    @ui_util.screenshot_on_error
    def test_queue_trigger_creation(self):
        """Test creation of a queue trigger."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab_queue_button]").click()

        # Fill form
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_trigger_input]").send_keys("Trigger name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_name_input]").send_keys("Process name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_queue_input]").send_keys("Queue Name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_batch_input]").send_keys("1")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_path_input]").send_keys("Process Path")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_git_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_args_input]").send_keys("Process args")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_blocking_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_priority_input]").send_keys("5")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_whitelist_input]").send_keys("Scheduler1\nScheduler2\n")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_save_button]").click()

        # Check result
        time.sleep(1)
        triggers = db_util.get_all_triggers()
        self.assertEqual(len(triggers), 1)
        trigger: QueueTrigger = triggers[0]
        self.assertIsInstance(trigger, QueueTrigger)

        self.assertEqual(trigger.trigger_name, "Trigger name")
        self.assertEqual(trigger.process_name, "Process name")
        self.assertEqual(trigger.queue_name, "Queue Name")
        self.assertEqual(trigger.min_batch_size, 11)
        self.assertEqual(trigger.process_path, "Process Path")
        self.assertEqual(trigger.is_git_repo, True)
        self.assertEqual(trigger.process_args, "Process args")
        self.assertEqual(trigger.is_blocking, False)
        self.assertEqual(trigger.priority, 5)
        self.assertEqual(trigger.scheduler_whitelist, '["Scheduler1", "Scheduler2"]')

    @ui_util.screenshot_on_error
    def test_trigger_table(self):
        """Test that data is shown correctly in the trigger table."""
        # Create some triggers
        yesterday = datetime.today() - timedelta(days=1)
        tomorrow = datetime.today() + timedelta(days=1)
        db_util.create_single_trigger("A Single trigger", "Single Process", yesterday, "Single path", "Single args", False, False, 0, [])
        db_util.create_scheduled_trigger("B Scheduled trigger", "Scheduled Process", "1 2 3 4 5", tomorrow, "Scheduled path", "Scheduled args", False, False, 0, [])
        db_util.create_queue_trigger("C Queue trigger", "Queue Process", "Queue Name", "Queue path", "Queue args", False, False, 25, 0, [])

        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "trigger_tab_trigger_table")

        # Check single trigger
        self.assertEqual(table_data[0][0], "A Single trigger")
        self.assertEqual(table_data[0][1], "0")
        self.assertEqual(table_data[0][2], "Single")
        self.assertEqual(table_data[0][3], "Idle")
        self.assertEqual(table_data[0][4], "Single Process")
        self.assertEqual(table_data[0][5], "Never")
        self.assertEqual(table_data[0][6], f"{datetime_util.format_datetime(yesterday)}\nOverdue")

        # Check scheduled trigger
        self.assertEqual(table_data[1][0], "B Scheduled trigger")
        self.assertEqual(table_data[1][1], "0")
        self.assertEqual(table_data[1][2], "Scheduled")
        self.assertEqual(table_data[1][3], "Idle")
        self.assertEqual(table_data[1][4], "Scheduled Process")
        self.assertEqual(table_data[1][5], "Never")
        self.assertEqual(table_data[1][6], f"{datetime_util.format_datetime(tomorrow)}")

        # Check queue trigger
        self.assertEqual(table_data[2][0], "C Queue trigger")
        self.assertEqual(table_data[2][1], "0")
        self.assertEqual(table_data[2][2], "Queue")
        self.assertEqual(table_data[2][3], "Idle")
        self.assertEqual(table_data[2][4], "Queue Process")
        self.assertEqual(table_data[2][5], "Never")
        self.assertEqual(table_data[2][6], "N/A")

    @ui_util.screenshot_on_error
    def test_delete_trigger(self):
        """Test deleting a trigger."""
        # Create a trigger
        db_util.create_queue_trigger("Queue trigger", "Queue Process", "Queue Name", "Queue path", "Queue args", False, False, 25, 0, [])
        ui_util.refresh_ui(self.browser)

        # Click trigger
        ui_util.click_table_row(self.browser, "trigger_tab_trigger_table", 0)

        # Delete trigger
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_delete_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button]").click()

        # Check result
        time.sleep(1)
        triggers = db_util.get_all_triggers()
        self.assertEqual(len(triggers), 0)

    @ui_util.screenshot_on_error
    def test_enable_disable(self):
        """Test disabling and enabling a trigger."""
        # Create a trigger
        db_util.create_queue_trigger("Queue trigger", "Queue Process", "Queue Name", "Queue path", "Queue args", False, False, 25, 0, [])
        ui_util.refresh_ui(self.browser)

        # Click trigger
        ui_util.click_table_row(self.browser, "trigger_tab_trigger_table", 0)

        # Disable trigger
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_disable_button]").click()
        time.sleep(1)

        trigger = db_util.get_all_triggers()[0]
        self.assertEqual(trigger.process_status, TriggerStatus.PAUSED)

        # Enable trigger
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_enable_button]").click()
        time.sleep(1)

        trigger = db_util.get_all_triggers()[0]
        self.assertEqual(trigger.process_status, TriggerStatus.IDLE)

        # Close trigger
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_cancel_button]").click()

    @ui_util.screenshot_on_error
    def test_edit_trigger(self):
        """Test editing a trigger."""
        # Create a trigger
        db_util.create_queue_trigger("Queue trigger", "Queue Process", "Queue Name", "Queue path", "Queue args", False, False, 25, 0, [])
        ui_util.refresh_ui(self.browser)

        # Click trigger
        ui_util.click_table_row(self.browser, "trigger_tab_trigger_table", 0)

        # Edit trigger
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_trigger_input]").send_keys(" Edit")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_save_button]").click()
        time.sleep(1)

        # Check result
        trigger = db_util.get_all_triggers()[0]
        self.assertEqual(trigger.trigger_name, "Queue trigger Edit")


if __name__ == '__main__':
    # unittest.main(failfast=True)
    t = TestTriggerTab()
    t.setUp()
    t.test_single_trigger_creation()
    t.tearDown()
