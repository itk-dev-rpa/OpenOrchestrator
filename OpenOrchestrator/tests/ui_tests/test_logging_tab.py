"""Tests relating to the logs tab in Orchestrator."""

import unittest
from datetime import datetime, timedelta
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.tests.ui_tests import ui_util


class TestLogsTab(unittest.TestCase):
    """Test functionality of the logs tab ui."""
    def setUp(self) -> None:
        self.browser = ui_util.open_orchestrator()
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=logs_tab]").click()
        ui_util.refresh_ui(self.browser)

    def tearDown(self) -> None:
        self.browser.quit()

    @ui_util.screenshot_on_error
    def test_logs_table(self):
        """Test that logs are shown correctly in the logs table."""
        # Create some logs
        self._create_logs()

        ui_util.refresh_ui(self.browser)

        # Check result
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertRegex(table_data[0][0], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(table_data[0][1], "Test Error")
        self.assertEqual(table_data[0][2], LogLevel.ERROR.value)
        self.assertEqual(table_data[0][3], "Error Message")

        self.assertRegex(table_data[1][0], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(table_data[1][1], "Test Info")
        self.assertEqual(table_data[1][2], LogLevel.INFO.value)
        self.assertEqual(table_data[1][3], "Info Message")

        self.assertRegex(table_data[2][0], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(table_data[2][1], "Test Trace")
        self.assertEqual(table_data[2][2], LogLevel.TRACE.value)
        self.assertEqual(table_data[2][3], "Trace Message")

    @ui_util.screenshot_on_error
    def test_date_filter(self):
        """Test filtering on date."""
        yesterday = datetime.today() - timedelta(days=1)
        tomorrow = datetime.today() + timedelta(days=1)

        self._create_logs()
        ui_util.refresh_ui(self.browser)

        # No filter
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

        # From yesterday
        self._set_date_filter(from_date=yesterday, to_date=None)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

        # From tomorrow
        self._set_date_filter(from_date=tomorrow, to_date=None)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 0)

        # To yesterday
        self._set_date_filter(from_date=None, to_date=yesterday)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 0)

        # To tomorrow
        self._set_date_filter(from_date=None, to_date=tomorrow)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

        # From yesterday To tomorrow
        self._set_date_filter(from_date=yesterday, to_date=tomorrow)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

        # Clear filter
        self._set_date_filter(None, None)

    @ui_util.screenshot_on_error
    def test_process_filter(self):
        """Test filtering on process name."""
        self._create_logs()

        self._set_process_filter(2)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Error")

        self._set_process_filter(3)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Info")

        self._set_process_filter(4)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Trace")

        self._set_process_filter(1)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

    @ui_util.screenshot_on_error
    def test_level_filter(self):
        """Test filtering on log level."""
        self._create_logs()

        self._set_level_filter(2)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Trace")

        self._set_level_filter(3)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Info")

        self._set_level_filter(4)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(table_data[0][1], "Test Error")

        self._set_level_filter(1)
        table_data = ui_util.get_table_data(self.browser, "logs_tab_logs_table")
        self.assertEqual(len(table_data), 3)

    def _set_date_filter(self, from_date: datetime | None, to_date: datetime | None):
        # Clear filters
        from_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=logs_tab_from_input]")
        from_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        to_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=logs_tab_to_input]")
        to_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)

        if from_date:
            from_input.send_keys(from_date.strftime("%d-%m-%Y %H:%M"))

        if to_date:
            to_input.send_keys(to_date.strftime("%d-%m-%Y %H:%M"))

    def _set_process_filter(self, index: int):
        """Select a process in the process filter.

        Args:
            index: The 1-based index of the process to choose.
        """
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=logs_tab_process_input]").click()
        self.browser.find_element(By.XPATH, f"//div[@role='listbox']//div[contains(@class, 'q-item')][{index}]").click()
        time.sleep(0.5)

    def _set_level_filter(self, index: int):
        """Select a level in the level filter.

        Args:
            index: The 1-based index of the level to choose.
        """
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=logs_tab_level_input]").click()
        self.browser.find_element(By.XPATH, f"//div[@role='listbox']//div[contains(@class, 'q-item')][{index}]").click()
        time.sleep(0.5)

    def _create_logs(self):
        """Create some logs for testing."""
        db_util.create_log("Test Trace", LogLevel.TRACE, "Trace Message")
        time.sleep(0.1)
        db_util.create_log("Test Info", LogLevel.INFO, "Info Message")
        time.sleep(0.1)
        db_util.create_log("Test Error", LogLevel.ERROR, "Error Message")

        ui_util.refresh_ui(self.browser)


if __name__ == '__main__':
    unittest.main()
