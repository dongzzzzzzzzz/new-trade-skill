#!/usr/bin/env python3
"""Validate the limit-open execution gate across February and March."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_jsonl(name: str) -> dict[str, dict]:
    path = ROOT / name
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["signal_date"]: row for row in rows}


def changed_executions(parent: dict[str, dict], challenger: dict[str, dict]) -> dict[str, tuple[str, str]]:
    assert parent.keys() == challenger.keys()
    for signal_date in parent:
        assert parent[signal_date]["original_queue"] == challenger[signal_date]["original_queue"]
    return {
        signal_date: (
            parent[signal_date].get("executed_candidate", ""),
            challenger[signal_date].get("executed_candidate", ""),
        )
        for signal_date in parent
        if parent[signal_date].get("executed_candidate")
        != challenger[signal_date].get("executed_candidate")
    }


def validate_returns(name: str) -> int:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = (
            float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        ) * 100.0
        assert math.isclose(expected, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    return len(computed)


def main() -> None:
    feb_parent = load_jsonl("replay_challenger_isolated_high_core_auction_2026-02.jsonl")
    feb_challenger = load_jsonl("replay_challenger_limit_open_execution_2026-02.jsonl")
    mar_parent = load_jsonl("replay_challenger_dual_divergence_high_low_auction_2026-03.jsonl")
    mar_challenger = load_jsonl("replay_challenger_limit_open_execution_2026-03.jsonl")

    feb_changes = changed_executions(feb_parent, feb_challenger)
    mar_changes = changed_executions(mar_parent, mar_challenger)
    assert feb_changes == {"2026-02-10": ("603533.SH", "300182.SZ")}
    assert mar_changes == {
        "2026-03-05": ("000533.SZ", "002498.SZ"),
        "2026-03-12": ("000537.SZ", "600726.SH"),
    }

    for challenger, changes in ((feb_challenger, feb_changes), (mar_challenger, mar_changes)):
        assert all(not any(row["leakage_check"].values()) for row in challenger.values())
        for signal_date, (old_code, new_code) in changes.items():
            auction = {row["candidate"]: row for row in challenger[signal_date]["auction_records"]}
            assert auction[old_code]["limit_open_untradeable"] is True
            assert auction[old_code]["decision"] == "跳过并递补"
            assert auction[new_code]["limit_open_untradeable"] is False
            assert auction[new_code]["decision"] == "保留并执行"

    result = {
        "2026-02": feb_changes,
        "2026-03": mar_changes,
        "computed_returns": {
            "2026-02": validate_returns("challenger_returns_limit_open_execution_2026-02.csv"),
            "2026-03": validate_returns("challenger_returns_limit_open_execution_2026-03.csv"),
        },
        "queues_unchanged": True,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
