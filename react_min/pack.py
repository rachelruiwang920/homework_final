"""讀取自建來源包。每一條 VERBATIM 都必須能在指定的一次來源擷取檔裡找到。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from react_min.security import require_source_id, resolve_inside


@dataclass(frozen=True)
class Verbatim:
    key: str
    primary: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class SourceDoc:
    source_id: str
    path: Path
    data: bytes
    text: str
    fields: dict[str, str]
    verbatims: tuple[Verbatim, ...]


def _parse(path: Path, data: bytes) -> SourceDoc:
    text = data.decode("utf-8")
    fields: dict[str, str] = {}
    verbatims: list[Verbatim] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.startswith("VERBATIM\t"):
            parts = line.split("\t")
            if len(parts) != 4:
                raise ValueError(f"{path}:{line_no} VERBATIM 欄位必須是 4 段")
            _, key, primary, quote = parts
            if not key or not primary or not quote:
                raise ValueError(f"{path}:{line_no} VERBATIM 有空欄")
            blob = quote.encode("utf-8")
            start = data.find(blob)
            if start < 0 or data.find(blob, start + 1) != -1:
                raise ValueError(f"{path}:{line_no} 引文必須在檔內恰好出現一次")
            verbatims.append(
                Verbatim(key=key, primary=primary, text=quote, start=start, end=start + len(blob))
            )
        elif "\t" not in line and ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            key = key.strip()
            if key and key.replace("_", "").isalnum():
                fields[key] = value.strip()
    source_id = fields.get("SOURCE_ID", "")
    require_source_id(source_id)
    if path.name != f"{source_id}.txt":
        raise ValueError(f"檔名 {path.name} 與 SOURCE_ID {source_id} 不一致")
    return SourceDoc(
        source_id=source_id,
        path=path,
        data=data,
        text=text,
        fields=fields,
        verbatims=tuple(verbatims),
    )


def load_sourcepack(source_root: Path) -> dict[str, SourceDoc]:
    """source_root 是 sourcepack 目錄，來源檔在其 sources/ 底下。"""
    sources_dir = source_root / "sources"
    if not sources_dir.is_dir():
        raise FileNotFoundError(f"找不到來源目錄：{sources_dir}")
    docs: dict[str, SourceDoc] = {}
    for entry in sorted(sources_dir.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.suffix != ".txt":
            continue
        resolved = resolve_inside(sources_dir, Path(entry.name))
        data = resolved.read_bytes()
        doc = _parse(resolved, data)
        if doc.source_id in docs:
            raise ValueError(f"重複的 SOURCE_ID：{doc.source_id}")
        docs[doc.source_id] = doc
    if not docs:
        raise ValueError("來源包是空的")
    return docs
