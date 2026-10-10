#!/usr/bin/env python3
"""Apply only the limit-open reachability gate to an existing auction replay."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import pandas as pd

from materialize_february_auction_execution import (
    matches_exchange_price,
    theoretical_limit_up,
    weak_repair_last_minute_spike,
)


def was_eligible(record: dict, previously_executed: str) -> bool:
    if record.get("candidate") == previously_executed:
        return True
    decision = str(record.get("decision", ""))
    return "保留" in decision and "递补" in decision and all(
        word not in decision for word in ("跳过", "降级", "观察")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--facts", required=True, type=Path)
    parser.add_argument("--auction-summary", required=True, type=Path)
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    facts = pd.read_csv(args.facts, usecols=["date", "thscode", "stock_name", "close"])
    facts = facts.drop_duplicates(["date", "thscode"])
    fact_lookup = {
        (str(row.date), str(row.thscode)): (str(row.stock_name), float(row.close))
        for row in facts.itertuples(index=False)
    }
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
    auction_lookup = {
        (str(row.trade_date), str(row.stock_code)): row._asdict()
        for row in auction.itertuples(index=False)
    }

    decision_rows = []
    for item in records:
        previously_executed = str(item.get("executed_candidate") or "")
        selected_code = ""
        selected_open = None
        for record in item.get("auction_records", []):
            code = str(record["candidate"])
            fresh = auction_lookup.get((item["auction_date"], code))
            prior_status = record.get("auction_status", "")
            prior_decision = record.get("decision", "")
            record["prior_auction_status"] = prior_status
            record["prior_decision"] = prior_decision
            if fresh and fresh.get("auction_data_mode") == "full_series":
                record["auction_price_0920"] = float(fresh["auction_price_0920"])
                record["auction_price_0924"] = float(fresh["auction_price_0924"])
                record["t1_open"] = float(fresh["open_price_0925"])
                record["open_volume_hands"] = float(fresh["open_volume_hands"])
            prices = [record.get("auction_price_0920"), record.get("auction_price_0924"), record.get("t1_open")]
            fact = fact_lookup.get((item["signal_date"], code))
            complete_prices = all(
                value is not None and not (isinstance(value, float) and math.isnan(value))
                for value in prices
            )
            limit_open_untradeable = False
            limit_up_price = None
            if fact and complete_prices:
                stock_name, previous_close = fact
                limit_up_price = theoretical_limit_up(previous_close, code, stock_name)
                limit_open_untradeable = all(
                    matches_exchange_price(float(value), limit_up_price) for value in prices
                )

            record["limit_up_price"] = limit_up_price
            record["limit_open_untradeable"] = limit_open_untradeable

            open_gap_pct = None
            auction_drift_pct = None
            if fact and complete_prices:
                open_gap_pct = (float(record["t1_open"]) / fact[1] - 1.0) * 100.0
                auction_drift_pct = (
                    float(record["auction_price_0924"]) / float(record["auction_price_0920"]) - 1.0
                ) * 100.0
            record["open_gap_pct"] = open_gap_pct
            record["auction_drift_pct"] = auction_drift_pct
            open_gap_failure = open_gap_pct is not None and open_gap_pct < -2.0
            record["open_gap_failure"] = open_gap_failure

            eligible = was_eligible(record, previously_executed)
            role = next(
                (
                    str(audit.get("role", ""))
                    for audit in item.get("candidate_audit", [])
                    if audit.get("candidate") == code
                ),
                "",
            )
            weak_repair_spike = bool(
                fact
                and complete_prices
                and weak_repair_last_minute_spike(
                    str(item.get("environment_state", "")),
                    str(item.get("sentiment_state", "")),
                    role,
                    fact[1],
                    float(record["auction_price_0924"]),
                    float(record["t1_open"]),
                )
            )
            record["weak_repair_last_minute_spike"] = weak_repair_spike
            if not fresh or fresh.get("auction_data_mode") != "full_series":
                record["auction_status"] = "不可判断"
                record["decision"] = "跳过并等待"
                record["reason"] = "T+1竞价事实缺失，不能假设可成交"
            elif limit_open_untradeable:
                record["auction_status"] = "不可交易"
                record["decision"] = "跳过并递补"
                record["reason"] = "9:20、9:24和T+1开盘均锁在涨停价，无法证明开盘可成交"
            elif weak_repair_spike:
                record["auction_status"] = "不及预期"
                record["decision"] = "跳过并递补"
                record["reason"] = "弱修复中的非市场核心在9:24后末分钟急拉且高开，按竞价虚强处理"
            elif open_gap_failure:
                record["auction_status"] = "不及预期"
                record["decision"] = "跳过并递补"
                record["reason"] = "T+1开盘跌破前收-2%的基础失效边界"
            elif eligible and not selected_code:
                selected_code = code
                selected_open = float(record["t1_open"])
                record["decision"] = "保留并执行"
                record["reason"] = "保留原竞价判断，并在前序不可交易后按冻结队列执行"
            elif eligible:
                record["decision"] = "保留为递补"

        item["executed_candidate"] = selected_code
        item["executed"] = bool(selected_code)
        item["execution_status"] = "selected_pending_t2_auction" if selected_code else "not_executed"
        item["t1_open_buy_price"] = selected_open
        item["t2_auction_sell_price"] = None
        item["return_pct"] = None
        item["replay_status"] = (
            "auction_confirmed_pending_t2_return_auction"
            if selected_code
            else "auction_rejected_or_missing"
        )
        if not selected_code:
            item["invalidated_reason"] = "原始队列内没有通过竞价且可在开盘成交的候选"

        candidate_name = next(
            (
                audit.get("name", "")
                for audit in item.get("candidate_audit", [])
                if audit.get("candidate") == selected_code
            ),
            "",
        )
        if not candidate_name and selected_code:
            candidate_name = fact_lookup.get((item["signal_date"], selected_code), ("", 0.0))[0]
        decision_rows.append(
            {
                "signal_date": item["signal_date"],
                "candidate": candidate_name,
                "code": selected_code,
                "executed": str(bool(selected_code)).lower(),
                "execution_status": item["execution_status"],
            }
        )

    with args.output.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    with args.decisions.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decision_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(decision_rows)


if __name__ == "__main__":
    main()
