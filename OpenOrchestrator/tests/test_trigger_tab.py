import unittest

from selenium.webdriver.common.by import By

from OpenOrchestrator.tests import db_test_util, ui_util


class TestTriggerTab(unittest.TestCase):
    """Test functionality of the trigger tab ui."""
    @classmethod
    def setUpClass(cls) -> None:
        db_test_util.establish_clean_database()
        cls.browser = ui_util.open_orchestrator()

    def test_single_trigger_creation(self):
        """Test creation of a single trigger."""
        self.browser.find_element(By.CSS_SELECTOR, "div[auto-id=trigger_tab]").click()
        self.browser.find_element(By.CSS_SELECTOR, "button[auto-id=trigger_tab_single_button]").click()


if __name__ == '__main__':
    unittest.main()
