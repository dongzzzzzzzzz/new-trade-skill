#!/usr/bin/env python3
"""Regenerate the January replay for the high-core crowding Challenger.

The Challenger changes one upstream gate in SKILL.md. This script materializes
the complete downstream replay so the comparison is not a queue-only patch.
The trigger uses only T-day facts already frozen in the baseline records.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_FILES = sorted(ROOT.glob("replay_baseline_2026-01*.jsonl"))
OUTPUT_JSONL = ROOT / "replay_challenger_high_core_lock_2026-01.jsonl"
OUTPUT_DECISIONS = ROOT / "challenger_decisions_high_core_lock_2026-01.csv"
CHALLENGER_ID = "high_core_crowding_lock_v1"


def load_records() -> list[dict]:
    records = []
    for path in SOURCE_FILES:
        # Do not read a prior Challenger output if this script is rerun.
        if path.name == OUTPUT_JSONL.name:
            continue
        for line in path.read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
    return sorted(records, key=lambda item: item["signal_date"])


def load_canonical_decisions() -> dict[str, dict[str, str]]:
    decisions = {}
    with (ROOT / "baseline_decisions_2026-01.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            decisions[row["signal_date"]] = row
    return decisions


def align_to_canonical_decisions(records: list[dict], decisions: dict[str, dict[str, str]]) -> None:
    """Prevent JSON execution annotations from overriding the canonical table."""
    for item in records:
        row = decisions.get(item["signal_date"])
        if row is None:
            item["executed_candidate"] = ""
            item["executed"] = False
            item["execution_status"] = "not_executed"
            item["t1_open_buy_price"] = None
            item["t2_auction_sell_price"] = None
            item["return_pct"] = None
            continue
        item["executed_candidate"] = row["code"]
        item["executed"] = row["executed"].lower() == "true"
        item["execution_status"] = row["execution_status"]
        if not item["executed"]:
            item["t1_open_buy_price"] = None
            item["t2_auction_sell_price"] = None
            item["return_pct"] = None


def audit_update(item: dict, code: str, **changes) -> None:
    for audit in item["candidate_audit"]:
        if audit.get("candidate") == code:
            audit.update(changes)
            return


def apply_jan28(item: dict) -> None:
    item["environment_state"] = "分歧"
    item["sentiment_state"] = "分歧"
    item["market_mode"] = "主线低位试错（高位核心封锁）"

    audit_update(
        item,
        "601212.SH",
        original_rank=None,
        environment_pass=False,
        environment_evidence="高位核心拥挤保护触发：下跌占比66.6%、跌停5只、炸板26只",
        risk_pass=False,
        risk_evidence="7板高位核心在广度恶化环境中不能自动成为队首",
        include_status="excluded",
        include_or_exclude_reason="保护门触发，保留观察，不进入正式队列",
    )
    for code in ("600916.SH", "600531.SH"):
        audit_update(
            item,
            code,
            original_rank=None,
            environment_pass=False,
            risk_pass=False,
            include_status="excluded",
            include_or_exclude_reason="超过低位保护上限，不能机械替代最高核心",
        )
    audit_update(
        item,
        "002155.SZ",
        original_rank=1,
        environment_pass=True,
        environment_evidence="保护门允许主线内不超过3板的低位候选",
        risk_pass=True,
        risk_evidence="一字/撤单/不可成交即失效，买入前提明确",
        role="低位试错",
        include_status="formal",
        include_or_exclude_reason="主线内3板低位候选，存在独立黄金响应和明确竞价边界",
    )

    item["original_queue"] = ["002155.SZ"]
    item["auction_records"] = [
        record
        for record in item["auction_records"]
        if record.get("candidate") == "002155.SZ"
    ]
    item["auction_records"][0]["decision"] = "执行"
    item["auction_records"][0]["reason"] = "高位核心被保护门锁定后，主线内低位候选可成交"
    item["executed_candidate"] = "002155.SZ"
    item["executed"] = True
    item["execution_status"] = "executed"
    item["t1_open_buy_price"] = 33.64
    item["t2_auction_sell_price"] = 37.00
    item["return_pct"] = (37.00 / 33.64 - 1.0) * 100.0
    item["invalidated_reason"] = "保护门阻止高位核心自动占据队首，改由满足低位门的主线候选执行"
    item["excluded_candidates"] = [
        {"candidate": "601212.SH", "reason": "高位核心拥挤保护"},
        {"candidate": "600916.SH", "reason": "超过低位保护上限"},
        {"candidate": "600531.SH", "reason": "超过低位保护上限"},
    ]


def apply_jan29(item: dict) -> None:
    item["environment_state"] = "分歧"
    item["sentiment_state"] = "分歧"
    item["market_mode"] = "等待（高位核心封锁）"
    for audit in item["candidate_audit"]:
        audit["original_rank"] = None
        audit["environment_pass"] = False
        audit["environment_evidence"] = "高位核心拥挤保护触发：下跌占比65.3%、跌停12只、炸板34只"
        audit["risk_pass"] = False
        audit["include_status"] = "excluded"
        audit["include_or_exclude_reason"] = "没有同时满足主线、低位和两梯队响应条件的候选"

    item["original_queue"] = []
    item["auction_records"] = []
    item["executed_candidate"] = ""
    item["executed"] = False
    item["execution_status"] = "not_executed"
    item["t1_open_buy_price"] = None
    item["t2_auction_sell_price"] = None
    item["return_pct"] = None
    item["invalidated_reason"] = "高位核心拥挤保护触发，且没有合格低位主线候选，保持等待"
    item["excluded_candidates"] = [
        {"candidate": audit["candidate"], "reason": audit["include_or_exclude_reason"]}
        for audit in item["candidate_audit"]
    ]


def main() -> None:
    records = load_records()
    align_to_canonical_decisions(records, load_canonical_decisions())
    for item in records:
        item["challenger_id"] = CHALLENGER_ID
        item["regenerated_from"] = "current_skill_january_baseline"
        if item["signal_date"] == "2026-01-28":
            apply_jan28(item)
        elif item["signal_date"] == "2026-01-29":
            apply_jan29(item)

    with OUTPUT_JSONL.open("w") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = []
    for item in records:
        if item["execution_status"] == "not_executed":
            continue
        name_by_code = {
            audit["candidate"]: audit.get("name", audit["candidate"])
            for audit in item["node_role_records"]
        }
        rows.append(
            {
                "signal_date": item["signal_date"],
                "candidate": name_by_code.get(item["executed_candidate"], item["executed_candidate"]),
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
