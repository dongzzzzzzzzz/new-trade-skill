#!/usr/bin/env python3
"""Apply the T+1 auction phase to the frozen February T-day queues.

The input queue file is frozen before this script runs. This phase reads only
T+1 09:25-or-earlier auction facts and does not read T+2 prices or returns.
"""

from __future__ import annotations

import csv
import json
import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_current_skill_tday_queue_2026-02.jsonl"
AUCTION = ROOT / "auction_cache_2026-02" / "auction_summary.parquet"
OUTPUT_JSONL = ROOT / "replay_current_skill_auction_2026-02.jsonl"
OUTPUT_CSV = ROOT / "current_skill_decisions_2026-02.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT_JSONL)
    parser.add_argument("--decisions", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--facts", type=Path, default=ROOT / "replay_inputs_2026-02.csv")
    parser.add_argument("--auction-summary", type=Path, default=AUCTION)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    facts = pd.read_csv(args.facts, usecols=["date", "thscode", "close"])
    auction = pd.read_parquet(
        args.auction_summary,
        columns=[
            "trade_date",
            "stock_code",
            "auction_price_0920",
            "auction_price_0924",
            "open_price_0925",
            "open_volume_hands",
            "auction_data_mode",
        ],
    )
    auction["trade_date"] = pd.to_datetime(auction["trade_date"]).dt.date.astype(str)
    auction["stock_code"] = auction["stock_code"].astype(str)
    lookup = {(row.trade_date, row.stock_code): row._asdict() for row in auction.itertuples(index=False)}

    for item in records:
        if item.get("replay_status") == "tday_queue_frozen_with_repair_challenger_slice":
            continue

        auction_records = []
        executable = []
        for code in item["original_queue"]:
            raw = lookup.get((item["auction_date"], code))
            if raw is None:
                auction_records.append(
                    {
                        "candidate": code,
                        "auction_status": "不可判断",
                        "decision": "跳过并等待",
                        "reason": "T+1竞价事实缺失，不能假设可成交",
                    }
                )
                continue
            open_price = float(raw["open_price_0925"])
            # This is an execution gate, not a new candidate ranker. The
            # original T-day queue order remains unchanged.
            tday_row = next(
                audit for audit in item["candidate_audit"] if audit["candidate"] == code
            )
            # The T-day close is stored in the input-derived audit only as
            # evidence text, so use the queue's source-independent open gap
            # gate from the auction cache against the previous close supplied
            # by the frozen replay input through a direct lookup below.
            close_rows = facts[(facts["date"] == item["signal_date"]) & facts["thscode"].eq(code)]
            close_price = float(close_rows.iloc[0]["close"])
            gap = (open_price / close_price - 1.0) * 100.0
            drift = (float(raw["auction_price_0924"]) / float(raw["auction_price_0920"]) - 1.0) * 100.0
            survives = gap >= -2.0 and float(raw["open_volume_hands"]) > 0 and drift > -8.0
            if gap >= 5.0:
                status = "超预期"
            elif survives:
                status = "符合预期"
            else:
                status = "不及预期"
            auction_records.append(
                {
                    "candidate": code,
                    "auction_status": status,
                    "auction_price_0920": float(raw["auction_price_0920"]),
                    "auction_price_0924": float(raw["auction_price_0924"]),
                    "t1_open": open_price,
                    "open_volume_hands": float(raw["open_volume_hands"]),
                    "open_gap_pct": gap,
                    "auction_drift_pct": drift,
                    "decision": "保留并执行" if survives else "跳过并递补",
                    "reason": "竞价可成交且未破坏T日买入前提" if survives else "竞价跌破失效边界",
                }
            )
            if survives:
                executable.append((code, open_price))

        item["auction_records"] = auction_records
        if executable:
            code, open_price = executable[0]
            item["executed_candidate"] = code
            item["executed"] = True
            item["execution_status"] = "selected_pending_t2_auction"
            item["t1_open_buy_price"] = open_price
            item["replay_status"] = "auction_confirmed_pending_t2_return_auction"
            for record in auction_records:
                if record["candidate"] != code and record["decision"] == "保留并执行":
                    record["decision"] = "保留为递补"
        else:
            item["executed_candidate"] = ""
            item["executed"] = False
            item["execution_status"] = "not_executed"
            item["replay_status"] = "auction_rejected_or_missing"
            item["invalidated_reason"] = "原始队列内没有通过T+1竞价执行门的候选"

    with args.output.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = []
    for item in records:
        rows.append(
            {
                "signal_date": item["signal_date"],
                "candidate": next((a.get("name", "") for a in item.get("candidate_audit", []) if a.get("candidate") == item.get("executed_candidate")), ""),
                "code": item.get("executed_candidate", ""),
                "executed": str(item.get("executed", False)).lower(),
                "execution_status": item.get("execution_status", ""),
            }
        )
    with args.decisions.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
