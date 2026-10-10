#!/usr/bin/env python3
"""Report dual-divergence high-to-low triggers across development windows."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return rows


def trigger(item: dict) -> bool:
    if item.get("environment_state") != "分歧" or item.get("sentiment_state") != "分歧":
        return False
    queue = item.get("original_queue") or []
    if len(queue) < 2:
        return False
    nodes = {row.get("candidate"): row for row in item.get("node_role_records", [])}
    head = nodes.get(queue[0], {})
    boards = int(float(head.get("board_count", 0) or 0))
    if head.get("role") == "市场核心" or boards < 4 or boards > 6:
        return False
    return any(int(float(nodes.get(code, {}).get("board_count", 99) or 99)) <= 2 for code in queue[1:])


def main() -> None:
    windows = {
        "2026-01": load(sorted(ROOT.glob("replay_baseline_2026-01*.jsonl"))),
        "2026-02": load([ROOT / "replay_current_skill_tday_queue_2026-02.jsonl"]),
        "2026-03": load([ROOT / "replay_current_skill_tday_queue_2026-03.jsonl"]),
    }
    result = {
        month: [item["signal_date"] for item in sorted(rows, key=lambda row: row["signal_date"]) if trigger(item)]
        for month, rows in windows.items()
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result != {"2026-01": [], "2026-02": [], "2026-03": ["2026-03-30"]}:
        raise SystemExit("unexpected cross-window trigger set")


if __name__ == "__main__":
    main()
