"""同一任務只改 max_steps。通過與否必須來自真正跑完的工具迴圈。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_excerpts import check
from react_min.loop import run_condition
from react_min.pack import load_sourcepack
from react_min.tools import search_sources


REPO = Path(__file__).resolve().parents[1]


class BudgetTests(unittest.TestCase):
    def test_excerpts_match_primary_files(self) -> None:
        self.assertEqual(check(REPO), [])

    def test_each_anchor_is_in_exactly_one_source(self) -> None:
        contract = json.loads((REPO / "task" / "task-contract.json").read_text(encoding="utf-8"))
        docs = load_sourcepack(REPO / "sourcepack")
        for slot in contract["required_slots"]:
            holders = [source_id for source_id, doc in docs.items() if slot["anchor"] in doc.text]
            self.assertEqual(holders, [holders[0]] if holders else [], slot["slot_id"])
            self.assertEqual(len(holders), 1, slot["slot_id"])

    def test_search_ranks_three_anchor_documents_first(self) -> None:
        contract = json.loads((REPO / "task" / "task-contract.json").read_text(encoding="utf-8"))
        docs = load_sourcepack(REPO / "sourcepack")
        found = search_sources(docs, contract["search_phrases"])
        top = found["results"][:3]
        self.assertTrue(all(row["phrase_hits"] == 1 for row in top))
        self.assertTrue(all(row["phrase_hits"] == 0 for row in found["results"][3:]))
        self.assertEqual(len(found["results"]), 7)

    def test_short_budget_fails_and_long_budget_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            short = run_condition(
                repo_root=REPO, out_dir=root / "short", max_steps=3, condition="max_steps_3"
            )
            long = run_condition(
                repo_root=REPO, out_dir=root / "long", max_steps=6, condition="max_steps_6"
            )
            self.assertFalse((root / "short" / "final-brief.md").exists())
            self.assertTrue((root / "long" / "final-brief.md").is_file())
        self.assertFalse(short["validator_pass"])
        self.assertEqual(short["tool_calls"], 3)
        self.assertEqual(short["search_calls"], 1)
        self.assertEqual(short["read_calls"], 2)
        self.assertEqual(short["write_calls"], 0)
        self.assertEqual(short["slots_observed"], 2)
        self.assertEqual(short["slots_cited"], 0)
        self.assertIn("no_final_brief", short["failure_reasons"])
        self.assertTrue(long["validator_pass"])
        self.assertEqual(long["tool_calls"], 5)
        self.assertEqual(long["search_calls"], 1)
        self.assertEqual(long["read_calls"], 3)
        self.assertEqual(long["write_calls"], 1)
        self.assertEqual(long["slots_observed"], 3)
        self.assertEqual(long["slots_cited"], 3)
        self.assertEqual(long["unused_steps"], 1)
        self.assertEqual(long["failure_reasons"], "")
        self.assertFalse(long["teacher_validator"])

    def test_rerun_is_identical_except_wall_clock(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run_condition(repo_root=REPO, out_dir=root / "a", max_steps=6, condition="max_steps_6")
            run_condition(repo_root=REPO, out_dir=root / "b", max_steps=6, condition="max_steps_6")
            for name in (
                "final-brief.md",
                "trajectory.jsonl",
                "tool-results.jsonl",
                "evaluation.csv",
                "error-note.md",
            ):
                self.assertEqual(
                    (root / "a" / name).read_bytes(),
                    (root / "b" / name).read_bytes(),
                    name,
                )
            left = json.loads((root / "a" / "provenance.json").read_text(encoding="utf-8"))
            right = json.loads((root / "b" / "provenance.json").read_text(encoding="utf-8"))
            left.pop("executed_at_utc")
            right.pop("executed_at_utc")
            self.assertEqual(left, right)

    def test_controller_does_not_hardcode_budget_or_source_ids(self) -> None:
        for path in (REPO / "react_min").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for banned in ("max_steps == 3", "max_steps == 6", "max_steps==3", "max_steps==6"):
                self.assertNotIn(banned, text, path.name)
        policy = (REPO / "react_min" / "policy.py").read_text(encoding="utf-8")
        for source_id in (
            "react_2023",
            "toolformer_2023",
            "agentbench_2024",
            "validator_pass = True",
        ):
            self.assertNotIn(source_id, policy)

    def test_same_contract_bytes_for_both_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run_condition(repo_root=REPO, out_dir=root / "s", max_steps=3, condition="max_steps_3")
            run_condition(repo_root=REPO, out_dir=root / "l", max_steps=6, condition="max_steps_6")
            self.assertEqual(
                (root / "s" / "task-contract.json").read_bytes(),
                (root / "l" / "task-contract.json").read_bytes(),
            )
            self.assertEqual(
                (root / "s" / "tool-schema.json").read_bytes(),
                (root / "l" / "tool-schema.json").read_bytes(),
            )
            short_trace = (root / "s" / "trajectory.jsonl").read_text(encoding="utf-8")
            self.assertNotIn('"tool": "write"', short_trace)
            self.assertIn("非模型輸出", short_trace)
            long_brief = (root / "l" / "final-brief.md").read_text(encoding="utf-8")
            self.assertIn("【自撰轉述】", long_brief)
            self.assertIn(":::citation", long_brief)

    def test_committed_runs_match_a_fresh_execution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run_condition(repo_root=REPO, out_dir=root / "s", max_steps=3, condition="max_steps_3")
            run_condition(repo_root=REPO, out_dir=root / "l", max_steps=6, condition="max_steps_6")
            for condition, folder in (("max_steps_3", "s"), ("max_steps_6", "l")):
                for name in ("trajectory.jsonl", "tool-results.jsonl", "evaluation.csv", "error-note.md"):
                    self.assertEqual(
                        (REPO / "runs" / condition / name).read_bytes(),
                        (root / folder / name).read_bytes(),
                        f"{condition}/{name}",
                    )
            self.assertEqual(
                (REPO / "final-brief.md").read_bytes(),
                (root / "l" / "final-brief.md").read_bytes(),
            )
            self.assertFalse((REPO / "runs" / "max_steps_3" / "final-brief.md").exists())


if __name__ == "__main__":
    unittest.main()
