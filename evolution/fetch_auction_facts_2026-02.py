#!/usr/bin/env python3
"""Fetch point-in-time T+1 auction facts for the February replay universe.

This imports only the existing eltdx data helper from dc-stock. It does not
import or execute that project's strategy selection logic. Worker count is
intentionally capped at two because this is a development data job on the
user's desktop.
"""

from __future__ import annotations

import importlib.util
import json
from bisect import bisect_right
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DC_STOCK = Path("/Users/lee.dong/Desktop/dc-stock")
HELPER = DC_STOCK / "scripts" / "replay_capital_profit_paths_v2.py"
INPUT = ROOT / "replay_inputs_2026-02.csv"
KLINES = DC_STOCK / "data" / "2026_raw" / "klines_2026.parquet"
OUTPUT_DIR = ROOT / "auction_cache_2026-02"
CONFIG = {
    "auction_workers": 2,
    "auction_timeout_seconds": 5.0,
    "auction_max_pages": 5,
}


def load_helper():
    spec = importlib.util.spec_from_file_location("auction_data_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load auction helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    helper = load_helper()
    inputs = pd.read_csv(INPUT, usecols=["date", "pool_type", "thscode"])
    inputs["date"] = pd.to_datetime(inputs["date"]).dt.normalize()
    inputs = inputs[inputs["pool_type"].eq("limit_up")]

    bars = pd.read_parquet(KLINES, columns=["date"])
    trade_dates = sorted(pd.to_datetime(bars["date"]).dt.normalize().drop_duplicates().tolist())
    requests: set[tuple[str, str]] = set()
    for signal_date in sorted(inputs["date"].drop_duplicates().tolist()):
        pos = bisect_right(trade_dates, signal_date)
        if pos >= len(trade_dates):
            continue
        auction_date = trade_dates[pos].date().isoformat()
        rows = inputs[inputs["date"].eq(signal_date)]
        requests.update((auction_date, str(code)) for code in rows["thscode"])

    summary, process, metadata = helper.load_or_fetch_auctions(
        sorted(requests), OUTPUT_DIR, CONFIG, refresh=False
    )
    manifest = {
        "input": str(INPUT),
        "scope": "limit_up rows in February replay inputs; T+1 auction only",
        "request_pairs": len(requests),
        "summary_rows": len(summary),
        "process_rows": len(process),
        "metadata": metadata,
        "worker_cap": 2,
        "return_prices_not_fetched": True,
    }
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
