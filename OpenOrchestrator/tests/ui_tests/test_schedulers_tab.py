"""Tests relating to the schedulers tab in Orchestrator."""

import unittest

from selenium.webdriver.common.by import By

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.tests.ui_tests import ui_util


class TestSchedulersTab(unittest.TestCase):
    """Test functionality of the schedulers tab ui."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.browser = ui_util.open_orchestrator()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.quit()

    def setUp(self) -> None:
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=schedulers_tab]").click()
        ui_util.refresh_ui(self.browser)

    @ui_util.screenshot_on_error
    def test_schedulers_table(self):
        """Test that schedulers are shown correctly in the schedulers table."""
        db_util.send_ping_from_scheduler("Testmachine")
        db_util.start_trigger_from_machine("Testmachine2", "RPA Process")
        ui_util.refresh_ui(self.browser)

        # Check that the text content is displayed correctly
        table_data = ui_util.get_table_data(self.browser, "schedulers_tab_schedulers_table")
        self.assertEqual(table_data[0][0], "Testmachine")
        self.assertRegex(table_data[0][1], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(table_data[0][2], "None yet")

        self.assertEqual(table_data[1][0], "Testmachine2")
        self.assertRegex(table_data[1][1], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(table_data[1][2], "RPA Process")
        self.assertRegex(table_data[1][3], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")


if __name__ == '__main__':
    unittest.main()
