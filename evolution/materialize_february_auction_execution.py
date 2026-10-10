#!/usr/bin/env python3
"""Apply the T+1 auction phase to the frozen February T-day queues.

The input queue file is frozen before this script runs. This phase reads only
T+1 09:25-or-earlier auction facts and does not read T+2 prices or returns.
"""

from __future__ import annotations

import csv
import json
import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_current_skill_tday_queue_2026-02.jsonl"
AUCTION = ROOT / "auction_cache_2026-02" / "auction_summary.parquet"
OUTPUT_JSONL = ROOT / "replay_current_skill_auction_2026-02.jsonl"
OUTPUT_CSV = ROOT / "current_skill_decisions_2026-02.csv"


def daily_limit_ratio(code: str, stock_name: str) -> Decimal:
    normalized_name = stock_name.upper().replace("*", "")
    if "ST" in normalized_name:
        return Decimal("0.05")
    if code.endswith(".BJ"):
        return Decimal("0.30")
    if code.split(".", 1)[0].startswith(("300", "301", "688", "689")):
        return Decimal("0.20")
    return Decimal("0.10")


def theoretical_limit_up(previous_close: float, code: str, stock_name: str) -> float:
    price = Decimal(str(previous_close)) * (Decimal("1") + daily_limit_ratio(code, stock_name))
    return float(price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def matches_exchange_price(left: float, right: float) -> bool:
    return abs(left - right) <= 0.011


def weak_repair_last_minute_spike(
    environment_state: str,
    sentiment_state: str,
    role: str,
    previous_close: float,
    auction_price_0924: float,
    open_price: float,
) -> bool:
    final_jump = (open_price / auction_price_0924 - 1.0) * 100.0
    open_gap = (open_price / previous_close - 1.0) * 100.0
    return (
        environment_state == "修复"
        and sentiment_state == "修复"
        and role != "市场核心"
        and final_jump >= 5.0
        and open_gap >= 8.0
    )


def repair_high_gap_overextension(
    environment_state: str,
    role: str,
    board_count: int,
    queue_rank: int,
    open_gap_pct: float,
) -> bool:
    """Reject high-premium non-core front candidates during plain repair."""
    return (
        environment_state == "修复"
        and role != "市场核心"
        and board_count >= 3
        and queue_rank <= 2
        and open_gap_pct >= 5.0
    )


def repair_20cm_auction_decay(
    environment_state: str,
    role: str,
    code: str,
    queue_rank: int,
    open_gap_pct: float,
    auction_drift_pct: float,
) -> bool:
    """Reject repair-day 20cm/30cm front candidates after auction decay."""
    is_large_limit = code.split(".", 1)[0].startswith(("300", "301", "688", "689"))
    return (
        environment_state == "修复"
        and role != "市场核心"
        and is_large_limit
        and queue_rank <= 2
        and open_gap_pct >= 5.0
        and auction_drift_pct <= -3.0
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT_JSONL)
    parser.add_argument("--decisions", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--facts", type=Path, default=ROOT / "replay_inputs_2026-02.csv")
    parser.add_argument("--auction-summary", type=Path, default=AUCTION)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    facts = pd.read_csv(args.facts, usecols=["date", "thscode", "stock_name", "close"])
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
        for queue_rank, code in enumerate(item["original_queue"], 1):
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
            stock_name = str(close_rows.iloc[0]["stock_name"])
            node_row = next(
                node for node in item.get("node_role_records", []) if node["candidate"] == code
            )
            gap = (open_price / close_price - 1.0) * 100.0
            drift = (float(raw["auction_price_0924"]) / float(raw["auction_price_0920"]) - 1.0) * 100.0
            limit_up_price = theoretical_limit_up(close_price, code, stock_name)
            limit_open_untradeable = all(
                matches_exchange_price(float(price), limit_up_price)
                for price in (raw["auction_price_0920"], raw["auction_price_0924"], open_price)
            )
            role = str(tday_row.get("role", ""))
            board_count = int(float(node_row.get("board_count", 0) or 0))
            high_volatility_auction_decay = (
                daily_limit_ratio(code, stock_name) >= Decimal("0.20")
                and matches_exchange_price(float(raw["auction_price_0920"]), limit_up_price)
                and drift <= -5.0
                and gap >= 10.0
                and item.get("environment_state") in {"分歧", "退潮", "分歧转退潮"}
                and role != "市场核心"
            )
            weak_repair_spike = weak_repair_last_minute_spike(
                str(item.get("environment_state", "")),
                str(item.get("sentiment_state", "")),
                role,
                close_price,
                float(raw["auction_price_0924"]),
                open_price,
            )
            repair_high_gap = repair_high_gap_overextension(
                str(item.get("environment_state", "")),
                role,
                board_count,
                queue_rank,
                gap,
            )
            repair_20cm_decay = repair_20cm_auction_decay(
                str(item.get("environment_state", "")),
                role,
                code,
                queue_rank,
                gap,
                drift,
            )
            survives = (
                not limit_open_untradeable
                and not high_volatility_auction_decay
                and not weak_repair_spike
                and not repair_high_gap
                and not repair_20cm_decay
                and gap >= -2.0
                and float(raw["open_volume_hands"]) > 0
                and drift > -8.0
            )
            if limit_open_untradeable:
                status = "不可交易"
            elif high_volatility_auction_decay:
                status = "不及预期"
            elif weak_repair_spike:
                status = "不及预期"
            elif repair_high_gap:
                status = "不及预期"
            elif repair_20cm_decay:
                status = "不及预期"
            elif gap >= 5.0:
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
                    "limit_up_price": limit_up_price,
                    "limit_open_untradeable": limit_open_untradeable,
                    "high_volatility_auction_decay": high_volatility_auction_decay,
                    "weak_repair_last_minute_spike": weak_repair_spike,
                    "repair_high_gap_overextension": repair_high_gap,
                    "repair_20cm_auction_decay": repair_20cm_decay,
                    "decision": "保留并执行" if survives else "跳过并递补",
                    "reason": (
                        "竞价可成交且未破坏T日买入前提"
                        if survives
                        else "T+1开盘价达到涨停价，无法证明开盘可成交，按原始队列顺延"
                        if limit_open_untradeable
                        else "20cm或30cm非市场核心从9:20涨停预期明显回落，双分歧或退潮中高开不等于超预期"
                        if high_volatility_auction_decay
                        else "弱修复中的非市场核心在9:24后末分钟急拉且高开，按竞价虚强处理"
                        if weak_repair_spike
                        else "修复环境中非市场核心3板以上且队列前两位高开至少5%，按高位溢价过度处理"
                        if repair_high_gap
                        else "修复环境中非市场核心20cm或30cm前排高开后竞价回落至少3%，按高预期塌缩处理"
                        if repair_20cm_decay
                        else "竞价跌破失效边界"
                    ),
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
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
