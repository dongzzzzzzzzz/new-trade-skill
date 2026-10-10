#!/usr/bin/env python3
"""Regenerate May queues using specific mainline relation evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_current_skill_tday_queue_2026-05.jsonl"
OUTPUT = ROOT / "replay_challenger_may_specific_relation_2026-05.jsonl"


def main() -> None:
    records = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for item in records:
        date = item["signal_date"]
        if date == "2026-05-07":
            # 603158 has the most direct liquid-cooling evidence; 600673 is
            # retained as a related candidate, while broad compute follows.
            new_queue = ["603158.SH", "600673.SH", "000818.SZ"]
            reason = "液冷服务器与热管理是当前主线的直接关系，优先于混合催化"
        elif date == "2026-05-08":
            # 002491 directly joins optical-fiber price/communications and
            # data-center demand; the other two are broader compute labels.
            new_queue = ["002491.SZ", "002929.SZ", "603636.SH"]
            reason = "光纤涨价、通信电缆与数据中心是当前主线的直接关系"
        elif date == "2026-05-19":
            # 300657 is compute-related but has no direct liquid-cooling
            # evidence, so it remains observation-only and cannot be a
            # recursive fallback after the direct candidates are locked.
            new_queue = ["002421.SZ", "002272.SZ"]
            reason = "300657.SZ只有泛算力关系，不能作为液冷主线正式递补"
        else:
            continue

        by_code = {row["candidate"]: row for row in item["candidate_audit"]}
        by_node = {row["candidate"]: row for row in item["node_role_records"]}
        for rank, code in enumerate(new_queue, 1):
            by_code[code]["original_rank"] = rank
            by_code[code]["include_status"] = "formal"
            by_code[code]["include_or_exclude_reason"] = reason
        if date == "2026-05-19":
            audit = by_code["300657.SZ"]
            audit["theme_pass"] = False
            audit["node_pass"] = False
            audit["include_status"] = "watch"
            audit["include_or_exclude_reason"] = reason
            node = by_node["300657.SZ"]
            node["role"] = "题材跟随观察"
            node["main_node"] = "关系不足"
            node["risk"] = reason

        item["original_queue"] = new_queue
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "pending_auction"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["invalidated_reason"] = "等待具体关系重生成后的队列接受T+1竞价验货"
        item["replay_status"] = "challenger_tday_queue_regenerated_pending_auction"
        item["challenger_id"] = "may_specific_relation_candidate_v1"
        item["regenerated_from"] = "current_skill_may_tday_queue"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
