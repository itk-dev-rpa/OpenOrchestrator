
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
    port = get_free_port()
    subprocess.Popen(["python", "-m", "OpenOrchestrator", "-o", "--port", str(port), "--dont_show"])

    browser = webdriver.Chrome()
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

    conn_string = os.environ['CONN_STRING']
    conn_input = browser.find_element(By.CSS_SELECTOR, "input[auto-id=connection_frame_conn_input]")
    conn_input.send_keys(Keys.CONTROL, "a", Keys.DELETE)
    conn_input.send_keys(conn_string[0])
    conn_input.send_keys(conn_string[1:])

    browser.find_element(By.CSS_SELECTOR, "button[auto-id=settings_tab_key_button]").click()
    browser.find_element(By.CSS_SELECTOR, "button[auto-id=connection_frame_conn_button]").click()

    return browser


if __name__ == '__main__':
    b = open_orchestrator()
    input("Continue...")
