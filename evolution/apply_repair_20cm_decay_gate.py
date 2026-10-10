#!/usr/bin/env python3
"""Apply the repair-day 20cm/30cm auction-decay Challenger to a replay."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def is_large_limit(code: str) -> bool:
    return code.split(".", 1)[0].startswith(("300", "301", "688", "689"))


def hits_gate(item: dict, record: dict, rank: int) -> bool:
    audits = {row.get("candidate"): row for row in item.get("candidate_audit", [])}
    candidate = record.get("candidate", "")
    gap = record.get("open_gap_pct")
    drift = record.get("auction_drift_pct")
    return (
        item.get("environment_state") == "修复"
        and audits.get(candidate, {}).get("role") != "市场核心"
        and is_large_limit(candidate)
        and rank <= 2
        and gap is not None
        and float(gap) >= 5.0
        and drift is not None
        and float(drift) <= -3.0
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    decisions = []
    for item in records:
        selected = ""
        selected_record = None
        for rank, record in enumerate(item.get("auction_records", []), 1):
            if record.get("decision") not in {"保留并执行", "保留为递补"}:
                continue
            if hits_gate(item, record, rank):
                record["repair_20cm_auction_decay"] = True
                record["decision"] = "跳过并递补"
                record["reason"] = (
                    "修复环境中非市场核心20cm或30cm前排高开后竞价回落至少3%，"
                    "按高预期塌缩处理"
                )
                continue
            selected = record.get("candidate", "")
            selected_record = record
            break

        item["repair_20cm_gate_applied"] = True
        item["executed_candidate"] = selected
        item["executed"] = bool(selected)
        item["execution_status"] = (
            "selected_pending_t2_auction" if selected else "not_executed"
        )
        item["replay_status"] = (
            "auction_confirmed_pending_t2_return_auction"
            if selected
            else "auction_rejected_or_missing"
        )
        item["t1_open_buy_price"] = (
            selected_record.get("t1_open") if selected_record else None
        )
        if not selected:
            item["invalidated_reason"] = "20cm竞价塌缩门后没有合格且可参与候选"
        for record in item.get("auction_records", []):
            if record.get("candidate") == selected:
                record["decision"] = "保留并执行"
            elif record.get("decision") == "保留并执行":
                record["decision"] = "保留为递补"

        decisions.append(
            {
                "signal_date": item.get("signal_date", ""),
                "candidate": next(
                    (
                        row.get("name", "")
                        for row in item.get("candidate_audit", [])
                        if row.get("candidate") == selected
                    ),
                    "",
                ),
                "code": selected,
                "executed": str(bool(selected)).lower(),
                "execution_status": item["execution_status"],
            }
        )

    args.output.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in records)
        + "\n",
        encoding="utf-8",
    )
    with args.decisions.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decisions[0]))
        writer.writeheader()
        writer.writerows(decisions)


if __name__ == "__main__":
    main()
