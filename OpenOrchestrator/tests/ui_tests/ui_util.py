
import subprocess
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from OpenOrchestrator.orchestrator.application import get_free_port


def open_orchestrator() -> webdriver.Chrome:
    """Open Orchestrator in a Selenium Chrome browser.

    Raises:
        RuntimeError: If the Orchestrator app didn't start.

    Returns:
        The Chrome browser logged in to Orchestrator.
    """
    conn_string = os.environ['CONN_STRING']

    port = get_free_port()
    subprocess.Popen(["python", "-m", "OpenOrchestrator", "-o", "--port", str(port), "--dont_show"])

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

    return browser


def refresh_ui(browser: webdriver.Chrome):
    """Press the refresh button."""
    browser.find_element(By.CSS_SELECTOR, "[auto-id=refresh_button").click()
    time.sleep(0.5)


def send_slow_keys(element, string: str):
    """Send keys to an element one at a time."""
    for c in string:
        element.send_keys(c)


if __name__ == '__main__':
    b = open_orchestrator()
    input("Continue...")
