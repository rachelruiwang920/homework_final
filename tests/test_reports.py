"""報告裡的英文逐字句必須在一次來源擷取檔中，分析必須寫上實際測量值。"""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def test_blockquotes_are_primary_substrings(self) -> None:
        extracts = list((REPO / "provenance" / "primary" / "extracts").glob("*.txt"))
        blob = "\n".join(path.read_text(encoding="utf-8") for path in extracts)
        quoted = []
        for path in (REPO / "reports").glob("*.md"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("> "):
                    quoted.append((path.name, line[2:]))
        self.assertGreaterEqual(len(quoted), 8)
        for name, quote in quoted:
            self.assertIn(quote, blob, f"{name} 的摘錄不在一次來源擷取檔")

    def test_analysis_contains_the_csv(self) -> None:
        analysis = (REPO / "reports" / "03-analysis.md").read_text(encoding="utf-8")
        with (REPO / "comparison-evaluation.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIn(row["tool_calls"], analysis)
            self.assertIn(row["trajectory_sha256"], analysis)
            if row["failure_reasons"]:
                self.assertIn(row["failure_reasons"], analysis)
            if row["brief_sha256"]:
                self.assertIn(row["brief_sha256"], analysis)
        self.assertIn("不是兩次獨立隨機試驗", analysis)
        self.assertIn("最容易出錯的一步", analysis)
        self.assertIn("自建", analysis)

    def test_checklist_maps_supplied_weights(self) -> None:
        checklist = (REPO / "SUBMISSION_CHECKLIST.md").read_text(encoding="utf-8")
        snapshot = (REPO / "requirements" / "AT3-original-requirements.md").read_text(encoding="utf-8")
        for phrase in ("8%", "12%", "10%", "前沿性", "覆蓋度", "復現度", "可運行性"):
            self.assertIn(phrase, checklist, phrase)
        self.assertIn("max_steps", snapshot)
        self.assertIn("每天", snapshot)
        self.assertNotIn("教師評分規準都沒有附", checklist)


if __name__ == "__main__":
    unittest.main()
