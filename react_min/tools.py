"""三個離線工具：search、read、write。

search 對來源檔做整段錨點的子字串計數，再用英文 token 交集打破平手。
read 只接受來源代號，不接受路徑。
write 只會把 final-brief.md 寫進指定輸出目錄，而且只引用已讀檔案裡的 VERBATIM 行。
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from react_min.pack import SourceDoc
from react_min.policy import observed_slot_ids
from react_min.security import PathEscape, require_source_id, resolve_inside


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z0-9]+", text) if len(token) >= 3}


def search_sources(docs: dict[str, SourceDoc], phrases: list[str]) -> dict[str, Any]:
    if not phrases:
        raise ValueError("檢索片語不可為空")
    query_tokens = tokenize(" ".join(phrases))
    results = []
    for source_id in sorted(docs):
        doc = docs[source_id]
        matched = [phrase for phrase in phrases if phrase in doc.text]
        overlap = len(query_tokens & tokenize(doc.text))
        results.append(
            {
                "source_id": source_id,
                "phrase_hits": len(matched),
                "matched_phrases": matched,
                "token_overlap": overlap,
                "title": doc.fields.get("TITLE", ""),
            }
        )
    results.sort(key=lambda row: (-row["phrase_hits"], -row["token_overlap"], row["source_id"]))
    return {
        "ok": True,
        "tool": "search",
        "mechanism": "substring_phrase_v1",
        "phrases": list(phrases),
        "results": results,
    }


def read_source(docs: dict[str, SourceDoc], source_id: str) -> dict[str, Any]:
    try:
        require_source_id(source_id)
    except PathEscape as exc:
        return {"ok": False, "tool": "read", "error": "path_rejected", "detail": str(exc)}
    doc = docs.get(source_id)
    if doc is None:
        return {"ok": False, "tool": "read", "error": "unknown_source", "source_id": source_id}
    digest = hashlib.sha256(doc.data).hexdigest()
    return {
        "ok": True,
        "tool": "read",
        "source_id": source_id,
        "sha256": digest,
        "n_bytes": len(doc.data),
        "text": doc.text,
        "verbatim_keys": [item.key for item in doc.verbatims],
    }


def _citation(doc: SourceDoc, quote: str) -> str:
    blob = quote.encode("utf-8")
    start = doc.data.find(blob)
    end = start + len(blob)
    if start < 0 or doc.data[start:end] != blob or doc.data.find(blob, start + 1) != -1:
        raise ValueError(f"{doc.source_id} 的引文無法對到唯一區間")
    digest = hashlib.sha256(blob).hexdigest()
    return (
        f":::citation source={doc.source_id} start={start} end={end} sha256={digest}\n"
        f"{quote}\n"
        f":::\n"
    )


def render_brief(docs: dict[str, SourceDoc], reads: list[dict[str, Any]], contract: dict[str, Any]) -> str:
    slots = contract["required_slots"]
    covered = observed_slot_ids(reads, slots)
    if covered != [slot["slot_id"] for slot in slots]:
        missing = [slot["slot_id"] for slot in slots if slot["slot_id"] not in covered]
        raise ValueError("證據槽尚未齊，拒絕寫入：" + ",".join(missing))
    by_id = {item["source_id"]: item for item in reads if item.get("ok")}
    templates = contract["paraphrase_templates"]
    blocks: list[str] = []
    prose: list[str] = []
    for slot in slots:
        anchor = slot["anchor"]
        holders = [source_id for source_id, item in by_id.items() if anchor in item.get("text", "")]
        if len(holders) != 1:
            raise ValueError(f"{slot['slot_id']} 的錨點必須恰好落在一份已讀來源")
        doc = docs[holders[0]]
        matches = [item for item in doc.verbatims if anchor in item.text]
        if len(matches) != 1:
            raise ValueError(f"{slot['slot_id']} 的錨點必須恰好落在一條 VERBATIM")
        blocks.append(_citation(doc, matches[0].text))
        prose.append("【自撰轉述】" + templates[slot["slot_id"]].strip())
    question = contract["question"].strip()
    body = [
        "# 證據簡報",
        "",
        "標示：這份簡報由確定性腳本控制器把工具觀察組裝而成，不是語言模型輸出。"
        "來源是依使用者指示自行選定的論文摘錄，屬於自建替代，不是教師夾具。"
        "未宣稱通過教師驗證器。",
        "",
        "## 問題",
        "",
        question,
        "",
        "## 自撰轉述",
        "",
        *prose,
        "",
        "【自撰轉述】三段摘錄把「行動」放在不同層：第一段在同一次生成裡與推理交錯，"
        "第二段由經過訓練的模型在預測後續 token 時決定 API 呼叫，第三段把代理在多個環境裡的行動當成評測對象。"
        "這三句是組裝時加上的對照，不是論文原句。",
        "",
        "## 逐字引用",
        "",
        *blocks,
        "## 區間約定",
        "",
        "start 與 end 是來源檔 UTF-8 位元組偏移，半開區間。sha256 是該位元組區間的 SHA-256。",
        "上面的【自撰轉述】不是引文，驗證器不把它當成證據。",
        "",
    ]
    return "\n".join(body)


def write_brief(
    docs: dict[str, SourceDoc],
    reads: list[dict[str, Any]],
    contract: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    try:
        text = render_brief(docs, reads, contract)
    except ValueError as exc:
        return {"ok": False, "tool": "write", "error": "refused", "detail": str(exc)}
    destination = resolve_inside(out_dir, Path("final-brief.md"))
    payload = text.encode("utf-8")
    destination.write_bytes(payload)
    return {
        "ok": True,
        "tool": "write",
        "path": "final-brief.md",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "n_bytes": len(payload),
    }
