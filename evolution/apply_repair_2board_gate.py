#!/usr/bin/env python3
"""Apply the predeclared repair-day 2-board gate to a frozen auction replay.

The source replay is an already accepted upstream chain. This challenger only
changes the execution gate; it never changes the T-day queue order or uses T+2
returns to choose a candidate.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def hits_gate(item: dict, record: dict, rank: int) -> bool:
    roles = {
        row.get("candidate"): row
        for row in item.get("candidate_audit", [])
    }
    nodes = {
        row.get("candidate"): row
        for row in item.get("node_role_records", [])
    }
    candidate = record.get("candidate")
    audit = roles.get(candidate, {})
    node = nodes.get(candidate, {})
    gap = record.get("open_gap_pct")
    return (
        item.get("environment_state") == "修复"
        and audit.get("role") != "市场核心"
        and int(float(node.get("board_count", 0) or 0)) >= 2
        and rank <= 2
        and gap is not None
        and float(gap) >= 5.0
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
    decision_rows = []
    for item in records:
        selected = ""
        selected_record = None
        for rank, record in enumerate(item.get("auction_records", []), 1):
            if record.get("decision") not in {"保留并执行", "保留为递补"}:
                continue
            if hits_gate(item, record, rank):
                record["repair_2board_high_gap"] = True
                record["decision"] = "跳过并递补"
                record["reason"] = (
                    "修复环境中非市场核心2板以上且原始队列前两位高开至少5%，"
                    "按高位溢价过度处理"
                )
                continue
            selected = record.get("candidate", "")
            selected_record = record
            break

        item["repair_2board_gate_applied"] = True
        item["executed_candidate"] = selected
        item["executed"] = bool(selected)
        if selected_record is not None:
            item["t1_open_buy_price"] = selected_record.get("t1_open")
            item["execution_status"] = "selected_pending_t2_auction"
            item["replay_status"] = "auction_confirmed_pending_t2_return_auction"
        else:
            item["t1_open_buy_price"] = None
            item["execution_status"] = "not_executed"
            item["replay_status"] = "auction_rejected_or_missing"
            item["invalidated_reason"] = "2板修复高开门后没有合格且可参与候选"
        for record in item.get("auction_records", []):
            if record.get("candidate") == selected:
                record["decision"] = "保留并执行"
            elif record.get("decision") == "保留并执行":
                record["decision"] = "保留为递补"

        decision_rows.append(
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
        writer = csv.DictWriter(handle, fieldnames=list(decision_rows[0]))
        writer.writeheader()
        writer.writerows(decision_rows)


if __name__ == "__main__":
    main()
