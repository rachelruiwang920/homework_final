"""路徑侷限。工具只能碰到呼叫端明示的根目錄。"""

from __future__ import annotations

import re
from pathlib import Path


class PathEscape(ValueError):
    """使用者提供的路徑或來源代號試圖離開允許的根目錄。"""


SOURCE_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def require_source_id(source_id: str) -> str:
    if not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id):
        raise PathEscape(f"拒絕來源代號：{source_id!r}")
    return source_id


def resolve_inside(root: Path, relative: Path) -> Path:
    """把 relative 解析到 root 之內。拒絕絕對路徑、上層目錄與連出根目錄的符號連結。"""
    root_real = root.resolve()
    if relative.is_absolute() or any(part == ".." for part in relative.parts):
        raise PathEscape(f"拒絕路徑：{relative}")
    if any(part.startswith("/") or "\x00" in part for part in relative.parts):
        raise PathEscape(f"拒絕路徑：{relative}")
    candidate = (root_real / relative).resolve()
    if not candidate.is_relative_to(root_real):
        raise PathEscape(f"路徑逸出根目錄：{relative}")
    return candidate
