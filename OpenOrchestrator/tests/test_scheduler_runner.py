"""This module tests the OpenOrchestrator.scheduler.runner module."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import subprocess

from OpenOrchestrator.scheduler import runner
from OpenOrchestrator.database import db_util
from OpenOrchestrator.tests import db_test_util
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database.triggers import TriggerStatus


TEST_MODULE = "OpenOrchestrator.scheduler.runner"


class TestSchedulerRunner(unittest.TestCase):
    """Test the runner functionality of the scheduler."""
    def setUp(self) -> None:
        db_test_util.establish_clean_database()

    @patch(f"{TEST_MODULE}.shutil.which", return_value="git")
    @patch(f"{TEST_MODULE}.os.makedirs")
    @patch(f"{TEST_MODULE}.subprocess.run")
    @patch(f"{TEST_MODULE}.get_repo_folder_path", return_value="repo_folder")
    def test_clone_git_repo(self, mock_get_repo_folder_path: MagicMock, mock_run: MagicMock, mock_makedirs: MagicMock, mock_which: MagicMock):
        """Test the clone_git_repo function of the runner module.

        Args:
            mock_get_repo_folder_path: A MagicMock of the runner.get_repo_folder_path.
            mock_run: A MagicMock of the subprocess.run function.
            mock_makedirs: A MagicMock of the os.makedirs function.
            mock_which: A MagicMock of the shutil.which function.
        """
        repo_url = "https://mock_repo.com/git"

        # Run without branch
        repo_path = runner.clone_git_repo(repo_url, "")

        self.assertRegex(repo_path, r"repo_folder\\[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")
        mock_get_repo_folder_path.assert_called_once()
        mock_makedirs.assert_called_once_with(repo_path)
        mock_which.assert_called_once_with("git")
        mock_run.assert_called_once_with(["git", "clone", repo_url, repo_path], check=True)

        # Run with branch
        mock_run.reset_mock()
        repo_path = runner.clone_git_repo(repo_url, "branch1")
        mock_run.assert_called_once_with(["git", "clone", "-b", "branch1", repo_url, repo_path], check=True)

    @patch(f"{TEST_MODULE}.util.get_scheduler_name", return_value="Machine Name")
    @patch(f"{TEST_MODULE}.subprocess.Popen")
    @patch(f"{TEST_MODULE}.os.path.isfile", return_value=True)
    @patch(f"{TEST_MODULE}.find_main_file", return_value="main.py")
    @patch(f"{TEST_MODULE}.clone_git_repo", return_value="folder_path")
    def test_run_trigger(self, mock_clone_git_repo: MagicMock, mock_find_main_file: MagicMock, mock_isfile: MagicMock,
                         mock_popen: MagicMock, mock_get_scheduler_name: MagicMock):
        """Test the run_trigger function in the runner module.

        Args:
            mock_clone_git_repo: A MagicMock of the runner.clone_git_repo function.
            mock_find_main_file: A MagicMock of the runner.find_main_file function.
            mock_isfile: A MagicMock of the os.path.isfile function.
            mock_Popen: A MagicMock of the subprocess.Popen class.
            mock_get_scheduler_name: A MagicMock of the util.get_scheduler_name function.
        """
        trigger_id = db_util.create_single_trigger(
            trigger_name="Trigger Name",
            process_name="Process Name",
            next_run=datetime.now(),
            process_path="https://mock_repo.com/git",
            process_args="Arguments",
            is_git_repo=True,
            is_blocking=False,
            priority=0,
            scheduler_whitelist=[],
            git_branch="Branch"
        )

        trigger = db_util.get_trigger(trigger_id)
        job = runner.run_trigger(trigger)

        # Check the job object
        self.assertEqual(job.trigger, trigger)
        self.assertEqual(job.process_folder, "folder_path")

        # Check that the mock functions were called correctly
        mock_clone_git_repo.assert_called_once_with(trigger.process_path, trigger.git_branch)
        mock_find_main_file.assert_called_once_with("folder_path")
        mock_isfile.assert_called_once_with("main.py")
        mock_popen.assert_called_once_with(['python', "main.py", trigger.process_name, db_util.get_conn_string(), crypto_util.get_key(), trigger.process_args],
                                           stderr=subprocess.PIPE, text=True)
        mock_get_scheduler_name.assert_called_once()

        # Check that trigger status was set
        trigger = db_util.get_trigger(trigger_id)
        self.assertEqual(trigger.process_status, TriggerStatus.RUNNING)

        # Check that a ping was sent to the schedulers list
        schedulers = db_util.get_schedulers()
        self.assertEqual(schedulers[0].machine_name, "Machine Name")
        self.assertEqual(schedulers[0].latest_trigger, "Trigger Name")


if __name__ == '__main__':
    unittest.main()
