"""ReAct 外形的工具迴圈。

步數上限只決定迴圈還能不能再呼叫一次工具。
通過與否由 validate.evaluate_run 事後讀檔決定，不在這裡按 max_steps 給分。
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from react_min import __version__
from react_min.pack import load_sourcepack
from react_min.policy import AgentState, decide
from react_min.tools import read_source, search_sources, write_brief
from react_min.validate import evaluate_run, write_evaluation_csv


def _dump(obj: dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_condition(
    *,
    repo_root: Path,
    out_dir: Path,
    max_steps: int,
    condition: str,
) -> dict[str, Any]:
    if max_steps < 0:
        raise ValueError("max_steps 不可為負")
    contract_path = repo_root / "task" / "task-contract.json"
    schema_path = repo_root / "task" / "tool-schema.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    source_root = repo_root / "sourcepack"
    docs = load_sourcepack(source_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "task-contract.json").write_text(
        contract_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (out_dir / "tool-schema.json").write_text(schema_path.read_text(encoding="utf-8"), encoding="utf-8")

    state = AgentState()
    trajectory: list[dict[str, Any]] = []
    tool_results: list[dict[str, Any]] = []
    stop_reason = ""
    pending: dict[str, Any] | None = None

    for step in range(1, max_steps + 1):
        decision = decide(state, contract)
        if decision.tool == "stop":
            stop_reason = str(decision.args.get("reason", "stop"))
            break
        if decision.tool == "search":
            result = search_sources(docs, decision.args["phrases"])
            state.searched = True
            state.hits = result["results"]
        elif decision.tool == "read":
            result = read_source(docs, decision.args["source_id"])
            state.reads.append(result)
        elif decision.tool == "write":
            result = write_brief(docs, state.reads, contract, out_dir)
            state.written = bool(result.get("ok"))
        else:
            raise RuntimeError(f"未知工具：{decision.tool}")
        record = {
            "step": step,
            "thought": decision.thought,
            "thought_origin": "scripted_template",
            "llm": False,
            "tool": decision.tool,
            "arguments": decision.args,
        }
        trajectory.append(record)
        stored = dict(result)
        stored["step"] = step
        tool_results.append(stored)
    else:
        stop_reason = "budget_exhausted"
        nxt = decide(state, contract)
        pending = {
            "tool": nxt.tool,
            "arguments": nxt.args,
            "thought": nxt.thought,
            "executed": False,
        }

    (out_dir / "trajectory.jsonl").write_text(
        "".join(_dump(row) + "\n" for row in trajectory), encoding="utf-8"
    )
    (out_dir / "tool-results.jsonl").write_text(
        "".join(_dump(row) + "\n" for row in tool_results), encoding="utf-8"
    )
    (out_dir / "error-note.md").write_text(
        _error_note(
            max_steps=max_steps,
            stop_reason=stop_reason,
            n_calls=len(trajectory),
            pending=pending,
            written=state.written,
        ),
        encoding="utf-8",
    )
    provenance = _provenance(
        repo_root=repo_root,
        contract_path=contract_path,
        schema_path=schema_path,
        source_root=source_root,
        max_steps=max_steps,
        condition=condition,
        stop_reason=stop_reason,
        n_calls=len(trajectory),
    )
    (out_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    evaluation = evaluate_run(out_dir, source_root, contract)
    write_evaluation_csv(out_dir / "evaluation.csv", evaluation)
    return evaluation


def _error_note(
    *,
    max_steps: int,
    stop_reason: str,
    n_calls: int,
    pending: dict[str, Any] | None,
    written: bool,
) -> str:
    lines = [
        "# 執行註記",
        "",
        "本檔由確定性執行器寫出，不是教師評語，也不是模型輸出。",
        "來源依使用者指示自行選定。驗證器是自建的。未宣稱通過教師驗證器。",
        "",
        f"- 步數上限：{max_steps}",
        f"- 已執行工具呼叫：{n_calls}",
        f"- 停止原因代碼：{stop_reason}",
        f"- 是否寫入 final-brief.md：{'是' if written else '否'}",
        "",
    ]
    if stop_reason == "budget_exhausted":
        lines.append("工具迴圈在寫完簡報之前用盡步數。")
        lines.append("下面這個動作是同一政策在停下來之後會做的下一步，它沒有被執行，也不在 trajectory.jsonl 裡。")
        if pending:
            lines.append("")
            lines.append("```")
            lines.append(_dump({"not_executed": True, **pending}))
            lines.append("```")
        lines.append("")
        lines.append("因此這個條件沒有最終簡報。驗證器會因為缺少簡報與未完成引用而不通過。")
    elif stop_reason == "complete":
        unused = max_steps - n_calls
        lines.append("簡報已寫入。這不是失敗。")
        lines.append(f"步數上限還剩 {unused} 次沒有使用。檔名仍沿用作業要求的 error-note.md。")
    elif stop_reason == "no_more_hits":
        lines.append("候選來源已讀完，證據槽仍未齊，政策停止，沒有寫入簡報。")
    else:
        lines.append("執行器沒有把這次停止歸成上述三類。請直接看軌跡。")
    lines.append("")
    return "\n".join(lines)


def _provenance(
    *,
    repo_root: Path,
    contract_path: Path,
    schema_path: Path,
    source_root: Path,
    max_steps: int,
    condition: str,
    stop_reason: str,
    n_calls: int,
) -> dict[str, Any]:
    source_hashes = {}
    for path in sorted((source_root / "sources").glob("*.txt")):
        source_hashes[path.name] = _file_sha(path)
    code_hashes = {}
    for path in sorted((repo_root / "react_min").glob("*.py")):
        code_hashes[path.name] = _file_sha(path)
    return {
        "fixture_origin": "self_selected_per_user_instruction",
        "source_selection": "使用者於 2026-11-17 指示以自行選定的相關論文摘錄作為來源，不把缺少教師來源包當成未完成事項。",
        "teacher_source_pack_attached": False,
        "teacher_source_pack_blocking": False,
        "teacher_validator_executed": False,
        "teacher_approval_claimed": False,
        "grade_claimed": False,
        "controller_type": "deterministic_scripted_policy",
        "llm_used": False,
        "model_output": False,
        "package_version": __version__,
        "condition": condition,
        "max_steps": max_steps,
        "stop_reason": stop_reason,
        "tool_calls_executed": n_calls,
        "offset_unit": "utf-8 bytes",
        "python": sys.version,
        "platform": platform.platform(),
        "executed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contract_sha256": _file_sha(contract_path),
        "tool_schema_sha256": _file_sha(schema_path),
        "source_sha256": source_hashes,
        "code_sha256": code_hashes,
        "command_note": "python3 scripts/run_experiment.py",
    }
