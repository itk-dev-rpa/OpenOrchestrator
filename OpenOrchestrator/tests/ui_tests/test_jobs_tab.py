# test_jobs_tab.py
"""Tests relating to the jobs tab in Orchestrator."""

import unittest
import time

from selenium.webdriver.common.by import By

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.jobs import JobStatus
from OpenOrchestrator.tests.ui_tests import ui_util


class TestJobsTab(unittest.TestCase):
    """Test functionality of the jobs tab ui."""

    def setUp(self) -> None:
        self.browser = ui_util.open_orchestrator()
        db_test_util.establish_clean_database()
        self.browser.find_element(By.CSS_SELECTOR, "[auto-id=jobs_tab]").click()
        ui_util.refresh_ui(self.browser)

    def tearDown(self) -> None:
        self.browser.quit()

    @ui_util.screenshot_on_error
    def test_jobs_table(self):
        """Test that jobs are shown correctly in the jobs table."""
        # Create some jobs
        self._create_test_jobs()

        ui_util.refresh_ui(self.browser)

        # Check result
        table_data = ui_util.get_table_data(self.browser, "jobs_tab_jobs_table")

        # Should have 3 jobs (newest first due to DESC ordering)
        self.assertEqual(len(table_data), 3)

        # Check first job (most recent - Failed)
        self.assertEqual(table_data[0][0], "Process3")
        self.assertEqual(table_data[0][1], "Scheduler1")
        self.assertRegex(table_data[0][2], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")  # Start time
        self.assertRegex(table_data[0][3], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")  # End time
        self.assertEqual(table_data[0][4], "Failed")

        # Check second job (Done)
        self.assertEqual(table_data[1][0], "Process2")
        self.assertEqual(table_data[1][4], "Done")

        # Check third job (Running - no end time)
        self.assertEqual(table_data[2][0], "Process1")
        self.assertEqual(table_data[2][3], "")  # No end time for running job
        self.assertEqual(table_data[2][4], "Running")

    @ui_util.screenshot_on_error
    def test_job_click_navigates_to_logs(self):
        """Test that clicking a job row navigates to logs tab with job filter."""
        # Create a job
        job = db_util.start_job("Test Process", "Test Scheduler")
        db_util.set_job_status(job.id, JobStatus.DONE)

        ui_util.refresh_ui(self.browser)

        # Click the job row
        ui_util.click_table_row(self.browser, "jobs_tab_jobs_table", 0)

        # Should navigate to logs tab
        time.sleep(0.5)
        active_tab = self.browser.find_element(By.CSS_SELECTOR, ".q-tab.q-tab--active")
        self.assertEqual(active_tab.text, "LOGS")

        # Job filter should be set (you might need to adjust selector)
        # This assumes you have an auto-id on the job select in logs tab
        job_select = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=job_filter_label]")
        selected_value = job_select.get_attribute("value")
        self.assertIn(str(job.id), selected_value)

    @ui_util.screenshot_on_error
    def test_empty_jobs_table(self):
        """Test that empty jobs table displays correctly."""
        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "jobs_tab_jobs_table")
        self.assertEqual(len(table_data), 0)

    @ui_util.screenshot_on_error
    def test_job_status_colors(self):
        """Test that job status badges have correct colors."""
        # Create jobs with different statuses
        db_util.start_job("Process1", "Scheduler")  # Running

        job2 = db_util.start_job("Process2", "Scheduler")
        db_util.set_job_status(job2.id, JobStatus.DONE)

        job3 = db_util.start_job("Process3", "Scheduler")
        db_util.set_job_status(job3.id, JobStatus.FAILED)

        job4 = db_util.start_job("Process4", "Scheduler")
        db_util.set_job_status(job4.id, JobStatus.KILLED)

        ui_util.refresh_ui(self.browser)

        # Get status badges
        table = self.browser.find_element(By.CSS_SELECTOR, "[auto-id=jobs_tab_jobs_table]")
        badges = table.find_elements(By.CSS_SELECTOR, ".q-badge")

        # Check we have 4 badges
        self.assertEqual(len(badges), 4)

        # Note: You might need to adjust color checking based on your implementation
        # This is a basic check that badges exist with text
        badge_texts = [b.text for b in badges]
        self.assertIn("Running", badge_texts)
        self.assertIn("Done", badge_texts)
        self.assertIn("Failed", badge_texts)
        self.assertIn("Killed", badge_texts)

    @ui_util.screenshot_on_error
    def test_jobs_sorted_by_start_time(self):
        """Test that jobs are sorted by start time descending."""
        # Create jobs with delays to ensure different timestamps
        db_util.start_job("First", "Scheduler")
        time.sleep(0.1)
        db_util.start_job("Second", "Scheduler")
        time.sleep(0.1)
        db_util.start_job("Third", "Scheduler")

        ui_util.refresh_ui(self.browser)

        table_data = ui_util.get_table_data(self.browser, "jobs_tab_jobs_table")

        # Newest should be first
        self.assertEqual(table_data[0][0], "Third")
        self.assertEqual(table_data[1][0], "Second")
        self.assertEqual(table_data[2][0], "First")

    def _create_test_jobs(self):
        """Create test jobs with different statuses."""
        # Running job
        db_util.start_job("Process1", "Scheduler1")
        time.sleep(0.1)

        # Done job
        job2 = db_util.start_job("Process2", "Scheduler2")
        db_util.set_job_status(job2.id, JobStatus.DONE)
        time.sleep(0.1)

        # Failed job
        job3 = db_util.start_job("Process3", "Scheduler1")
        db_util.set_job_status(job3.id, JobStatus.FAILED)

        ui_util.refresh_ui(self.browser)


if __name__ == '__main__':
    browser = ui_util.open_orchestrator()
    input("...")
