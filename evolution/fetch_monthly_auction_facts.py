#!/usr/bin/env python3
"""Fetch T+1 auction facts for a monthly strategy-neutral replay input."""

from __future__ import annotations

import argparse
import importlib.util
import json
from bisect import bisect_right
from pathlib import Path

import pandas as pd


DC_STOCK = Path("/Users/lee.dong/Desktop/dc-stock")
HELPER = DC_STOCK / "scripts" / "replay_capital_profit_paths_v2.py"
KLINES = DC_STOCK / "data" / "2026_raw" / "klines_2026.parquet"


def load_helper():
    spec = importlib.util.spec_from_file_location("auction_data_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load auction helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--input", type=Path)
    inputs.add_argument("--queue-input", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    helper = load_helper()
    requests: set[tuple[str, str]] = set()
    if args.queue_input:
        queue_records = [
            json.loads(line)
            for line in args.queue_input.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for record in queue_records:
            requests.update((record["auction_date"], str(code)) for code in record["original_queue"])
        input_path = args.queue_input
        scope = "frozen original_queue rows; T+1 auction only"
    else:
        monthly_inputs = pd.read_csv(args.input, usecols=["date", "pool_type", "thscode"])
        monthly_inputs["date"] = pd.to_datetime(monthly_inputs["date"]).dt.normalize()
        monthly_inputs = monthly_inputs[monthly_inputs["pool_type"].eq("limit_up")]
        bars = pd.read_parquet(KLINES, columns=["date"])
        trade_dates = sorted(pd.to_datetime(bars["date"]).dt.normalize().drop_duplicates().tolist())
        for signal_date in sorted(monthly_inputs["date"].drop_duplicates().tolist()):
            pos = bisect_right(trade_dates, signal_date)
            if pos >= len(trade_dates):
                continue
            auction_date = trade_dates[pos].date().isoformat()
            rows = monthly_inputs[monthly_inputs["date"].eq(signal_date)]
            requests.update((auction_date, str(code)) for code in rows["thscode"])
        input_path = args.input
        scope = "limit_up rows; T+1 auction only"

    config = {
        "auction_workers": 2,
        "auction_timeout_seconds": 5.0,
        "auction_max_pages": 5,
    }
    summary, process, metadata = helper.load_or_fetch_auctions(
        sorted(requests), args.output_dir, config, refresh=False
    )
    manifest = {
        "input": str(input_path.resolve()),
        "scope": scope,
        "request_pairs": len(requests),
        "summary_rows": len(summary),
        "process_rows": len(process),
        "metadata": metadata,
        "worker_cap": 2,
        "return_prices_not_fetched": True,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
