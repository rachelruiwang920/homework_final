"""確定性腳本政策。

Thought 字串是程式裡的固定模板，用來保留 ReAct 的
Thought → Action → Observation 外形。它們不是模型生成。
政策只看檢索排序與錨點有沒有出現在已讀文字裡，不看來源代號表。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


THOUGHT_SEARCH = (
    "【腳本模板，非模型輸出】任務契約有多個必須被逐字摘錄覆蓋的證據槽。"
    "先檢索自建來源包，看哪些檔案含有這些錨點片語。"
)
THOUGHT_READ = (
    "【腳本模板，非模型輸出】仍有證據槽的錨點沒有在已讀文字中出現。"
    "依檢索排序讀取下一個尚未讀過的候選。"
)
THOUGHT_WRITE = (
    "【腳本模板，非模型輸出】每一個證據槽的錨點都已在讀取結果中出現。"
    "依照來源檔上的原文區間組裝簡報，不補寫沒讀到的引文。"
)
THOUGHT_STOP = (
    "【腳本模板，非模型輸出】沒有尚未讀過的候選，或簡報已經寫入。停止。"
)


@dataclass
class Decision:
    tool: str
    args: dict[str, Any]
    thought: str


@dataclass
class AgentState:
    searched: bool = False
    hits: list[dict[str, Any]] = field(default_factory=list)
    reads: list[dict[str, Any]] = field(default_factory=list)
    written: bool = False


def observed_slot_ids(reads: list[dict[str, Any]], slots: list[dict[str, str]]) -> list[str]:
    chunks = [item.get("text", "") for item in reads if item.get("ok")]
    blob = "\n".join(chunks)
    return [slot["slot_id"] for slot in slots if slot["anchor"] in blob]


def decide(state: AgentState, contract: dict[str, Any]) -> Decision:
    slots = contract["required_slots"]
    if not state.searched:
        return Decision("search", {"phrases": list(contract["search_phrases"])}, THOUGHT_SEARCH)
    covered = observed_slot_ids(state.reads, slots)
    if len(covered) < len(slots):
        seen = {item["source_id"] for item in state.reads if item.get("ok")}
        unread = [hit for hit in state.hits if hit["source_id"] not in seen]
        if not unread:
            return Decision("stop", {"reason": "no_more_hits"}, THOUGHT_STOP)
        return Decision("read", {"source_id": unread[0]["source_id"]}, THOUGHT_READ)
    if not state.written:
        return Decision("write", {}, THOUGHT_WRITE)
    return Decision("stop", {"reason": "complete"}, THOUGHT_STOP)
