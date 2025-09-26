"""This module contains tests of the functionality of alembic database migration."""

import unittest
import os
import subprocess
import sys

from OpenOrchestrator.database import db_util
from OpenOrchestrator.tests import db_test_util


class TestAlembic(unittest.TestCase):
    """Test functionality of Alembic database migrations."""
    def setUp(self) -> None:
        db_util.connect(os.environ["CONN_STRING"])
        db_test_util.drop_all_tables()

    def test_new_database(self):
        """Test creating a new database with Alembic"""
        subprocess.run([sys.executable, "-m", "OpenOrchestrator", "u", os.environ["CONN_STRING"], "--new"], check=True)


if __name__ == '__main__':
    unittest.main()