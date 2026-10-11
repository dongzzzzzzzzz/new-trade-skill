#!/usr/bin/env python3
"""Apply the user's hard main-board trading universe before auction replay.

This transformation preserves the frozen order of every remaining candidate.
It is deliberately upstream of auction facts and return computation: a
non-main-board symbol is excluded from the candidate pool, not merely skipped
at execution time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MAINBOARD_PREFIXES = ("000", "001", "002", "003", "600", "601", "603", "605")


def is_mainboard_tradeable(code: str) -> bool:
    return str(code).split(".", 1)[0].startswith(MAINBOARD_PREFIXES)


def filter_record(item: dict) -> dict:
    original = list(item.get("original_queue") or [])
    kept = [code for code in original if is_mainboard_tradeable(code)]
    removed = [code for code in original if not is_mainboard_tradeable(code)]

    audits = item.get("candidate_audit") or []
    audit_by_code = {row.get("candidate"): row for row in audits}
    for code in removed:
        row = dict(audit_by_code.get(code) or {"candidate": code})
        row["include_status"] = "excluded"
        row["mainboard_tradeable"] = False
        row["include_or_exclude_reason"] = (
            "用户只能买主板股票；在候选池生成前排除，不能进入观察池、原始队列或收益统计"
        )
        row["exclusion_step"] = "个人可交易范围硬门"
        audit_by_code[code] = row

    filtered_audits = []
    for row in audits:
        code = row.get("candidate")
        if code in kept:
            row = dict(row)
            row["mainboard_tradeable"] = True
            filtered_audits.append(row)
        elif code in removed:
            filtered_audits.append(audit_by_code[code])
    for code in removed:
        if code not in {row.get("candidate") for row in filtered_audits}:
            filtered_audits.append(audit_by_code[code])

    item = dict(item)
    item["original_queue_before_mainboard_filter"] = original
    item["original_queue"] = kept
    item["candidate_audit"] = filtered_audits
    item["node_role_records"] = [
        row for row in (item.get("node_role_records") or [])
        if is_mainboard_tradeable(row.get("candidate", ""))
    ]
    item["excluded_candidates"] = list(item.get("excluded_candidates") or []) + [
        {
            "candidate": code,
            "step": "个人可交易范围硬门",
            "reason": "非主板股票不可交易",
        }
        for code in removed
    ]
    item["mainboard_filter"] = {
        "applied_before_auction": True,
        "allowed_prefixes": list(MAINBOARD_PREFIXES),
        "removed": removed,
        "kept_order_preserved": True,
    }
    if removed and not kept:
        item["invalidated_reason"] = "原始候选均不属于用户可交易的主板范围"
    return item


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = [
        filter_record(json.loads(line))
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
