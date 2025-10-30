# test_jobs.py
"""Tests for the Job ORM and related database functions."""

import unittest
from datetime import datetime
import time

from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.jobs import JobStatus


class TestJobORM(unittest.TestCase):
    """Test the Job ORM class and database operations."""

    def setUp(self):
        db_test_util.establish_clean_database()

    def test_create_job(self):
        """Test creating a job in the database."""
        job = db_util.start_job("Test Process", "Test Scheduler")

        self.assertIsNotNone(job)
        self.assertIsNotNone(job.id)
        self.assertEqual(job.process_name, "Test Process")
        self.assertEqual(job.scheduler_name, "Test Scheduler")
        self.assertEqual(job.status, JobStatus.RUNNING)
        self.assertIsNotNone(job.start_time)
        self.assertIsNone(job.end_time)

    def test_job_default_values(self):
        """Test that default values are set correctly."""
        job = db_util.start_job("Process", "Scheduler")

        # Status should default to RUNNING
        self.assertEqual(job.status, JobStatus.RUNNING)

        # start_time should be set automatically
        self.assertIsInstance(job.start_time, datetime)
        time_diff = abs((datetime.now() - job.start_time).total_seconds())
        self.assertLess(time_diff, 1)  # Should be within 1 second

        # end_time should be None initially
        self.assertIsNone(job.end_time)

    def test_update_job_status(self):
        """Test updating job status through lifecycle."""
        job = db_util.start_job("Process", "Scheduler")
        original_id = job.id

        # Update to DONE - should set end_time automatically
        db_util.set_job_status(original_id, JobStatus.DONE)
        updated_job = db_util.get_job(original_id)
        self.assertEqual(updated_job.status, JobStatus.DONE)
        self.assertIsNotNone(updated_job.end_time)

        # Create new job and update to FAILED
        job2 = db_util.start_job("Process2", "Scheduler")
        db_util.set_job_status(job2.id, JobStatus.FAILED)
        updated_job2 = db_util.get_job(job2.id)
        self.assertEqual(updated_job2.status, JobStatus.FAILED)
        self.assertIsNotNone(updated_job2.end_time)

        # Create new job and update to KILLED
        job3 = db_util.start_job("Process3", "Scheduler")
        db_util.set_job_status(job3.id, JobStatus.KILLED)
        updated_job3 = db_util.get_job(job3.id)
        self.assertEqual(updated_job3.status, JobStatus.KILLED)
        self.assertIsNotNone(updated_job3.end_time)

    def test_end_time_set_on_completion(self):
        """Test that end_time is set when job status changes from RUNNING."""
        job = db_util.start_job("Process", "Scheduler")
        self.assertIsNone(job.end_time)

        # Complete the job
        time.sleep(0.1)
        db_util.set_job_status(job.id, JobStatus.DONE)

        updated_job = db_util.get_job(job.id)
        self.assertIsNotNone(updated_job.end_time)
        self.assertGreater(updated_job.end_time, updated_job.start_time)

    def test_get_jobs(self):
        """Test retrieving multiple jobs."""
        # Create multiple jobs
        job1 = db_util.start_job("Process1", "Scheduler1")
        time.sleep(0.01)
        job2 = db_util.start_job("Process2", "Scheduler2")
        time.sleep(0.01)
        job3 = db_util.start_job("Process3", "Scheduler1")

        # Get all jobs
        jobs = db_util.get_jobs()
        self.assertEqual(len(jobs), 3)

        # Jobs should be ordered by start_time DESC (newest first)
        self.assertEqual(jobs[0].id, job3.id)
        self.assertEqual(jobs[1].id, job2.id)
        self.assertEqual(jobs[2].id, job1.id)

    def test_get_jobs_by_status(self):
        """Test filtering jobs by status."""
        job1 = db_util.start_job("Process1", "Scheduler")
        job2 = db_util.start_job("Process2", "Scheduler")
        job3 = db_util.start_job("Process3", "Scheduler")

        db_util.set_job_status(str(job1.id), JobStatus.DONE)
        db_util.set_job_status(str(job2.id), JobStatus.FAILED)
        # job3 remains RUNNING

        running_jobs = db_util.get_jobs(status=JobStatus.RUNNING)
        self.assertEqual(len(running_jobs), 1)
        self.assertEqual(running_jobs[0].id, job3.id)

        done_jobs = db_util.get_jobs(status=JobStatus.DONE)
        self.assertEqual(len(done_jobs), 1)
        self.assertEqual(done_jobs[0].id, job1.id)

        failed_jobs = db_util.get_jobs(status=JobStatus.FAILED)
        self.assertEqual(len(failed_jobs), 1)
        self.assertEqual(failed_jobs[0].id, job2.id)

    def test_to_row_dict(self):
        """Test the to_row_dict method."""
        job = db_util.start_job("Test Process", "Test Scheduler")

        row_dict = job.to_row_dict()

        self.assertEqual(row_dict["ID"], str(job.id))
        self.assertEqual(row_dict["Process Name"], "Test Process")
        self.assertEqual(row_dict["Scheduler"], "Test Scheduler")
        self.assertRegex(row_dict["Start Time"], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(row_dict["End Time"], "N/A")
        self.assertEqual(row_dict["Status"], "Running")

        # Test with completed job
        db_util.set_job_status(str(job.id), JobStatus.DONE)

        updated_job = db_util.get_job(job.id)
        row_dict = updated_job.to_row_dict()

        self.assertRegex(row_dict["End Time"], r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")
        self.assertEqual(row_dict["Status"], "Done")


if __name__ == '__main__':
    unittest.main()
