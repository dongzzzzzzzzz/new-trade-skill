#!/usr/bin/env python3
"""Fetch future auction prices for explicitly declared recall diagnostics.

These pairs are not strategy decisions. They are only used after the frozen
replay to locate missed candidates and are recorded as diagnostic scope.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DC_STOCK = Path("/Users/lee.dong/Desktop/dc-stock")
HELPER = DC_STOCK / "scripts" / "replay_capital_profit_paths_v2.py"
OUTPUT_DIR = ROOT / "auction_cache_2026-02"

# Declared before reading any resulting prices. These candidates are the
# strongest T-day alternatives around the two negative executed trades.
DIAGNOSTIC_REQUESTS = [
    ("2026-02-06", "301362.SZ"),
    ("2026-02-06", "603618.SH"),
    ("2026-02-06", "000533.SZ"),
    ("2026-02-06", "603616.SH"),
    ("2026-03-03", "002378.SZ"),
    ("2026-03-03", "000899.SZ"),
    ("2026-03-03", "001209.SZ"),
    ("2026-03-03", "001896.SZ"),
]


def load_helper():
    spec = importlib.util.spec_from_file_location("auction_data_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load auction helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    helper = load_helper()
    config = {
        "auction_workers": 2,
        "auction_timeout_seconds": 5.0,
        "auction_max_pages": 5,
    }
    summary, process, metadata = helper.load_or_fetch_auctions(
        sorted(DIAGNOSTIC_REQUESTS), OUTPUT_DIR, config, refresh=False
    )
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest.update(
        {
            "diagnostic_return_requests_added": len(DIAGNOSTIC_REQUESTS),
            "diagnostic_return_requests": sorted(DIAGNOSTIC_REQUESTS),
            "diagnostic_return_fetch_metadata": metadata,
            "summary_rows_current": len(summary),
            "process_rows_current": len(process),
            "diagnostic_scope": "includes targeted T+2 pairs for frozen negative-trade recall audits; never decision inputs",
        }
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"requests": sorted(DIAGNOSTIC_REQUESTS), "summary_rows": len(summary), "process_rows": len(process)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
