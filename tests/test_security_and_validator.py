"""驗證器的負例，以及路徑不能逃出來源根目錄。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from react_min.pack import load_sourcepack
from react_min.security import PathEscape
from react_min.tools import read_source, write_brief
from react_min.validate import check_brief, evaluate_run


REPO = Path(__file__).resolve().parents[1]


def _write_source(directory: Path, source_id: str, quote: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    text = (
        f"SOURCE_ID: {source_id}\n"
        "KIND: unit_fixture\n"
        "FIXTURE_ORIGIN: self_built_substitute\n"
        "TITLE: unit\n"
        f"VERBATIM\tline\tprovenance/unused.txt\t{quote}\n"
    )
    (directory / f"{source_id}.txt").write_text(text, encoding="utf-8")


class SecurityTests(unittest.TestCase):
    def test_read_rejects_path_like_ids(self) -> None:
        docs = load_sourcepack(REPO / "sourcepack")
        for source_id in ("../secret", "/etc/passwd", "react_2023/../../x", "..", "Alpha"):
            result = read_source(docs, source_id)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "path_rejected")

    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            outside = root / "secret.txt"
            outside.write_text("SECRET", encoding="utf-8")
            sources = root / "sourcepack" / "sources"
            sources.mkdir(parents=True)
            link = sources / "beta_note.txt"
            link.symlink_to(outside)
            with self.assertRaises(PathEscape):
                load_sourcepack(root / "sourcepack")


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sources = self.root / "sourcepack" / "sources"
        _write_source(sources, "alpha_note", "alpha evidence sentence stays here")
        _write_source(sources, "beta_note", "beta evidence sentence stays here")
        self.docs = load_sourcepack(self.root / "sourcepack")
        self.slots = [
            {"slot_id": "alpha_slot", "anchor": "alpha evidence sentence"},
            {"slot_id": "beta_slot", "anchor": "beta evidence sentence"},
        ]
        self.contract = {
            "question": "測試問題",
            "search_phrases": ["alpha evidence sentence", "beta evidence sentence"],
            "required_slots": self.slots,
            "paraphrase_templates": {
                "alpha_slot": "甲槽只重述已讀到的那句。",
                "beta_slot": "乙槽只重述已讀到的那句。",
            },
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _good_brief(self) -> str:
        reads = [
            {"ok": True, "source_id": "alpha_note", "text": self.docs["alpha_note"].text},
            {"ok": True, "source_id": "beta_note", "text": self.docs["beta_note"].text},
        ]
        out = self.root / "out"
        out.mkdir()
        result = write_brief(self.docs, reads, self.contract, out)
        self.assertTrue(result["ok"])
        return (out / "final-brief.md").read_text(encoding="utf-8")

    def test_good_brief_passes(self) -> None:
        report = check_brief(self._good_brief(), self.docs, self.slots)
        self.assertEqual(report["reasons"], [])
        self.assertEqual(report["slots_cited"], ["alpha_slot", "beta_slot"])

    def test_anchor_in_prose_is_not_evidence(self) -> None:
        text = (
            "不是語言模型輸出。自建替代。未宣稱通過教師驗證器。\n"
            "alpha evidence sentence\nbeta evidence sentence\n"
        )
        report = check_brief(text, self.docs, self.slots)
        self.assertIn("slot_not_cited:alpha_slot", report["reasons"])
        self.assertIn("slot_not_cited:beta_slot", report["reasons"])

    def test_bad_span_and_bad_hash(self) -> None:
        brief = self._good_brief()
        span_broken = brief.replace("start=", "start=1", 1).replace("end=", "end=2", 1)
        span_report = check_brief(span_broken, self.docs, self.slots)
        self.assertTrue(any(item.startswith("bad_citation_span:") for item in span_report["reasons"]))
        digest = brief.split("sha256=", 1)[1][:64]
        hash_broken = brief.replace(digest, "0" * 64, 1)
        hash_report = check_brief(hash_broken, self.docs, self.slots)
        self.assertTrue(any(item.startswith("bad_citation_hash:") for item in hash_report["reasons"]))

    def test_missing_slot_and_path_source(self) -> None:
        brief = self._good_brief()
        # 去掉 beta 的引用區塊，錨點仍可能留在被刪除前的位置；直接構造只含 alpha 的簡報。
        alpha_only = brief.split(":::citation source=beta_note", 1)[0]
        alpha_only += "\n## 尾\n"
        report = check_brief(alpha_only, self.docs, self.slots)
        self.assertIn("slot_not_cited:beta_slot", report["reasons"])
        self.assertNotIn("slot_not_cited:alpha_slot", report["reasons"])
        forged = (
            "不是語言模型輸出。自建替代。未宣稱通過教師驗證器。\n"
            ":::citation source=../secret start=0 end=4 sha256="
            + ("a" * 64)
            + "\nnope\n:::\n"
        )
        forged_report = check_brief(forged, self.docs, self.slots)
        self.assertIn("path_rejected", forged_report["reasons"])

    def test_missing_brief_fails_run(self) -> None:
        run = self.root / "run"
        run.mkdir()
        (run / "trajectory.jsonl").write_text(
            json.dumps({"step": 1, "tool": "search", "llm": False}) + "\n", encoding="utf-8"
        )
        (run / "tool-results.jsonl").write_text(
            json.dumps({"step": 1, "tool": "search", "ok": True, "results": []}) + "\n",
            encoding="utf-8",
        )
        (run / "provenance.json").write_text(
            json.dumps({"condition": "unit", "max_steps": 1}), encoding="utf-8"
        )
        row = evaluate_run(run, self.root / "sourcepack", self.contract)
        self.assertFalse(row["validator_pass"])
        self.assertIn("no_final_brief", row["failure_reasons"])

    def test_write_refuses_incomplete_evidence(self) -> None:
        reads = [{"ok": True, "source_id": "alpha_note", "text": self.docs["alpha_note"].text}]
        out = self.root / "partial"
        out.mkdir()
        result = write_brief(self.docs, reads, self.contract, out)
        self.assertFalse(result["ok"])
        self.assertFalse((out / "final-brief.md").exists())


if __name__ == "__main__":
    unittest.main()
