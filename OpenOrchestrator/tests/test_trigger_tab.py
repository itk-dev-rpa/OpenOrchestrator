import unittest
from datetime import datetime
import time

from selenium.webdriver.common.by import By

from OpenOrchestrator.tests import db_test_util, ui_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import SingleTrigger


class TestTriggerTab(unittest.TestCase):
    """Test functionality of the trigger tab ui."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.browser = ui_util.open_orchestrator()

    def setUp(self) -> None:
        db_test_util.establish_clean_database()

    def test_single_trigger_creation(self):
        """Test creation of a single trigger."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_tab_single_button]").click()

        # Fill form
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_trigger_input]").send_keys("Trigger name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_name_input]").send_keys("Process name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_time_input]").send_keys("12-11-2020 12:34")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_path_input]").send_keys("Process Path")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_git_check]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_args_input]").send_keys("Process args")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_blocking_check]").click()

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=trigger_popup_save_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button]").click()

        time.sleep(1)
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


if __name__ == '__main__':
    unittest.main()
