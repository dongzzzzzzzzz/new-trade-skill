#!/usr/bin/env python3
"""Audit February candidate survivorship through the T+1 auction.

This is diagnostic only. It uses T-day limit-up facts and the next auction
snapshot, but it does not choose candidates, use T+2 prices, or feed any
future result back into the skill.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_inputs_2026-02.csv"
AUCTION = ROOT / "auction_cache_2026-02" / "auction_summary.parquet"
OUTPUT = ROOT / "february_auction_survivorship_audit_2026-02.csv"


def main() -> None:
    facts = pd.read_csv(INPUT)
    facts = facts[facts["pool_type"].eq("limit_up")].copy()
    facts["date"] = pd.to_datetime(facts["date"]).dt.normalize()
    facts["boards"] = pd.to_numeric(facts["continue_day_cnt"], errors="coerce").fillna(1)
    facts["close"] = pd.to_numeric(facts["close"], errors="coerce")

    auction = pd.read_parquet(
        AUCTION,
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
    auction["trade_date"] = pd.to_datetime(auction["trade_date"]).dt.normalize()
    auction["stock_code"] = auction["stock_code"].astype(str)

    # The next trading date is already represented by the auction cache. The
    # join is intentionally point-in-time: no T+1 close or T+2 information.
    dates = sorted(auction["trade_date"].drop_duplicates())
    signal_dates = sorted(facts["date"].drop_duplicates())
    next_date = {}
    for signal in signal_dates:
        later = [value for value in dates if value > signal]
        if later:
            next_date[signal] = later[0]

    facts["auction_date"] = facts["date"].map(next_date)
    merged = facts.merge(
        auction,
        left_on=["auction_date", "thscode"],
        right_on=["trade_date", "stock_code"],
        how="left",
    )
    merged["open_gap_pct"] = (merged["open_price_0925"] / merged["close"] - 1.0) * 100.0
    merged["auction_drift_pct"] = (
        merged["auction_price_0924"] / merged["auction_price_0920"] - 1.0
    ) * 100.0
    merged["auction_survives_basic_gate"] = (
        merged["open_price_0925"].notna()
        & (merged["open_gap_pct"] >= -2.0)
        & (merged["open_volume_hands"] > 0)
    )

    rows = []
    for signal_date, day in merged.groupby("date", sort=True):
        basic = day["auction_survives_basic_gate"]
        low = day["boards"].le(3)
        high = day["boards"].ge(4)
        surviving = day[basic]
        top = surviving.sort_values(
            ["boards", "open_gap_pct", "open_volume_hands"],
            ascending=[False, False, False],
        ).head(3)
        rows.append(
            {
                "signal_date": signal_date.date().isoformat(),
                "auction_date": day["auction_date"].iloc[0].date().isoformat()
                if pd.notna(day["auction_date"].iloc[0])
                else "",
                "limit_up_candidates": len(day),
                "auction_covered": int(day["open_price_0925"].notna().sum()),
                "auction_survivors_basic_gate": int(basic.sum()),
                "low_board_candidates": int(low.sum()),
                "low_board_survivors": int((basic & low).sum()),
                "high_board_candidates": int(high.sum()),
                "high_board_survivors": int((basic & high).sum()),
                "negative_breadth": float(day["down_ratio"].iloc[0]) >= 0.5,
                "prior_limit_up_negative": float(
                    day["prev_limit_up_close_return_median"].iloc[0]
                ) < 0,
                "top_survivors": "; ".join(
                    f"{row.thscode}:{row.stock_name}:{int(row.boards)}B:{row.open_gap_pct:.2f}%"
                    for row in top.itertuples()
                ),
            }
        )

    pd.DataFrame(rows).to_csv(OUTPUT, index=False)


if __name__ == "__main__":
    main()
