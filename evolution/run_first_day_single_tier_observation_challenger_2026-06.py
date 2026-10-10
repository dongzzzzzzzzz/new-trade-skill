#!/usr/bin/env python3
"""Keep a first-day single-tier theme as observation on 2026-06-15."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_current_skill_tday_queue_2026-06.jsonl"
OUTPUT = ROOT / "replay_challenger_first_day_single_tier_2026-06.jsonl"


def main() -> None:
    records = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for item in records:
        if item["signal_date"] != "2026-06-15":
            continue
        item["market_mode"] = "油运新题材观察"
        item["market_mode_evidence"] = {
            "theme": "原油/成品油运输/航运",
            "source": "T-day facts only; all responses are first boards without a prior leader or cross-tier ladder",
        }
        item["theme_classification"] = [
            {
                "theme": "原油/成品油运输/航运",
                "status": "新题材观察",
                "evidence": "三只独立首板形成同日响应，但没有先行核心或跨梯队结构",
            }
        ]
        for node in item["node_role_records"]:
            node["role"] = "新题材观察"
            node["main_node"] = "首日单梯队，节点未确认"
            node["risk"] = "全部为首板，未形成跨日或跨梯队主线，不进入正式队列"
        for audit in item["candidate_audit"]:
            audit["theme_pass"] = False
            audit["node_pass"] = False
            audit["include_status"] = "watch"
            audit["include_or_exclude_reason"] = "首日只有单一首板梯队，保留观察但不生成正式队列"
        item["original_queue"] = []
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "not_executed"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "首日单梯队新题材只观察，不交易"
        item["replay_status"] = "challenger_upstream_observation_pending_auction"
        item["challenger_id"] = "first_day_single_tier_observation_v1"
        item["regenerated_from"] = "current_skill_june_tday_queue"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
