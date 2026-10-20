import dataclasses
from datetime import datetime, timezone
import unittest

from ues_community_signal.aggregate import PublicItem, aggregate_items


class AggregateTests(unittest.TestCase):
    def test_output_has_no_raw_text_author_or_content_id_fields(self):
        items = [
            PublicItem("one", datetime(2026, 10, 19, tzinfo=timezone.utc), "AAPL bullish", "Apple upside"),
            PublicItem("two", datetime(2026, 10, 19, tzinfo=timezone.utc), "Apple strong", "AAPL"),
            PublicItem("three", datetime(2026, 10, 19, tzinfo=timezone.utc), "AAPL growth", "Apple"),
        ]
        rows = aggregate_items(items, {"AAPL": ("AAPL", "Apple")})
        self.assertEqual(len(rows), 1)
        row = dataclasses.asdict(rows[0])
        self.assertEqual(row["mention_count"], 3)
        self.assertEqual(row["positive_count"], 3)
        self.assertFalse(row["suppressed"])
        self.assertTrue({"title", "body", "author", "content_id"}.isdisjoint(row))

    def test_duplicate_content_is_counted_once_and_sparse_output_is_flagged(self):
        item = PublicItem("same", datetime(2026, 10, 19, tzinfo=timezone.utc), "AAPL", "bearish")
        rows = aggregate_items([item, item], {"AAPL": ("AAPL",)})
        self.assertTrue(rows[0].suppressed)
        self.assertIsNone(rows[0].mention_count)
        self.assertIsNone(rows[0].negative_count)

    def test_suppression_threshold_cannot_be_reduced_below_three(self):
        with self.assertRaises(ValueError):
            aggregate_items([], {}, minimum_publishable_mentions=2)

    def test_naive_timestamp_is_rejected(self):
        item = PublicItem("one", datetime(2026, 10, 19), "AAPL", "bullish")
        with self.assertRaises(ValueError):
            aggregate_items([item], {"AAPL": ("AAPL",)})


if __name__ == "__main__":
    unittest.main()
