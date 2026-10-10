#!/usr/bin/env python3
"""Build T-day market facts from raw daily bars and special-pool data.

This intentionally emits facts only. It does not infer themes, market modes,
candidate rankings, or returns, so those decisions remain inside the target
skill and cannot be imported from another strategy.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--klines", required=True, type=Path)
    parser.add_argument("--special-pools", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    args = parser.parse_args()

    bars = pd.read_parquet(
        args.klines,
        columns=["thscode", "date", "open", "close", "volume", "amount"],
    )
    bars["date"] = pd.to_datetime(bars["date"]).dt.normalize()
    bars = bars.sort_values(["thscode", "date"])
    bars["prev_close"] = bars.groupby("thscode")["close"].shift(1)
    bars["open_return"] = bars["open"] / bars["prev_close"] - 1.0
    bars["close_return"] = bars["close"] / bars["prev_close"] - 1.0
    bars["up"] = bars["close_return"] > 0
    bars["down"] = bars["close_return"] < 0

    pools = pd.read_parquet(
        args.special_pools,
        columns=["date", "type", "thscode", "name", "limit_up_time", "open_times"],
    )
    pools["date"] = pd.to_datetime(pools["date"]).dt.normalize()

    pool_counts = pools.pivot_table(
        index="date", columns="type", values="thscode", aggfunc="count", fill_value=0
    ).reset_index()
    for column in ["limit_up", "limit_break", "limit_down"]:
        if column not in pool_counts:
            pool_counts[column] = 0

    daily = bars.groupby("date", as_index=False).agg(
        stock_count=("thscode", "count"),
        up_count=("up", "sum"),
        down_count=("down", "sum"),
        amount_sum=("amount", "sum"),
        volume_sum=("volume", "sum"),
        open_return_median=("open_return", "median"),
        close_return_median=("close_return", "median"),
    )
    daily["up_ratio"] = daily["up_count"] / daily["stock_count"]
    daily["down_ratio"] = daily["down_count"] / daily["stock_count"]

    # Feedback for the stocks that were limit-up on the previous T day.
    limit_up = pools[pools["type"].eq("limit_up")][["date", "thscode"]].copy()
    trading_dates = sorted(bars["date"].drop_duplicates().tolist())
    next_date = {trading_dates[i]: trading_dates[i + 1] for i in range(len(trading_dates) - 1)}
    limit_up["feedback_date"] = limit_up["date"].map(next_date)
    feedback = limit_up.merge(
        bars[["date", "thscode", "open_return", "close_return"]],
        left_on=["feedback_date", "thscode"],
        right_on=["date", "thscode"],
        how="left",
    )
    feedback_daily = feedback.groupby("feedback_date", as_index=False).agg(
        prev_limit_up_count=("thscode", "count"),
        prev_limit_up_open_positive_ratio=("open_return", lambda s: (s > 0).mean()),
        prev_limit_up_open_return_median=("open_return", "median"),
        prev_limit_up_close_return_median=("close_return", "median"),
    )

    result = daily.merge(
        pool_counts.rename(
            columns={"limit_up": "limit_up_count", "limit_break": "limit_break_count", "limit_down": "limit_down_count"}
        ),
        on="date",
        how="left",
    ).merge(feedback_daily, left_on="date", right_on="feedback_date", how="left")
    result = result.drop(columns=["feedback_date"], errors="ignore").fillna(0)

    if args.start_date:
        result = result[result["date"] >= pd.Timestamp(args.start_date)]
    if args.end_date:
        result = result[result["date"] <= pd.Timestamp(args.end_date)]

    result["date"] = result["date"].dt.date.astype(str)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
