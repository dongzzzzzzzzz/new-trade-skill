#!/usr/bin/env python3
"""Regenerate 2026-04-29 as wait when no coherent catalyst cluster exists."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_challenger_theme_relation_auction_2026-04.jsonl"
OUTPUT = ROOT / "replay_challenger_unrelated_cluster_wait_2026-04.jsonl"


def main() -> None:
    records = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for item in records:
        if item["signal_date"] != "2026-04-29":
            continue
        item["market_mode"] = "等待，未确认可持续主线"
        item["market_mode_evidence"] = {
            "theme": "",
            "source": "T-day facts only; candidates lack a shared catalyst cluster",
        }
        item["theme_classification"] = [
            {
                "theme": "",
                "status": "无正式主线",
                "evidence": "黄金供应链、AI纺织设备、液冷储能三组原因没有共同具体催化",
            }
        ]
        for node in item["node_role_records"]:
            node["role"] = "独立异动观察"
            node["main_node"] = "关系不足"
            node["risk"] = "不同催化不能拼成一条主线，不进入正式队列"
        for audit in item["candidate_audit"]:
            audit["theme_pass"] = False
            audit["node_pass"] = False
            audit["include_status"] = "watch"
            audit["include_or_exclude_reason"] = "候选之间没有共同具体催化，退回观察池"
        item["original_queue"] = []
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "not_executed"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "无共同具体催化的正式主线，等待"
        item["replay_status"] = "challenger_upstream_wait_pending_auction"
        item["challenger_id"] = "unrelated_cluster_wait_v1"
        item["regenerated_from"] = "theme_relation_candidate_april"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
