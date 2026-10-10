#!/usr/bin/env python3
"""Regenerate March queues for the dual-divergence high-to-low Challenger."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "replay_current_skill_tday_queue_2026-03.jsonl"
OUTPUT = ROOT / "replay_challenger_dual_divergence_high_low_2026-03.jsonl"


def main() -> None:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in records:
        item["challenger_id"] = "dual_divergence_high_low_v1"
        item["regenerated_from"] = "current_skill_march_tday_queue"
        if item["signal_date"] != "2026-03-30":
            continue
        for audit in item["candidate_audit"]:
            if audit["candidate"] == "603538.SH":
                audit.update(
                    {
                        "original_rank": None,
                        "node_pass": False,
                        "risk_pass": False,
                        "role": "非市场核心高位延续",
                        "include_status": "watch",
                        "include_or_exclude_reason": "环境与接力情绪双分歧，同题材存在2板主动前排，高位降为观察",
                    }
                )
            elif audit["candidate"] in {"002038.SZ", "600488.SH"}:
                audit["original_rank"] = 1 if audit["candidate"] == "002038.SZ" else 2
                audit["role"] = "同题材低位前排"
                audit["include_status"] = "formal"
                audit["include_or_exclude_reason"] = "双分歧下由同题材低位主动前排重新生成正式队列"
        item["original_queue"] = ["002038.SZ", "600488.SH"]
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "pending_auction"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "等待重新生成后的低位队列接受T+1竞价验货"
        item["replay_status"] = "challenger_tday_queue_regenerated_pending_auction"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
