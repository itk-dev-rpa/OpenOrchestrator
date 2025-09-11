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
    def test_queue_popup_status_filter(self):
        """Test status filtering in queue popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Test each status individually
        for i, status in enumerate(QueueStatus):
            self._set_status_filter(status.value)
            table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
            expected_count = i + 1
            self.assertEqual(len(table_data), expected_count)

        # Test clearing status filter
        self._set_status_filter(None)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 15)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_queue_popup_search_filter(self):
        """Test search filtering in queue popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Test partial reference search
        self._set_search_filter("Reference 0")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        expected_count = len(QueueStatus)  # One "Reference 0,x" per status
        self.assertEqual(len(table_data), expected_count)
        self.assertIn("Reference 0", table_data[0][0])

        # Test exact reference search
        self._set_search_filter("Reference 0,1")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 1)
        self.assertEqual("Reference 0,1", table_data[0][0])

        # Test data search
        self._set_search_filter("Data 0,1")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 1)
        self.assertEqual("Data 0,1", table_data[0][2])

        # Test partial data search
        self._set_search_filter("ata 0")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 5)

        # Test message search
        self._set_search_filter("Message 0,1")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 1)
        self.assertEqual("Message 0,1", table_data[0][3])

        # Test no matches
        self._set_search_filter("NonExistentRef")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 0)

        # Test empty search (should show all)
        self._set_search_filter("")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 15)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_queue_popup_combined_filters(self):
        """Test combining multiple filters."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        yesterday = datetime.today() - timedelta(days=1)
        tomorrow = datetime.today() + timedelta(days=1)

        # Date + Status filter
        self._set_date_filter(from_date=yesterday, to_date=tomorrow)
        self._set_status_filter("New")  # Assuming this is first status
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 1)

        # Date + Search filter
        self._set_status_filter(None)  # Clear status
        self._set_search_filter("Reference 0")
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        expected_count = len(QueueStatus)
        self.assertIn("Reference 0", table_data[0][0])
        self.assertEqual(len(table_data), expected_count)

        # All three filters
        self._set_status_filter("In Progress")  # Assuming second status
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), 1)

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

    @ui_util.screenshot_on_error
    def test_queue_element_popup(self):
        """Test content of queue element popup.
        """
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)

        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        ui_util.click_table_row(self.browser, "queue_popup_table", 0)
        for i, field in enumerate(['reference', 'status', 'data_field', 'message', 'created_date', 'start_date', 'end_date', 'created_by', 'id_text']):
            field_content = self.browser.find_element(By.CSS_SELECTOR, f"[auto-id=queue_element_popup_{field}]").get_attribute('value')
            if field in ['status', 'id_text', 'created_by']:
                field_content = self.browser.find_element(By.CSS_SELECTOR, f"[auto-id=queue_element_popup_{field}]").text
            if not field_content:
                field_content = "N/A"
            self.assertEqual(table_data[0][i], field_content)

    @ui_util.screenshot_on_error
    def test_create_new_queue_element(self):
        """Test creating a new queue element through the popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Click "New" button to create a new queue element
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_new_button]").click()

        # Fill in the form and save
        reference_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_reference]")
        reference_input.send_keys("New Reference")

        status_select = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_status]")
        status_select.click()
        status_select.find_element(By.XPATH, "//div[contains(@class,'q-item')]//span[text()='In Progress']").click()

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_save_button]").click()

        # Verify the new element appears in the queue popup table
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertTrue(any("New Reference" in row[0] for row in table_data))

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_edit_queue_element(self):
        """Test editing an existing queue element through the popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Open the first queue element in the popup
        ui_util.click_table_row(self.browser, "queue_popup_table", 0)

        # Edit the reference field
        reference_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_reference]")
        reference_input.clear()
        reference_input.send_keys("Edited Reference")

        # Change the status
        status_select = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_status]")
        status_select.click()
        status_select.find_element(By.XPATH, "//div[contains(@class,'q-item')]//span[text()='Done']").click()

        # Edit the date field
        reference_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_start_date]")
        reference_input.clear()
        reference_input.send_keys("01-01-2000 12:34:56")

        # Save the changes
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_save_button]").click()

        # Verify the changes in the queue popup table
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertTrue(any("Edited Reference" in row[0] for row in table_data))
        self.assertTrue(any("Done" in row[1] for row in table_data))
        self.assertTrue(any("01-01-2000 12:34:56" in row[5] for row in table_data))

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_delete_queue_element(self):
        """Test deleting a queue element through the popup."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Get the initial count of queue elements
        initial_count = len(ui_util.get_table_data(self.browser, "queue_popup_table"))

        # Open the first queue element in the popup
        ui_util.click_table_row(self.browser, "queue_popup_table", 0)

        # Click the delete button and confirm
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_delete_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button").click()

        # Verify the element was deleted
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertEqual(len(table_data), initial_count - 1)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_close_button]").click()

    @ui_util.screenshot_on_error
    def test_queue_element_validation(self):
        """Test validation of queue element fields."""
        self._create_queue_elements()
        ui_util.refresh_ui(self.browser)
        ui_util.click_table_row(self.browser, "queues_tab_queue_table", 0)

        # Click "New" button to create a new queue element
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_new_button]").click()

        reference_input = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_reference]")
        reference_input.send_keys("Valid Reference")

        status_select = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_status]")
        status_select.click()
        status_select.find_element(By.XPATH, "//div[contains(@class,'q-item')]//span[text()='In Progress']").click()

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_element_popup_save_button]").click()

        # Verify the element was created
        table_data = ui_util.get_table_data(self.browser, "queue_popup_table")
        self.assertTrue(any("Valid Reference" in row[0] for row in table_data))

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
            from_input.send_keys(from_date.strftime("%d-%m-%Y %H:%M:%S"))

        if to_date:
            to_input.send_keys(to_date.strftime("%d-%m-%Y %H:%M:%S"))

    def _set_status_filter(self, status=None):
        """Set status filter in queue popup."""
        if status is None:
            status = "All"
        status_select = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_status_select]")
        status_select.click()
        option = status_select.find_element(By.XPATH, f"//div[contains(@class,'q-item')]//span[text()='{status}']")
        option.click()

    def _set_search_filter(self, search_term=""):
        """Set reference search filter in queue popup."""
        search_field = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=queue_popup_search_input]")
        search_field.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        if search_term:
            search_field.send_keys(search_term)


if __name__ == '__main__':
    unittest.main()
