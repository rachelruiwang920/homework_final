"""跑 max_steps=3 與 max_steps=6，並把完成條件的產物放到 completed/ 與倉庫根目錄。"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from react_min.loop import run_condition


ROOT_ARTIFACTS = (
    "final-brief.md",
    "task-contract.json",
    "tool-schema.json",
    "trajectory.jsonl",
    "tool-results.jsonl",
    "evaluation.csv",
    "error-note.md",
    "provenance.json",
)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    runs = repo_root / "runs"
    if runs.exists():
        shutil.rmtree(runs)
    completed = repo_root / "completed"
    if completed.exists():
        shutil.rmtree(completed)
    evidence = repo_root / "evidence"
    evidence.mkdir(exist_ok=True)

    summaries = []
    for max_steps in (3, 6):
        condition = f"max_steps_{max_steps}"
        out_dir = runs / condition
        row = run_condition(
            repo_root=repo_root,
            out_dir=out_dir,
            max_steps=max_steps,
            condition=condition,
        )
        summaries.append(row)
        print(
            f"{condition} pass={row['validator_pass']} tools={row['tool_calls']} "
            f"search={row['search_calls']} read={row['read_calls']} write={row['write_calls']} "
            f"observed={row['slots_observed']} cited={row['slots_cited']} "
            f"unused={row['unused_steps']} reasons={row['failure_reasons']}"
        )

    success = runs / "max_steps_6"
    shutil.copytree(success, completed)
    for name in ROOT_ARTIFACTS:
        shutil.copyfile(success / name, repo_root / name)

    comparison = repo_root / "comparison-evaluation.csv"
    with comparison.open("w", encoding="utf-8", newline="") as handle:
        writer = None
        for max_steps in (3, 6):
            with (runs / f"max_steps_{max_steps}" / "evaluation.csv").open(
                encoding="utf-8", newline=""
            ) as source:
                reader = csv.DictReader(source)
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=reader.fieldnames)
                    writer.writeheader()
                for record in reader:
                    writer.writerow(record)

    (evidence / "summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    short = runs / "max_steps_3" / "evaluation.csv"
    long = runs / "max_steps_6" / "evaluation.csv"
    failed = json.loads((evidence / "summary.json").read_text(encoding="utf-8"))
    if failed[0]["validator_pass"] or not failed[1]["validator_pass"]:
        print("實驗結果不符合這個任務預期的一敗一成，請看 evidence/summary.json", file=sys.stderr)
        return 1
    print(f"已寫入 {short.relative_to(repo_root)} 與 {long.relative_to(repo_root)}")
    print("完成條件已複製到 completed/ 與倉庫根目錄。這不是教師驗證器的結果。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
