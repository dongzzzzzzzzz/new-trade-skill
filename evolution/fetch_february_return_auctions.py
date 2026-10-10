#!/usr/bin/env python3
"""Fetch T+2 09:25 auction prices only for frozen executed candidates."""

from __future__ import annotations

import importlib.util
import json
import argparse
from bisect import bisect_right
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DC_STOCK = Path("/Users/lee.dong/Desktop/dc-stock")
HELPER = DC_STOCK / "scripts" / "replay_capital_profit_paths_v2.py"
KLINES = DC_STOCK / "data" / "2026_raw" / "klines_2026.parquet"
OUTPUT_DIR = ROOT / "auction_cache_2026-02"
INPUT = ROOT / "replay_current_skill_auction_2026-02.jsonl"


def load_helper():
    spec = importlib.util.spec_from_file_location("auction_data_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load auction helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    helper = load_helper()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    bars = pd.read_parquet(KLINES, columns=["date"])
    trade_dates = sorted(pd.to_datetime(bars["date"]).dt.normalize().drop_duplicates().tolist())
    requests: set[tuple[str, str]] = set()
    for item in records:
        if not item.get("executed") or item.get("execution_status") != "selected_pending_t2_auction":
            continue
        signal = pd.Timestamp(item["signal_date"]).normalize()
        pos = bisect_right(trade_dates, signal)
        if pos + 1 >= len(trade_dates):
            continue
        t2_date = trade_dates[pos + 1].date().isoformat()
        requests.add((t2_date, item["executed_candidate"]))

    config = {
        "auction_workers": 2,
        "auction_timeout_seconds": 5.0,
        "auction_max_pages": 5,
    }
    summary, process, metadata = helper.load_or_fetch_auctions(
        sorted(requests), args.output_dir, config, refresh=False
    )
    manifest_path = args.output_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest.update(
        {
            "return_request_pairs_added": len(requests),
            "return_requests": sorted(requests),
            "return_fetch_metadata": metadata,
            "summary_rows_current": len(summary),
            "process_rows_current": len(process),
            "full_series_pairs_current": int(
                summary.get("auction_data_mode", pd.Series(dtype=str)).eq("full_series").sum()
            ),
            "return_prices_not_fetched": False,
        }
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"requests": sorted(requests), "summary_rows": len(summary), "process_rows": len(process)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
