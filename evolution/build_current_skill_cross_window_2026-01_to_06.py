#!/usr/bin/env python3
"""Combine the latest kept January-June return windows in date order."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCES = [
    ROOT / "challenger_returns_open_gap_floor_2026-01.csv",
    ROOT / "challenger_returns_high_volatility_auction_decay_2026-02.csv",
    ROOT / "challenger_returns_high_volatility_auction_decay_2026-03.csv",
    ROOT / "challenger_returns_unrelated_cluster_wait_april17_2026-04.csv",
    ROOT / "challenger_returns_may_specific_relation_2026-05.csv",
    ROOT / "challenger_returns_residual_extreme_loss_repair_2026-06.csv",
]
OUTPUT = ROOT / "current_skill_returns_2026-01_to_06.csv"


def main() -> None:
    frames = []
    for source in SOURCES:
        frame = pd.read_csv(source)
        frame["source_window"] = source.stem
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    combined["signal_date"] = pd.to_datetime(combined["signal_date"])
    assert not combined["signal_date"].duplicated().any()
    combined = combined.sort_values("signal_date")
    combined["signal_date"] = combined["signal_date"].dt.date.astype(str)
    combined.to_csv(OUTPUT, index=False)


if __name__ == "__main__":
    main()
