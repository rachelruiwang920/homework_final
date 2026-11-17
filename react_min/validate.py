"""自建驗證器。

它重讀來源檔與簡報，不讀 max_steps，也不把軌跡裡的成功旗標當成分數。
這裡的通過只表示自建規則通過。來源是依使用者指示自行選定的。沒有宣稱教師認可，也沒有模型輸出。
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from react_min.pack import load_sourcepack
from react_min.security import PathEscape, require_source_id


CITATION_RE = re.compile(
    r":::citation source=([^\n]+) start=(\d+) end=(\d+) sha256=([0-9a-f]{64})\n(.*?)\n:::\n",
    re.DOTALL,
)

REQUIRED_LABELS = (
    "不是語言模型輸出",
    "自建替代",
    "未宣稱通過教師驗證器",
)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no} 不是 JSON") from exc
    return rows


def check_brief(text: str, docs: dict, slots: list[dict[str, str]]) -> dict[str, Any]:
    reasons: list[str] = []
    for label in REQUIRED_LABELS:
        if label not in text:
            reasons.append(f"missing_label:{label}")
    matches = list(CITATION_RE.finditer(text))
    openings = len(re.findall(r"(?m)^:::citation\b", text))
    closings = len(re.findall(r"(?m)^:::$", text))
    if openings != len(matches) or closings != len(matches):
        reasons.append("unmatched_citation_marker")
    cited_slots: list[str] = []
    seen_quotes: list[str] = []
    for match in matches:
        source_raw, start_s, end_s, digest, quote = match.groups()
        try:
            source_id = require_source_id(source_raw)
        except PathEscape:
            reasons.append("path_rejected")
            continue
        doc = docs.get(source_id)
        if doc is None:
            reasons.append(f"unknown_source:{source_raw}")
            continue
        start, end = int(start_s), int(end_s)
        blob = quote.encode("utf-8")
        if start < 0 or end > len(doc.data) or doc.data[start:end] != blob:
            reasons.append(f"bad_citation_span:{source_id}:{start}:{end}")
            continue
        actual = hashlib.sha256(doc.data[start:end]).hexdigest()
        if actual != digest:
            reasons.append(f"bad_citation_hash:{source_id}")
            continue
        seen_quotes.append(quote)
    for slot in slots:
        if any(slot["anchor"] in quote for quote in seen_quotes):
            cited_slots.append(slot["slot_id"])
        else:
            reasons.append(f"slot_not_cited:{slot['slot_id']}")
    return {
        "reasons": reasons,
        "slots_cited": cited_slots,
        "n_citations": len(matches),
    }


def evaluate_run(run_dir: Path, source_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    docs = load_sourcepack(source_root)
    reasons: list[str] = []
    trajectory_path = run_dir / "trajectory.jsonl"
    results_path = run_dir / "tool-results.jsonl"
    brief_path = run_dir / "final-brief.md"
    if not trajectory_path.is_file():
        reasons.append("missing_trajectory")
        trajectory: list[dict[str, Any]] = []
    else:
        trajectory = _load_jsonl(trajectory_path)
    if not results_path.is_file():
        reasons.append("missing_tool_results")
        results: list[dict[str, Any]] = []
    else:
        results = _load_jsonl(results_path)

    tool_names = [row.get("tool", "") for row in trajectory]
    search_calls = tool_names.count("search")
    read_calls = tool_names.count("read")
    write_calls = tool_names.count("write")
    observed: list[str] = []
    for row in results:
        if row.get("tool") != "read" or not row.get("ok"):
            continue
        source_id = row.get("source_id", "")
        doc = docs.get(source_id)
        if doc is None or hashlib.sha256(doc.data).hexdigest() != row.get("sha256"):
            reasons.append(f"read_hash_mismatch:{source_id}")
            continue
        for slot in contract["required_slots"]:
            if slot["anchor"] in doc.text and slot["slot_id"] not in observed:
                observed.append(slot["slot_id"])

    brief_sha = ""
    slots_cited: list[str] = []
    if not brief_path.is_file():
        reasons.append("no_final_brief")
    else:
        brief_bytes = brief_path.read_bytes()
        brief_sha = hashlib.sha256(brief_bytes).hexdigest()
        brief_check = check_brief(brief_bytes.decode("utf-8"), docs, contract["required_slots"])
        reasons.extend(brief_check["reasons"])
        slots_cited = brief_check["slots_cited"]

    # 穩定順序，方便重跑比對。
    deduped: list[str] = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)
    passed = not deduped
    trajectory_sha = ""
    if trajectory_path.is_file():
        trajectory_sha = hashlib.sha256(trajectory_path.read_bytes()).hexdigest()
    provenance_path = run_dir / "provenance.json"
    max_steps: Any = ""
    condition = ""
    unused_steps: Any = ""
    if provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        max_steps = provenance.get("max_steps", "")
        condition = provenance.get("condition", "")
        if isinstance(max_steps, int):
            unused_steps = max_steps - len(trajectory)
    return {
        "condition": condition,
        "max_steps": max_steps,
        "completed": passed,
        "validator_pass": passed,
        "tool_calls": len(trajectory),
        "search_calls": search_calls,
        "read_calls": read_calls,
        "write_calls": write_calls,
        "slots_required": len(contract["required_slots"]),
        "slots_observed": len(observed),
        "slots_cited": len(slots_cited),
        "failure_reasons": "|".join(deduped),
        "brief_sha256": brief_sha,
        "trajectory_sha256": trajectory_sha,
        "unused_steps": unused_steps,
        "rubric": "self_built_rubric_v1",
        "teacher_validator": False,
    }


def write_evaluation_csv(path: Path, row: dict[str, Any]) -> None:
    fields = [
        "condition",
        "max_steps",
        "completed",
        "validator_pass",
        "tool_calls",
        "search_calls",
        "read_calls",
        "write_calls",
        "slots_required",
        "slots_observed",
        "slots_cited",
        "failure_reasons",
        "brief_sha256",
        "trajectory_sha256",
        "unused_steps",
        "rubric",
        "teacher_validator",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in fields})
