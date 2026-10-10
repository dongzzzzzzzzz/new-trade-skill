#!/usr/bin/env python3
"""Compute T+1-open to T+2-auction returns from raw market data.

The decisions file is the only strategy-owned input. Existing strategy returns
must not be reused because they may use a different exit timing or candidate
selection process.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from pathlib import Path

import pandas as pd


def normalize_code(value: object) -> str:
    code = str(value).strip().upper()
    if code.endswith((".SZ", ".SH", ".BJ")):
        return code
    if code.isdigit():
        if code.startswith(("0", "2", "3")):
            return f"{code.zfill(6)}.SZ"
        if code.startswith(("4", "8")):
            return f"{code.zfill(6)}.BJ"
        return f"{code.zfill(6)}.SH"
    return code


def next_two_dates(signal_date: pd.Timestamp, trading_dates: list[pd.Timestamp]):
    pos = bisect_right(trading_dates, signal_date)
    if pos + 1 >= len(trading_dates):
        return None, None
    return trading_dates[pos], trading_dates[pos + 1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--klines", required=True, type=Path)
    parser.add_argument("--auction-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    decisions = pd.read_csv(args.decisions)
    required = {"signal_date", "code", "executed"}
    missing = required - set(decisions.columns)
    if missing:
        raise SystemExit(f"decisions missing columns: {sorted(missing)}")

    klines = pd.read_parquet(args.klines, columns=["thscode", "date", "open"])
    auction = pd.read_parquet(
        args.auction_summary,
        columns=["trade_date", "stock_code", "open_price_0925", "auction_data_mode"],
    )
    klines["date"] = pd.to_datetime(klines["date"]).dt.normalize()
    auction["trade_date"] = pd.to_datetime(auction["trade_date"]).dt.normalize()
    klines["code_key"] = klines["thscode"].map(normalize_code)
    auction["code_key"] = auction["stock_code"].map(normalize_code)
    trading_dates = sorted(pd.to_datetime(klines["date"].drop_duplicates()).tolist())

    rows = []
    for record in decisions.to_dict("records"):
        signal_date = pd.Timestamp(record["signal_date"]).normalize()
        code = normalize_code(record["code"])
        t1_date, t2_date = next_two_dates(signal_date, trading_dates)
        executed = str(record["executed"]).strip().lower() in {"1", "true", "yes", "y"}
        result = {
            "signal_date": signal_date.date().isoformat(),
            "candidate": record.get("candidate", ""),
            "code": code,
            "executed": executed,
            "t1_date": t1_date.date().isoformat() if t1_date is not None else "",
            "t2_date": t2_date.date().isoformat() if t2_date is not None else "",
            "t1_open_buy_price": "",
            "t2_auction_sell_price": "",
            "return_pct": "",
            "status": "missing_trading_dates" if t2_date is None else "pending",
        }
        if t1_date is None or t2_date is None:
            rows.append(result)
            continue

        t1_rows = klines[(klines["date"] == t1_date) & (klines["code_key"] == code)]
        t2_rows = auction[(auction["trade_date"] == t2_date) & (auction["code_key"] == code)]
        if t1_rows.empty or t2_rows.empty:
            result["status"] = "missing_raw_price"
            rows.append(result)
            continue

        buy_price = float(t1_rows.iloc[0]["open"])
        sell_price = float(t2_rows.iloc[0]["open_price_0925"])
        if not executed:
            result["status"] = "not_executed"
            rows.append(result)
            continue

        result["t1_open_buy_price"] = buy_price
        result["t2_auction_sell_price"] = sell_price
        result["return_pct"] = (sell_price / buy_price - 1.0) * 100.0
        result["status"] = "computed"
        rows.append(result)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
