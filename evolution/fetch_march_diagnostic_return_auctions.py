#!/usr/bin/env python3
"""Fetch declared T+2 auction pairs for March failure diagnostics only."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DC_STOCK = Path("/Users/lee.dong/Desktop/dc-stock")
HELPER = DC_STOCK / "scripts" / "replay_capital_profit_paths_v2.py"
OUTPUT_DIR = ROOT / "auction_cache_2026-03"

REQUESTS = [
    ("2026-03-11", "002261.SZ"),
    ("2026-03-11", "601789.SH"),
    ("2026-03-16", "600726.SH"),
    ("2026-03-16", "002150.SZ"),
    ("2026-03-16", "601016.SH"),
    ("2026-04-01", "002038.SZ"),
    ("2026-04-01", "600488.SH"),
    ("2026-04-01", "600513.SH"),
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
    summary, process, metadata = helper.load_or_fetch_auctions(
        sorted(REQUESTS),
        OUTPUT_DIR,
        {"auction_workers": 2, "auction_timeout_seconds": 5.0, "auction_max_pages": 5},
        refresh=False,
    )
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "diagnostic_return_requests": sorted(REQUESTS),
            "diagnostic_return_fetch_metadata": metadata,
            "summary_rows_current": len(summary),
            "process_rows_current": len(process),
            "diagnostic_scope": "T+2 prices for frozen March failure attribution only; never decision inputs",
        }
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"requests": sorted(REQUESTS), "summary_rows": len(summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
