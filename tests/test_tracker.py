"""Run:  python -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analysis
import storage
import validation as v

PODCASTS = pd.DataFrame({"podcast": ["Alpha", "Beta"], "category": ["History", "Business"]})
EPISODES = pd.DataFrame({
    "podcast": ["Alpha", "Alpha", "Beta", "Alpha", "Beta"],
    "title":   ["a1", "a2", "b1", "a3", "b2"],
    "date":    ["2026-07-01", "2026-07-02", "2026-07-03", "2026-07-20", "2026-08-10"],
    "minutes": [60, 40, 30, 50, 20],
    "rating":  [5, 4, 2, 5, 3]})
DF = analysis.prepare(EPISODES, PODCASTS)


class ValidationTests(unittest.TestCase):
    def test_valid_input(self):
        self.assertEqual(v.check_text("  Rewind   History ", "Name"), "Rewind History")
        self.assertEqual(v.check_date("2026-09-30"), "2026-09-30")
        self.assertEqual(v.check_number("45", "Minutes", 1, 600), 45)

    def test_bad_text(self):
        for bad in ("", "   ", "<script>", "x" * 61):
            with self.assertRaises(ValueError):
                v.check_text(bad, "Name")

    def test_bad_dates(self):
        for bad in ("", "30-09-2026", "2026-02-30", "2999-01-01", "abc"):
            with self.assertRaises(ValueError):
                v.check_date(bad)

    def test_bad_numbers(self):
        for bad in ("", "0", "601", "-5", "4.5", "abc"):
            with self.assertRaises(ValueError):
                v.check_number(bad, "Minutes", 1, 600)

    def test_bad_category(self):
        with self.assertRaises(ValueError):
            v.check_category("Cooking")


class AnalysisTests(unittest.TestCase):
    def test_totals(self):
        t = analysis.totals(DF)
        self.assertEqual((t["episodes"], t["total_minutes"]), (5, 200))
        self.assertEqual((t["avg_minutes"], t["avg_rating"]), (40.0, 3.8))

    def test_by_podcast(self):
        t = analysis.by_podcast(DF)
        self.assertEqual(t.loc["Alpha", "minutes"], 150)
        self.assertAlmostEqual(t.loc["Alpha", "avg_rating"], 4.67)
        self.assertEqual(list(t.index), ["Alpha", "Beta"])

    def test_by_month(self):
        t = analysis.by_month(DF)
        self.assertEqual(list(t["minutes"]), [180, 20])
        self.assertEqual(t["change"].iloc[1], -160)

    def test_consistency(self):
        c = analysis.consistency(DF)
        self.assertEqual((c["days_listened"], c["days_in_period"]), (5, 41))
        self.assertEqual(c["longest_break"], 20)     # 20 silent days between Jul 20 and Aug 10

    def test_preferences(self):
        p = analysis.preferences(DF)
        self.assertEqual((p["most_listened"], p["best_rated"]), ("Alpha", "Alpha"))
        self.assertEqual(p["favourite_category"], "History")
        self.assertEqual(p["liked_percent"], 60.0)


class StorageTests(unittest.TestCase):
    def test_missing_file_gives_empty_table(self):
        table = storage.load("no_such_file.csv", storage.PODCAST_COLS)
        self.assertTrue(table.empty)

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.csv"
            PODCASTS.to_csv(path, index=False)
            self.assertEqual(len(storage.load(path, storage.PODCAST_COLS)), 2)

    def test_wrong_columns(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("a,b\n1,2\n")
            with self.assertRaises(ValueError):
                storage.load(path, storage.PODCAST_COLS)


if __name__ == "__main__":
    unittest.main()
