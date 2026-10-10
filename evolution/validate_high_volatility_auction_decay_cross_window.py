#!/usr/bin/env python3
"""Validate the high-volatility auction-decay gate across January-March."""

from __future__ import annotations

import csv
import json
import math
from decimal import Decimal
from pathlib import Path

import pandas as pd

from materialize_february_auction_execution import daily_limit_ratio, matches_exchange_price


ROOT = Path(__file__).resolve().parent


def load_jsonl(name: str) -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["signal_date"]: row for row in rows}


def changed_executions(parent: dict[str, dict], challenger: dict[str, dict]) -> dict[str, tuple[str, str]]:
    assert parent.keys() == challenger.keys()
    changes = {}
    for signal_date in parent:
        assert parent[signal_date]["original_queue"] == challenger[signal_date]["original_queue"]
        old = parent[signal_date].get("executed_candidate") or ""
        new = challenger[signal_date].get("executed_candidate") or ""
        if old != new:
            changes[signal_date] = (old, new)
    return changes


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


def january_triggers() -> list[tuple[str, str]]:
    records = load_jsonl("replay_challenger_limit_open_execution_2026-01.jsonl")
    facts = pd.read_csv(
        ROOT / "replay_inputs_2026-01.csv",
        usecols=["date", "thscode", "stock_name", "close"],
    ).drop_duplicates(["date", "thscode"])
    lookup = {
        (str(row.date), str(row.thscode)): (str(row.stock_name), float(row.close))
        for row in facts.itertuples(index=False)
    }
    triggers = []
    for signal_date, item in records.items():
        nodes = {row["candidate"]: row for row in item.get("candidate_audit", [])}
        for auction in item.get("auction_records", []):
            code = auction["candidate"]
            fact = lookup.get((signal_date, code))
            if not fact or any(auction.get(key) is None for key in ("auction_price_0920", "auction_price_0924", "t1_open")):
                continue
            stock_name, previous_close = fact
            ratio = daily_limit_ratio(code, stock_name)
            limit_price = float(
                (Decimal(str(previous_close)) * (Decimal("1") + ratio)).quantize(Decimal("0.01"))
            )
            drift = (float(auction["auction_price_0924"]) / float(auction["auction_price_0920"]) - 1.0) * 100.0
            gap = (float(auction["t1_open"]) / previous_close - 1.0) * 100.0
            role = str(nodes.get(code, {}).get("role", ""))
            if (
                ratio >= Decimal("0.20")
                and matches_exchange_price(float(auction["auction_price_0920"]), limit_price)
                and drift <= -5.0
                and gap >= 10.0
                and item.get("environment_state") in {"分歧", "退潮", "分歧转退潮"}
                and role != "市场核心"
            ):
                triggers.append((signal_date, code))
    return triggers


def main() -> None:
    feb_parent = load_jsonl("replay_challenger_limit_open_execution_2026-02.jsonl")
    feb_challenger = load_jsonl("replay_challenger_high_volatility_auction_decay_2026-02.jsonl")
    mar_parent = load_jsonl("replay_challenger_limit_open_execution_2026-03.jsonl")
    mar_challenger = load_jsonl("replay_challenger_high_volatility_auction_decay_2026-03.jsonl")

    feb_changes = changed_executions(feb_parent, feb_challenger)
    mar_changes = changed_executions(mar_parent, mar_challenger)
    assert feb_changes == {"2026-02-10": ("300182.SZ", "")}
    assert mar_changes == {}
    assert january_triggers() == []
    assert all(not any(row["leakage_check"].values()) for row in feb_challenger.values())
    assert all(not any(row["leakage_check"].values()) for row in mar_challenger.values())

    trigger_record = next(
        record
        for record in feb_challenger["2026-02-10"]["auction_records"]
        if record["candidate"] == "300182.SZ"
    )
    assert trigger_record["high_volatility_auction_decay"] is True
    assert trigger_record["decision"] == "跳过并递补"

    result = {
        "trigger_set": {
            "2026-01": [],
            "2026-02": [["2026-02-10", "300182.SZ"]],
            "2026-03": [],
        },
        "execution_changes": {"2026-02": feb_changes, "2026-03": mar_changes},
        "computed_returns": {
            "2026-02": validate_returns("challenger_returns_high_volatility_auction_decay_2026-02.csv"),
            "2026-03": validate_returns("challenger_returns_high_volatility_auction_decay_2026-03.csv"),
        },
        "queues_unchanged": True,
        "all_leakage_flags_false": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
