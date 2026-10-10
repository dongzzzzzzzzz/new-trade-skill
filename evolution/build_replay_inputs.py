#!/usr/bin/env python3
"""Build strategy-neutral T-day replay inputs.

The output contains raw market facts and derived point-in-time price facts only.
It deliberately excludes market roles, theme elections, candidate eligibility,
path ids, rankings, and returns produced by any other strategy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--klines", required=True, type=Path)
    parser.add_argument("--special-pools", required=True, type=Path)
    parser.add_argument("--enriched-pools", required=True, type=Path)
    parser.add_argument("--market-facts", required=True, type=Path)
    parser.add_argument("--index-facts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()

    start = pd.Timestamp(args.start_date).normalize()
    end = pd.Timestamp(args.end_date).normalize()

    bars = pd.read_parquet(args.klines)
    bars["date"] = pd.to_datetime(bars["date"]).dt.normalize()
    bars = bars.sort_values(["thscode", "date"])
    bars["prev_close"] = bars.groupby("thscode")["close"].shift(1)
    bars["prev2_close"] = bars.groupby("thscode")["close"].shift(2)
    bars["tday_open_return"] = bars["open"] / bars["prev_close"] - 1.0
    bars["tday_close_return"] = bars["close"] / bars["prev_close"] - 1.0
    bars["prior_close_return"] = bars["prev_close"] / bars["prev2_close"] - 1.0
    bars["range_return"] = bars["high"] / bars["low"] - 1.0
    bars["amount_5d_median"] = bars.groupby("thscode")["amount"].transform(
        lambda s: s.shift(1).rolling(5, min_periods=1).median()
    )
    bars["amount_vs_5d_median"] = bars["amount"] / bars["amount_5d_median"]
    bars = bars[(bars["date"] >= start) & (bars["date"] <= end)]

    pools = pd.read_parquet(args.special_pools)
    pools["date"] = pd.to_datetime(pools["date"]).dt.normalize()
    pools = pools[(pools["date"] >= start) & (pools["date"] <= end)]

    enriched = pd.read_csv(args.enriched_pools)
    enriched["date"] = pd.to_datetime(enriched["trade_date"]).dt.normalize()
    enriched = enriched[(enriched["date"] >= start) & (enriched["date"] <= end)]
    enriched = enriched[
        [
            "date",
            "pool_type",
            "thscode",
            "stock_name",
            "limit_up_reason",
            "continue_day_text",
            "continue_day_cnt",
            "seal_money",
            "max_seal_money",
            "open_times",
            "turnover_ratio_pct",
            "turnover",
        ]
    ]

    # The enriched source carries descriptive facts but may not have the raw
    # pool's open-times field. Keep the raw pool field under an explicit name.
    raw_pool_fields = pools[
        ["date", "type", "thscode", "name", "limit_up_time", "open_times"]
    ].rename(
        columns={
            "type": "raw_pool_type",
            "name": "raw_stock_name",
            "limit_up_time": "raw_limit_up_time",
            "open_times": "raw_open_times",
        }
    )

    facts = enriched.merge(
        raw_pool_fields,
        left_on=["date", "pool_type", "thscode"],
        right_on=["date", "raw_pool_type", "thscode"],
        how="left",
    ).drop(columns=["raw_pool_type"], errors="ignore")
    facts = facts.merge(
        bars[
            [
                "date",
                "thscode",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "amount",
                "prev_close",
                "prev2_close",
                "tday_open_return",
                "tday_close_return",
                "prior_close_return",
                "range_return",
                "amount_5d_median",
                "amount_vs_5d_median",
            ]
        ],
        on=["date", "thscode"],
        how="left",
    )
    market = pd.read_csv(args.market_facts)
    market["date"] = pd.to_datetime(market["date"]).dt.normalize()
    facts = facts.merge(market, on="date", how="left", suffixes=("", "_market"))

    index_payload = json.loads(args.index_facts.read_text(encoding="utf-8"))
    index_rows = []
    for index_name, record in index_payload["indices"].items():
        for line in record["payload"]["data"]["klines"]:
            date, open_, close, high, low, volume, amount, change_pct = line.split(",")
            index_rows.append(
                {
                    "date": pd.Timestamp(date).normalize(),
                    "index_name": index_name,
                    "index_open": float(open_),
                    "index_close": float(close),
                    "index_high": float(high),
                    "index_low": float(low),
                    "index_volume": float(volume),
                    "index_amount": float(amount),
                    "index_change_pct": float(change_pct),
                }
            )
    index_df = pd.DataFrame(index_rows).sort_values(["index_name", "date"])
    index_df["index_prev_close"] = index_df.groupby("index_name")["index_close"].shift(1)
    index_df["index_close_return"] = (
        index_df["index_close"] / index_df["index_prev_close"] - 1.0
    )
    index_df["index_3d_return"] = index_df.groupby("index_name")["index_close"].transform(
        lambda s: s / s.shift(3) - 1.0
    )
    index_df["index_amount_prev"] = index_df.groupby("index_name")["index_amount"].shift(1)
    index_df["index_amount_change"] = (
        index_df["index_amount"] / index_df["index_amount_prev"] - 1.0
    )
    index_wide = index_df.pivot(index="date", columns="index_name")
    index_wide.columns = [f"{field}_{name}" for field, name in index_wide.columns]
    index_wide = index_wide.reset_index()
    index_wide["index_breadth_spread_sh_vs_chinext"] = (
        index_wide["index_close_return_shanghai_composite"]
        - index_wide["index_close_return_chinext"]
    )
    facts = facts.merge(index_wide, on="date", how="left")
    facts["fact_source"] = (
        "2026_raw/klines_2026.parquet + 2026_raw/special_pools_2026.parquet + "
        "trade_setup_strategy/hithink_enriched/special_pools_enriched.csv + "
        "eastmoney_push2his index kline endpoint"
    )
    facts["strategy_fields_excluded"] = True
    facts = facts.sort_values(["date", "pool_type", "thscode"])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    facts.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
