#!/usr/bin/env python3
"""Regenerate the 2026-04-21 queue using explicit catalyst overlap."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_current_skill_tday_queue_2026-04.jsonl"
OUTPUT = ROOT / "replay_challenger_theme_relation_2026-04.jsonl"


def main() -> None:
    records = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for item in records:
        if item["signal_date"] != "2026-04-21":
            continue
        for node in item["node_role_records"]:
            if node["candidate"] == "603178.SH":
                node["role"] = "跨题材低位观察"
                node["main_node"] = "关系不足"
                node["node_evidence"] = "T日原因只有低空经济，未与主线候选共享商业航天催化"
                node["risk"] = "不得因同一宽泛概念自动进入正式队列"
        for audit in item["candidate_audit"]:
            if audit["candidate"] == "603178.SH":
                audit["theme_pass"] = False
                audit["node_pass"] = False
                audit["include_status"] = "watch"
                audit["include_or_exclude_reason"] = "未共享主线的具体商业航天催化，退回观察池"
            elif audit["candidate"] == "603017.SH":
                audit["original_rank"] = 2
                audit["include_status"] = "formal"
                audit["include_or_exclude_reason"] = "与主线共享商业航天+低空经济具体催化关系"
        item["original_queue"] = ["002081.SZ", "603017.SH"]
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "pending_auction"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "等待关系重生成后的队列接受T+1竞价验货"
        item["replay_status"] = "challenger_tday_queue_regenerated_pending_auction"
        item["challenger_id"] = "theme_relation_candidate_v1"
        item["regenerated_from"] = "current_skill_april_tday_queue"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
