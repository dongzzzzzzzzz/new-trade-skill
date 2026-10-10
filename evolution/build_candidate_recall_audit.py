#!/usr/bin/env python3
"""Build a post-baseline candidate-recall audit.

Future prices are used only to diagnose what the frozen T-day candidate
process missed. The resulting file must never be fed back into a Challenger
decision.
"""

from __future__ import annotations

import csv
import json
from bisect import bisect_right
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW_INPUTS = ROOT / "replay_inputs_2026-01.csv"
KLINES = Path("/Users/lee.dong/Desktop/dc-stock/data/2026_raw/klines_2026.parquet")
AUCTION = Path("/Users/lee.dong/Desktop/dc-stock/data/capital_profit_path_replay_v3/auction_summary.parquet")
OUTPUT = ROOT / "candidate_recall_audit_2026-01.csv"


def normalize_code(value: object) -> str:
    code = str(value).strip().upper()
    if code.endswith((".SZ", ".SH", ".BJ")):
        return code
    return code


def load_baseline_cases() -> list[dict]:
    cases = []
    for path in sorted(ROOT.glob("replay_baseline_2026-01*.jsonl")):
        cases.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
    return cases


def main() -> None:
    inputs = pd.read_csv(RAW_INPUTS)
    inputs["date"] = pd.to_datetime(inputs["date"]).dt.normalize()
    inputs["code_key"] = inputs["thscode"].map(normalize_code)
    klines = pd.read_parquet(KLINES, columns=["thscode", "date", "open"])
    klines["date"] = pd.to_datetime(klines["date"]).dt.normalize()
    klines["code_key"] = klines["thscode"].map(normalize_code)
    auction = pd.read_parquet(AUCTION, columns=["trade_date", "stock_code", "open_price_0925"])
    auction["trade_date"] = pd.to_datetime(auction["trade_date"]).dt.normalize()
    auction["code_key"] = auction["stock_code"].map(normalize_code)
    dates = sorted(klines["date"].drop_duplicates().tolist())

    # Restrict the lookup tables to the 19-case development window. Repeated
    # full-frame filtering made the first implementation unnecessarily heavy.
    signal_dates = sorted(pd.to_datetime(inputs["date"].drop_duplicates()).tolist())
    lookup_dates = set()
    for signal in signal_dates:
        pos = bisect_right(dates, signal)
        if pos + 1 < len(dates):
            lookup_dates.update((dates[pos], dates[pos + 1]))
    klines = klines[klines["date"].isin(lookup_dates)]
    auction = auction[auction["trade_date"].isin(lookup_dates)]
    buy_map = {
        (row.date, row.code_key): float(row.open)
        for row in klines.itertuples(index=False)
    }
    sell_map = {
        (row.trade_date, row.code_key): float(row.open_price_0925)
        for row in auction.itertuples(index=False)
    }

    rows = []
    for case in load_baseline_cases():
        signal = pd.Timestamp(case["signal_date"]).normalize()
        pos = bisect_right(dates, signal)
        if pos + 1 >= len(dates):
            continue
        t1, t2 = dates[pos], dates[pos + 1]
        selected = case.get("executed_candidate") or ""
        queue_codes = set(case.get("original_queue") or [])
        day = inputs[(inputs["date"] == signal) & inputs["pool_type"].eq("limit_up")]
        candidates = []
        for record in day.to_dict("records"):
            code = normalize_code(record["thscode"])
            buy_price = buy_map.get((t1, code))
            sell_price = sell_map.get((t2, code))
            if buy_price is None or sell_price is None:
                continue
            if buy_price <= 0 or sell_price <= 0:
                continue
            candidates.append(
                {
                    "code": code,
                    "name": record["stock_name"],
                    "return_pct": (sell_price / buy_price - 1.0) * 100.0,
                    "board_count": record.get("continue_day_cnt", ""),
                    "reason": record.get("limit_up_reason", ""),
                    "in_candidate_audit": code in {
                        item.get("candidate") for item in case.get("candidate_audit", [])
                    },
                    "in_original_queue": code in queue_codes,
                }
            )
        candidates.sort(key=lambda item: item["return_pct"], reverse=True)
        best = candidates[0] if candidates else {}
        selected_row = next((item for item in candidates if item["code"] == selected), {})
        selected_rank = ""
        if selected_row:
            selected_rank = 1 + next(
                index for index, item in enumerate(candidates) if item["code"] == selected
            )
        rows.append(
            {
                "signal_date": case["signal_date"],
                "selected_code": selected,
                "selected_return_pct": selected_row.get("return_pct", ""),
                "selected_rank_by_realized_return": selected_rank,
                "best_available_code": best.get("code", ""),
                "best_available_name": best.get("name", ""),
                "best_available_return_pct": best.get("return_pct", ""),
                "best_board_count": best.get("board_count", ""),
                "best_reason": best.get("reason", ""),
                "best_in_candidate_audit": best.get("in_candidate_audit", ""),
                "best_in_original_queue": best.get("in_original_queue", ""),
                "candidate_count_with_valid_returns": len(candidates),
                "diagnostic_only": True,
            }
        )

    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
