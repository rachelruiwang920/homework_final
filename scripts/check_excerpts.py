"""確認來源包裡的每一條 VERBATIM 都是一次來源擷取檔的子字串。"""

from __future__ import annotations

import sys
from pathlib import Path


def check(repo_root: Path) -> list[str]:
    errors: list[str] = []
    sources = repo_root / "sourcepack" / "sources"
    for path in sorted(sources.glob("*.txt")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.startswith("VERBATIM\t"):
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                errors.append(f"{path.name}:{line_no} 欄位數不是 4")
                continue
            _, key, primary, quote = parts
            target = repo_root / primary
            if not target.is_file():
                errors.append(f"{path.name}:{line_no} {key} 找不到 {primary}")
                continue
            if quote not in target.read_text(encoding="utf-8"):
                errors.append(f"{path.name}:{line_no} {key} 不是 {primary} 的子字串")
    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    errors = check(repo_root)
    if errors:
        print("摘錄核對失敗")
        for error in errors:
            print(error)
        return 1
    print(f"摘錄核對通過：{repo_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
