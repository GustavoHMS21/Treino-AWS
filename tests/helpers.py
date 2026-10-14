import tempfile
import unittest
from pathlib import Path

import database


class TempDatabase(unittest.TestCase):
    """Roda cada teste num banco temporário, sem tocar em data/simulator.db."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._original = database.DB_PATH
        database.DB_PATH = Path(self._dir.name) / "simulator.db"
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self._original
        self._dir.cleanup()
