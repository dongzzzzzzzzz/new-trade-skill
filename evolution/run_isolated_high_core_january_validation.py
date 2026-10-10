#!/usr/bin/env python3
"""Apply the isolated-high-core rule to the complete January baseline."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "replay_challenger_isolated_high_core_2026-01.jsonl"
DECISIONS = ROOT / "challenger_decisions_isolated_high_core_2026-01.csv"


def load_records() -> list[dict]:
    rows = []
    for path in sorted(ROOT.glob("replay_baseline_2026-01*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return sorted(rows, key=lambda item: item["signal_date"])


def isolated_high_core(item: dict) -> bool:
    if item.get("environment_state") != "分歧" or not item.get("original_queue"):
        return False
    head = item["original_queue"][0]
    node = next((row for row in item.get("node_role_records", []) if row.get("candidate") == head), {})
    if node.get("role") == "市场核心" and float(node.get("board_count", 0) or 0) >= 7:
        return False
    evidence = " ".join(
        str(value)
        for value in [node.get("node_evidence", ""), node.get("risk", "")]
    )
    if any(
        marker in " ".join(str(row.get("evidence", "")) for row in item.get("theme_classification", []))
        for marker in ("梯队", "响应", "扩散")
    ):
        return False
    # T-day response evidence already frozen in the baseline. A response or
    # ladder mention means this rule does not trigger.
    response_markers = ("梯队", "响应", "扩散", "承接", "同题材")
    return not any(marker in evidence for marker in response_markers)


def main() -> None:
    records = load_records()
    triggered = []
    for item in records:
        item["challenger_id"] = "isolated_high_core_lock_v1"
        item["regenerated_from"] = "current_skill_january_baseline"
        if not isolated_high_core(item):
            continue
        triggered.append(item["signal_date"])
        item["original_queue"] = []
        item["auction_records"] = []
        item["executed_candidate"] = ""
        item["executed"] = False
        item["execution_status"] = "not_executed"
        item["t1_open_buy_price"] = None
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["replay_status"] = "challenger_tday_queue_regenerated_wait"
        item["invalidated_reason"] = "分歧环境下T日孤立高位延续锁定"

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    canonical = {}
    with (ROOT / "baseline_decisions_2026-01.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canonical[row["signal_date"]] = row
    rows = []
    for item in records:
        rows.append(
            canonical.get(
                item["signal_date"],
                {
                    "signal_date": item["signal_date"],
                    "candidate": "",
                    "code": "",
                    "executed": "false",
                    "execution_status": "not_executed",
                },
            )
        )
    for row in rows:
        if row["signal_date"] in triggered:
            row["code"] = ""
            row["candidate"] = ""
            row["executed"] = "false"
            row["execution_status"] = "not_executed"
    with DECISIONS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({"records": len(records), "triggered_dates": triggered}, ensure_ascii=False))


if __name__ == "__main__":
    main()
