#!/usr/bin/env python3
"""Validate the combined January-June current-skill return window."""

from __future__ import annotations

import json
import math
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


def main() -> None:
    combined = pd.read_csv(ROOT / "current_skill_returns_2026-01_to_06.csv")
    metrics = json.loads((ROOT / "current_skill_metrics_2026-01_to_06.json").read_text())
    source_rows = sum(len(pd.read_csv(source)) for source in SOURCES)
    assert len(combined) == source_rows == 115
    assert not combined["signal_date"].duplicated().any()
    assert list(combined["signal_date"]) == sorted(combined["signal_date"])
    computed = combined[combined["status"].eq("computed")]
    assert len(computed) == metrics["computed_trades"] == 43
    for row in computed.itertuples(index=False):
        expected = float(row.t2_auction_sell_price) / float(row.t1_open_buy_price) - 1.0
        assert math.isclose(expected * 100.0, float(row.return_pct), rel_tol=0, abs_tol=1e-10)
    returns = pd.to_numeric(computed["return_pct"])
    assert math.isclose(float(returns.sum()), metrics["simple_return_sum_pct"], abs_tol=1e-10)
    compounded = float((1.0 + returns / 100.0).prod() - 1.0) * 100.0
    assert math.isclose(compounded, metrics["compounded_return_pct"], abs_tol=1e-10)
    print(json.dumps({
        "signal_dates": len(combined),
        "computed_trades": len(computed),
        "source_windows": len(SOURCES),
        "no_duplicate_signal_dates": True,
        "all_return_formulas_recomputed": True,
        "continuous_compound_verified": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
