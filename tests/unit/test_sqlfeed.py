from pathlib import Path
import unittest

from roboquant import SQLFeed
from tests.common import get_feed, run_priceaction_feed
import tempfile


class TestSQLFeed(unittest.TestCase):

    def test_sql_feed(self):
        path = tempfile.gettempdir()
        db_file = Path(path).joinpath("tmp.db")
        db_file.unlink(missing_ok=True)
        self.assertFalse(db_file.exists())

        feed = SQLFeed(db_file)

        origin_feed = get_feed()
        feed.record(origin_feed)
        self.assertTrue(db_file.exists())

        self.assertEqual(origin_feed.timeframe(), feed.timeframe())
        feed.create_index()

        self.assertEqual(set(origin_feed.symbols), set(feed.symbols()))

        run_priceaction_feed(feed, origin_feed.symbols, self)
        db_file.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
