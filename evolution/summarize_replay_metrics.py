#!/usr/bin/env python3
"""Summarize replay returns, including sequential equity drawdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--returns", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = pd.read_csv(args.returns)
    trades = data[data["status"].eq("computed")].copy()
    returns = pd.to_numeric(trades["return_pct"], errors="coerce").dropna()
    equity = (1.0 + returns / 100.0).cumprod()
    drawdown = equity / equity.cummax() - 1.0 if not equity.empty else pd.Series(dtype=float)
    result = {
        "source": str(args.returns),
        "signal_dates": int(len(data)),
        "computed_trades": int(len(returns)),
        "not_executed": int(data["status"].eq("not_executed").sum()),
        "simple_return_sum_pct": float(returns.sum()) if len(returns) else None,
        "average_trade_return_pct": float(returns.mean()) if len(returns) else None,
        "win_rate": float((returns > 0).mean()) if len(returns) else None,
        "compounded_return_pct": float((equity.iloc[-1] - 1.0) * 100.0) if len(equity) else None,
        "max_sequential_equity_drawdown_pct": float(drawdown.min() * 100.0) if len(drawdown) else None,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
