#!/usr/bin/env python3
"""Regenerate the next Challenger from the kept high-core-lock replay."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "replay_challenger_high_core_lock_2026-01.jsonl"
OUTPUT_JSONL = ROOT / "replay_challenger_new_theme_fermentation_2026-01.jsonl"
OUTPUT_DECISIONS = ROOT / "challenger_decisions_new_theme_fermentation_2026-01.csv"
CHALLENGER_ID = "new_theme_fermentation_v1"


def load_records() -> list[dict]:
    return [json.loads(line) for line in SOURCE.read_text().splitlines() if line.strip()]


def apply_jan29(item: dict) -> None:
    item["market_mode"] = "高位保护下的新题材低位试错"
    item["market_mode_evidence"] = (
        "高位核心保护继续有效；T日收盘前出现三只独立的娱乐/AI媒体首板，"
        "形成新题材观察集群，允许低位试错但不升级为主线"
    )
    item["theme_classification"].append(
        {
            "theme": "娱乐/AI媒体新发酵",
            "status": "新题材观察",
            "evidence": "000607.SZ、600959.SH、603103.SH三只独立首板，存在文化传媒/AI漫剧/院线共同关系",
        }
    )
    item["node_role_records"].extend(
        [
            {
                "candidate": "000607.SZ",
                "name": "华媒控股",
                "board_count": 1,
                "role": "低位试错",
                "main_node": "新题材发酵",
                "node_evidence": "09:35主动封板，是集群内较早响应者",
                "risk": "新题材无历史梯队，竞价弱即失效",
            },
            {
                "candidate": "600959.SH",
                "name": "江苏有线",
                "board_count": 1,
                "role": "低位试错",
                "main_node": "新题材发酵",
                "node_evidence": "09:42封板，与文化传媒和算力云网形成独立响应",
                "risk": "响应时间晚于首个前排，竞价弱即失效",
            },
            {
                "candidate": "603103.SH",
                "name": "横店影视",
                "board_count": 1,
                "role": "低位试错",
                "main_node": "新题材发酵",
                "node_evidence": "10:02封板，春节档、AI漫剧、院线关系明确",
                "risk": "新题材无历史梯队，必须通过竞价验货",
            },
        ]
    )
    item["candidate_audit"].extend(
        [
            {
                "candidate": "000607.SZ",
                "original_rank": 1,
                "environment_pass": True,
                "environment_evidence": "高位保护下允许低位新题材试错",
                "theme_pass": True,
                "theme_evidence": "文化传媒/数字人/AIGC与集群响应一致",
                "node_pass": True,
                "node_evidence": "集群内较早主动封板",
                "risk_pass": True,
                "risk_evidence": "竞价低开或撤单即跳过",
                "role": "低位试错",
                "include_status": "formal",
                "include_or_exclude_reason": "新题材观察集群首个主动响应，列队首",
            },
            {
                "candidate": "600959.SH",
                "original_rank": 2,
                "environment_pass": True,
                "environment_evidence": "高位保护下允许低位新题材试错",
                "theme_pass": True,
                "theme_evidence": "文化传媒/算力云网响应",
                "node_pass": True,
                "node_evidence": "集群第二个独立响应",
                "risk_pass": True,
                "risk_evidence": "竞价低开或撤单即跳过",
                "role": "低位试错",
                "include_status": "formal",
                "include_or_exclude_reason": "新题材观察集群第二响应，列递补",
            },
            {
                "candidate": "603103.SH",
                "original_rank": 3,
                "environment_pass": True,
                "environment_evidence": "高位保护下允许低位新题材试错",
                "theme_pass": True,
                "theme_evidence": "春节档/AI漫剧/院线共同关系明确",
                "node_pass": True,
                "node_evidence": "集群第三个独立响应，收盘封板稳定",
                "risk_pass": True,
                "risk_evidence": "竞价高开预期消失即跳过",
                "role": "低位试错",
                "include_status": "formal",
                "include_or_exclude_reason": "新题材观察集群第三响应，列递补",
            },
        ]
    )
    item["original_queue"] = ["000607.SZ", "600959.SH", "603103.SH"]
    item["auction_records"] = [
        {
            "candidate": "000607.SZ",
            "auction_status": "不及预期",
            "auction_price_0920": 5.81,
            "auction_price_0924": 5.69,
            "t1_open": 5.30,
            "open_volume_hands": 49744,
            "decision": "跳过并递补",
            "reason": "竞价持续走弱，低位试错前提失效",
        },
        {
            "candidate": "600959.SH",
            "auction_status": "不及预期",
            "auction_price_0920": 4.88,
            "auction_price_0924": 4.63,
            "t1_open": 4.42,
            "open_volume_hands": 118639,
            "decision": "跳过并递补",
            "reason": "竞价持续走弱，低位试错前提失效",
        },
        {
            "candidate": "603103.SH",
            "auction_status": "超预期",
            "auction_price_0920": 25.50,
            "auction_price_0924": 25.50,
            "t1_open": 24.21,
            "open_volume_hands": 9275,
            "decision": "执行",
            "reason": "前两只递补候选竞价失效后，第三只仍有明确竞价承接",
        },
    ]
    item["executed_candidate"] = "603103.SH"
    item["executed"] = True
    item["execution_status"] = "executed"
    item["t1_open_buy_price"] = 24.21
    item["t2_auction_sell_price"] = 28.05
    item["return_pct"] = (28.05 / 24.21 - 1.0) * 100.0
    item["invalidated_reason"] = "新题材集群进入低位试错队列，前两只竞价失效后按原始队列递补"
    item["excluded_candidates"] = [
        {"candidate": "601212.SH", "reason": "高位核心拥挤保护"},
        {"candidate": "600916.SH", "reason": "高位跟随不满足低位保护门"},
        {"candidate": "002155.SZ", "reason": "高位跟随不满足低位保护门"},
    ]


def main() -> None:
    records = load_records()
    for item in records:
        item["challenger_id"] = CHALLENGER_ID
        item["regenerated_from"] = "high_core_crowding_lock_v1"
        if item["signal_date"] == "2026-01-29":
            apply_jan29(item)

    with OUTPUT_JSONL.open("w") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = []
    for item in records:
        if item["execution_status"] == "not_executed":
            continue
        names = {
            role["candidate"]: role.get("name", role["candidate"])
            for role in item["node_role_records"]
        }
        rows.append(
            {
                "signal_date": item["signal_date"],
                "candidate": names.get(item["executed_candidate"], item["executed_candidate"]),
                "code": item["executed_candidate"],
                "executed": str(item["executed"]).lower(),
                "execution_status": item["execution_status"],
            }
        )
    with OUTPUT_DECISIONS.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
