"""This module contains functions to help with ui tests."""

import subprocess
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from OpenOrchestrator.orchestrator.application import get_free_port


ENCRYPTION_KEY = None


def open_orchestrator() -> webdriver.Chrome:
    """Open Orchestrator in a Selenium Chrome browser.

    Raises:
        RuntimeError: If the Orchestrator app didn't start.

    Returns:
        The Chrome browser logged in to Orchestrator.
    """
    conn_string = os.environ['CONN_STRING']

    port = get_free_port()
    subprocess.Popen(["python", "-m", "OpenOrchestrator", "-o", "--port", str(port), "--dont_show"])  # pylint: disable=consider-using-with

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(2)
    browser.maximize_window()
    for _ in range(5):
        try:
            browser.get(f"http://localhost:{port}")
            break
        except WebDriverException:
            pass
    else:
        raise RuntimeError("Couldn't connect to app after 5 tries.")

    # Wait for the ui to load
    time.sleep(1)

    conn_input = browser.find_element(By.CSS_SELECTOR, "input[auto-id=connection_frame_conn_input]")
    conn_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)
    send_slow_keys(conn_input, conn_string)

    browser.find_element(By.CSS_SELECTOR, "button[auto-id=settings_tab_key_button]").click()
    browser.find_element(By.CSS_SELECTOR, "button[auto-id=connection_frame_conn_button]").click()

    global ENCRYPTION_KEY  # pylint: disable=global-statement
    ENCRYPTION_KEY = browser.find_element(By.CSS_SELECTOR, "input[auto-id=connection_frame_key_input]").get_attribute("value")

    time.sleep(1)

    return browser


def refresh_ui(browser: webdriver.Chrome):
    """Press the refresh button."""
    browser.find_element(By.CSS_SELECTOR, "[auto-id=refresh_button").click()
    time.sleep(0.5)


def send_slow_keys(element, string: str):
    """Send keys to an element one at a time."""
    for c in string:
        element.send_keys(c)


def get_table_data(browser: webdriver.Chrome, auto_id: str) -> list[list[str]]:
    """Get the data from a table.

    Args:
        browser: The browser object to perform the action.
        auto_id: The automation id of the table.

    Returns:
        A 2D list of strings of all the data in the table.
    """
    table = browser.find_element(By.CSS_SELECTOR, f"[auto-id={auto_id}]")
    rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        fields = row.find_elements(By.TAG_NAME, "td")
        data.append([f.text for f in fields])

    return data


def click_table_row(browser: webdriver.Chrome, auto_id: str, index: int):
    """Click a row in a table.

    Args:
        browser: The browser to perform the action.
        auto_id: The automation id of the table.
        index: The 0-based index of the row to click.
    """
    table = browser.find_element(By.CSS_SELECTOR, f"[auto-id={auto_id}]")
    rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
    rows[index].click()
    time.sleep(0.5)


if __name__ == '__main__':
    b = open_orchestrator()
    input("Continue...")
