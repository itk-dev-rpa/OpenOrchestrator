"""Tests relating to the constants tab in Orchestrator."""

import unittest
import time

from selenium.webdriver.common.by import By

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.tests.ui_tests import ui_util


class TestConstantsTab(unittest.TestCase):
    """Test functionality of the constants tab ui."""
    def setUp(self) -> None:
        self.browser = ui_util.open_orchestrator()
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constants_tab]").click()
        ui_util.refresh_ui(self.browser)

    def tearDown(self) -> None:
        self.browser.quit()

    @ui_util.screenshot_on_error
    def test_constants_table(self):
        """Test that constants are shown correctly in the constants table."""
        db_util.create_constant("Constant 1", "Value 1")
        db_util.create_constant("Constant 2", "Value 2")
        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "constants_tab_constants_table")

        self.assertEqual(table_data[0][0], "Constant 1")
        self.assertEqual(table_data[0][1], "Value 1")
        self.assertRegex(table_data[0][2], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")

        self.assertEqual(table_data[1][0], "Constant 2")
        self.assertEqual(table_data[1][1], "Value 2")
        self.assertRegex(table_data[1][2], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")

    @ui_util.screenshot_on_error
    def test_credentials_table(self):
        """Test that credentials are shown correctly in the credentials table."""
        db_util.create_credential("Credential 1", "Username 1", "abc")
        db_util.create_credential("Credential 2", "Username 2", "abcdefghijklmnopq")
        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "constants_tab_credentials_table")

        self.assertEqual(table_data[0][0], "Credential 1")
        self.assertEqual(table_data[0][1], "Username 1")
        self.assertEqual(table_data[0][2], "100 encrypted bytes. 0-15 decrypted bytes.")
        self.assertRegex(table_data[0][3], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")

        self.assertEqual(table_data[1][0], "Credential 2")
        self.assertEqual(table_data[1][1], "Username 2")
        self.assertEqual(table_data[1][2], "120 encrypted bytes. 16-31 decrypted bytes.")
        self.assertRegex(table_data[1][3], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")

    @ui_util.screenshot_on_error
    def test_create_constant(self):
        """Test creating a constant."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constants_tab_constant_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_name_input]").send_keys("Constant Name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_value_input]").send_keys("Constant Value")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_save_button]").click()
        time.sleep(1)

        constant = db_util.get_constant("Constant Name")
        self.assertEqual(constant.name, "Constant Name")
        self.assertEqual(constant.value, "Constant Value")

    @ui_util.screenshot_on_error
    def test_create_credential(self):
        """Test creating a credential."""
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constants_tab_credential_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_name_input]").send_keys("Credential Name")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_username_input]").send_keys("Credential Username")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_password_input]").send_keys("Credential Password")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_save_button]").click()
        time.sleep(1)

        # Make sure the encryption key matches the one in the ui
        crypto_util.set_key(ui_util.ENCRYPTION_KEY)

        credential = db_util.get_credential("Credential Name")
        self.assertEqual(credential.name, "Credential Name")
        self.assertEqual(credential.username, "Credential Username")
        self.assertEqual(credential.password, "Credential Password")

    @ui_util.screenshot_on_error
    def test_edit_constant(self):
        """Test editing an existing constant."""
        # Create a constant
        db_util.create_constant("Constant Name", "Value")
        ui_util.refresh_ui(self.browser)

        # Click constant in table
        ui_util.click_table_row(self.browser, "constants_tab_constants_table", 0)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_value_input]").send_keys(" New")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_save_button]").click()
        time.sleep(1)

        constant = db_util.get_constant("Constant Name")
        self.assertEqual(constant.value, "Value New")

    @ui_util.screenshot_on_error
    def test_edit_credential(self):
        """Test editing an existing credential."""
        # Create a credential
        db_util.create_credential("Credential Name", "Username", "Password")
        ui_util.refresh_ui(self.browser)

        # Click credential in table
        ui_util.click_table_row(self.browser, "constants_tab_credentials_table", 0)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_username_input]").send_keys(" New")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_password_input]").send_keys("Password New")
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_save_button]").click()
        time.sleep(1)

        # Make sure the encryption key matches the one in the ui
        crypto_util.set_key(ui_util.ENCRYPTION_KEY)

        credential = db_util.get_credential("Credential Name")
        self.assertEqual(credential.username, "Username New")
        self.assertEqual(credential.password, "Password New")

    @ui_util.screenshot_on_error
    def test_delete_constant(self):
        """Test deleting a constant."""
        # Create a constant
        db_util.create_constant("Constant Name", "Value")
        ui_util.refresh_ui(self.browser)

        # Click constant in table
        ui_util.click_table_row(self.browser, "constants_tab_constants_table", 0)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=constant_popup_delete_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button]").click()
        time.sleep(1)

        with self.assertRaises(ValueError):
            db_util.get_constant("Constant Name")

    @ui_util.screenshot_on_error
    def test_delete_credential(self):
        """Test deleting a credential."""
        # Create a credential
        db_util.create_credential("Credential Name", "Username", "Password")
        ui_util.refresh_ui(self.browser)

        # Click credential in table
        ui_util.click_table_row(self.browser, "constants_tab_credentials_table", 0)

        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=credential_popup_delete_button]").click()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=popup_option1_button]").click()
        time.sleep(1)

        with self.assertRaises(ValueError):
            db_util.get_credential("Credential Name")


if __name__ == '__main__':
    unittest.main()
