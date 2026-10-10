#!/usr/bin/env python3
"""Reclassify 2026-06-01 as repair after residual extreme loss effects."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_challenger_first_day_single_tier_2026-06.jsonl"
OUTPUT = ROOT / "replay_challenger_residual_extreme_loss_repair_2026-06.jsonl"


def main() -> None:
    records = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for item in records:
        if item["signal_date"] != "2026-06-01":
            continue
        item["environment_state"] = "修复"
        item["sentiment_state"] = "修复但负反馈未清"
        item["environment_evidence"]["previous_trade_day_down_ratio"] = 0.711716621253406
        item["environment_evidence"]["previous_trade_day_limit_down_count"] = 50
        item["environment_evidence"]["residual_limit_down_count"] = 21
        item["environment_evidence"]["classification_reason"] = (
            "前一交易日极端亏钱效应后广度反弹，但两大指数仍弱且跌停残留，最多判修复"
        )

        for node in item["node_role_records"]:
            if node["candidate"] == "000539.SZ":
                node["role"] = "高位核心观察"
                node["main_node"] = "修复日高位延续降级"
                node["risk"] = "极端负反馈后的首个修复日，高位延续不进入正式队列"
        for audit in item["candidate_audit"]:
            if audit["candidate"] == "000539.SZ":
                audit["environment_pass"] = False
                audit["include_status"] = "watch"
                audit["include_or_exclude_reason"] = "修复日高位延续降级为观察"
            else:
                audit["environment_evidence"] = "修复; 极端负反馈未清，只保留同题材低位前排"
                audit["include_status"] = "formal"
                audit["include_or_exclude_reason"] = "同题材低位前排通过修复日试错门"
        item["original_queue"] = ["002608.SZ", "000767.SZ"]
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "pending_auction"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "等待修复环境重生成后的低位队列接受T+1竞价验货"
        item["replay_status"] = "challenger_tday_queue_regenerated_pending_auction"
        item["challenger_id"] = "residual_extreme_loss_repair_v1"
        item["regenerated_from"] = "first_day_single_tier_june"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
