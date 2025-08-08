"""Tests relating to the queues tab in Orchestrator."""

import unittest
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.tests.ui_tests import ui_util


class TestQueuesTab(unittest.TestCase):
    """Test functionality of the queues tab ui."""
    def setUp(self) -> None:
        self.browser = ui_util.open_orchestrator()
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queues_tab]").click()
        ui_util.refresh_ui(self.browser)

    def tearDown(self) -> None:
        self.browser.quit()

    @ui_util.screenshot_on_error
    def test_queues_table(self):
        """Test that queues are displayed correctly in the queues table."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "queues_tab_queue_table")
        self.assertEqual(table_data[0], ["Queue Name 1", "1", "2", "3", "4", "5"])
        self.assertEqual(table_data[1], ["Queue Name 2", "1", "2", "3", "4", "5"])

    @ui_util.screenshot_on_error
    def test_queue_popup(self):
        """Test that queue elements are displayed correctly in the queue popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)

        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")

        queue_elements = db_util.get_queue_elements("Queue Name 1")

        self.assertEqual(len(table_data), len(queue_elements))
        for i, queue_element in enumerate(queue_elements):
            self.assertIn(table_data[i][0], queue_element.reference)
            self.assertEqual(table_data[i][1], queue_element.status.value)
            self.assertEqual(table_data[i][2], queue_element.data)
            self.assertEqual(table_data[i][3], queue_element.message)
            self.assertRegex(table_data[i][4], r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})|(N/A)")
            self.assertRegex(table_data[i][5], r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})|(N/A)")
            self.assertRegex(table_data[i][6], r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})|(N/A)")
            self.assertEqual(table_data[i][7], queue_element.created_by)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_queue_popup_filters(self):
        """Test setting filters in the queue popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)

        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        yesterday = datetime.today() - timedelta(days=1)
        tomorrow = datetime.today() + timedelta(days=1)

        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 15)

        # From yesterday
        self._set_date_filter(from_date=yesterday, to_date=None)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 15)

        # From tomorrow
        self._set_date_filter(from_date=tomorrow, to_date=None)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 0)

        # To yesterday
        self._set_date_filter(from_date=None, to_date=yesterday)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 0)

        # From yesterday to tomorrow
        self._set_date_filter(from_date=yesterday, to_date=tomorrow)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 15)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    def _create_queue_elements(self):
        """Create some queue elements.
        Creates 1x'New', 2x'In Progress' and so on.
        """
        for j in range(2):
            for i, status in enumerate(QueueStatus):
                for k in range(i+1):
                    qe = db_util.create_queue_element(f"Queue Name {j+1}", reference=f"Reference {k},{i}", data=f"Data {k},{i}", created_by=f"Creator {k},{i}")
                    db_util.set_queue_element_status(qe.id, status, message=f"Message {k},{i}")

    # This code is similar to some in test_logging_tab.
    # Since the ui might change it doesn't make sense to make a common function for this.
    # pylint: disable=duplicate-code
    def _set_date_filter(self, from_date: datetime | None, to_date: datetime | None):
        """Set the date filters."""
        # Clear filters
        from_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_from_input]")
        from_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        to_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_to_input]")
        to_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)

        if from_date:
            from_input.send_keys(from_date.strftime("%d-%m-%Y %H:%M"))

        if to_date:
            to_input.send_keys(to_date.strftime("%d-%m-%Y %H:%M"))


if __name__ == '__main__':
    unittest.main()
