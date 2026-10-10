#!/usr/bin/env python3
"""Regenerate the February chain for the isolated-high-core Challenger."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "replay_current_skill_tday_queue_2026-02.jsonl"
OUTPUT = ROOT / "replay_challenger_isolated_high_core_2026-02.jsonl"
DECISIONS = ROOT / "challenger_decisions_isolated_high_core_2026-02.csv"


def main() -> None:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in records:
        item["challenger_id"] = "isolated_high_core_lock_v1"
        item["regenerated_from"] = "current_skill_february_tday_queue"
        if item["signal_date"] != "2026-02-04":
            continue
        item["environment_state"] = "分歧"
        item["sentiment_state"] = "强化但指数分化"
        item["market_mode"] = "收缩中的连板接力"
        for audit in item.get("candidate_audit", []):
            if audit.get("candidate") == "002830.SZ":
                audit.update(
                    {
                        "environment_pass": False,
                        "theme_pass": False,
                        "node_pass": False,
                        "risk_pass": False,
                        "role": "孤立高位延续",
                        "include_status": "watch",
                        "include_or_exclude_reason": "分歧环境下T日没有同题材或相邻梯队主动响应，降为观察",
                    }
                )
        item["original_queue"] = []
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "not_executed"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "分歧环境下孤立高位延续锁定，未生成合格正式候选"
        item["replay_status"] = "challenger_tday_queue_regenerated_wait"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = []
    for item in records:
        rows.append(
            {
                "signal_date": item["signal_date"],
                "candidate": "",
                "code": item.get("executed_candidate", ""),
                "executed": str(item.get("executed", False)).lower(),
                "execution_status": item.get("execution_status", "not_executed"),
            }
        )
    with DECISIONS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
