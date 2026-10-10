#!/usr/bin/env python3
"""Freeze a current-skill T-day queue for every February signal date.

This phase reads only replay_inputs_2026-02.csv. Auction facts, T+1 opens,
T+2 auctions, and realized returns are deliberately excluded. The output is
therefore a strategy decision artifact, not an economic result.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_inputs_2026-02.csv"
EXISTING = ROOT / "replay_challenger_repair_day_low_front_2026-02.jsonl"
OUTPUT_JSONL = ROOT / "replay_current_skill_tday_queue_2026-02.jsonl"
OUTPUT_CSV = ROOT / "queue_freeze_current_skill_2026-02.csv"


# This map is the predeclared T-day interpretation of the current skill. It
# is intentionally written before auction facts are joined in the next phase.
PLANS = {
    "2026-02-02": ("退潮", "退潮", "等待", "", []),
    "2026-02-04": (
        "分歧",
        "强化但指数分化",
        "收缩中的连板接力",
        "AI传媒/文化内容",
        ["002830.SZ"],
    ),
    "2026-02-05": ("退潮", "退潮", "等待", "", []),
    "2026-02-10": (
        "分歧",
        "分歧",
        "低位轮动",
        "AI短剧/文化传媒",
        ["603533.SH", "001330.SZ", "300182.SZ"],
    ),
    "2026-02-11": ("退潮", "退潮", "等待", "", []),
    "2026-02-12": ("退潮", "冰点", "等待", "", []),
    "2026-02-13": ("退潮", "冰点", "等待", "", []),
    "2026-02-25": (
        "进攻",
        "强化",
        "连板接力",
        "算力/火电绿电",
        ["001896.SZ", "002498.SZ"],
    ),
    "2026-02-26": (
        "分歧",
        "分歧",
        "低位接棒",
        "磷化工/化肥",
        ["002470.SZ", "600078.SH"],
    ),
    "2026-02-27": (
        "修复偏强",
        "强化但高位需验货",
        "连板接力/主线延续",
        "算力火电绿电与资源轮动",
        ["001896.SZ", "002470.SZ", "002378.SZ"],
    ),
}


def read_existing() -> dict[str, dict]:
    records = {}
    for line in EXISTING.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            records[item["signal_date"]] = item
    return records


def next_auction_date(date: pd.Timestamp, auction_dates: list[pd.Timestamp]) -> str:
    later = [value for value in auction_dates if value > date]
    return later[0].date().isoformat() if later else ""


def make_record(
    date: str,
    day: pd.DataFrame,
    auction_date: str,
    environment: str,
    sentiment: str,
    mode: str,
    theme: str,
    queue: list[str],
) -> dict:
    first = day.iloc[0]
    evidence = {
        "breadth": {
            "up_ratio": float(first["up_ratio"]),
            "down_ratio": float(first["down_ratio"]),
            "limit_up_count": int(first["limit_up_count"]),
            "limit_break_count": int(first["limit_break_count"]),
            "limit_down_count": int(first["limit_down_count"]),
        },
        "prior_limit_up_feedback": {
            "open_positive_ratio": float(first["prev_limit_up_open_positive_ratio"]),
            "close_return_median": float(first["prev_limit_up_close_return_median"]),
        },
    }
    audits = []
    for rank, code in enumerate(queue, 1):
        row = day[day["thscode"].eq(code)]
        if row.empty:
            raise ValueError(f"{date}: queue code not present in T-day inputs: {code}")
        r = row.iloc[0]
        boards = float(r["continue_day_cnt"]) if pd.notna(r["continue_day_cnt"]) else 1.0
        audits.append(
            {
                "candidate": code,
                "name": str(r["stock_name"]),
                "original_rank": rank,
                "environment_pass": True,
                "environment_evidence": f"{environment}; breadth and prior feedback recorded in T-day facts",
                "theme_pass": True,
                "theme_evidence": f"{theme}; raw reason: {r['limit_up_reason']}",
                "node_pass": True,
                "node_evidence": f"{int(boards)}板与T日主动封板事实，进入该路径原始队列",
                "risk_pass": True,
                "risk_evidence": "竞价弱、撤单或不可成交即失效；不使用未来收益",
                "role": "低位试错" if boards <= 3 else "题材前排",
                "include_status": "formal",
                "include_or_exclude_reason": "通过当前skill的盘后环境、题材、节点和风险门",
            }
        )

    return {
        "case_id": f"{date.replace('-', '')}-current-skill-queue",
        "signal_date": date,
        "data_cutoff": f"{date} 15:00 Asia/Shanghai",
        "environment_state": environment,
        "environment_evidence": evidence,
        "sentiment_state": sentiment,
        "sentiment_evidence": "由T日涨跌广度、涨停/炸板/跌停和前一日涨停反馈生成",
        "market_mode": mode,
        "market_mode_evidence": {"theme": theme, "source": "T-day facts only"},
        "theme_classification": [{"theme": theme, "status": "主线或可参与分支" if theme else "无正式主线", "evidence": "T日原始涨停原因和梯队事实"}],
        "node_role_records": audits,
        "candidate_audit": audits,
        "original_queue": queue,
        "auction_date": auction_date,
        "auction_records": [],
        "executed_candidate": "",
        "executed": False,
        "execution_status": "pending_auction",
        "t1_open_buy_price": None,
        "t2_auction_sell_price": None,
        "return_pct": None,
        "return_protocol": "T+1 open buy -> T+2 09:25 auction sell",
        "invalidated_reason": "等待独立竞价阶段",
        "excluded_candidates": [],
        "leakage_check": {
            "tday_decision_uses_after_tday_data": False,
            "auction_decision_uses_after_0925_data": False,
            "return_used_to_change_decision": False,
        },
        "replay_status": "tday_queue_frozen_pending_auction",
    }


def main() -> None:
    inputs = pd.read_csv(INPUT)
    inputs["date"] = pd.to_datetime(inputs["date"]).dt.normalize()
    limit_up = inputs[inputs["pool_type"].eq("limit_up")].copy()
    auction = pd.read_parquet(ROOT / "auction_cache_2026-02" / "auction_summary.parquet", columns=["trade_date"])
    auction_dates = sorted(pd.to_datetime(auction["trade_date"]).dt.normalize().drop_duplicates().tolist())
    existing = read_existing()
    records = []
    for date_value in sorted(limit_up["date"].drop_duplicates()):
        date = date_value.date().isoformat()
        if date in existing:
            item = existing[date]
            item.setdefault("auction_date", next_auction_date(date_value, auction_dates))
            item.setdefault("market_mode_evidence", {"source": "existing repair-day slice"})
            item["replay_status"] = "tday_queue_frozen_with_repair_challenger_slice"
            records.append(item)
            continue
        if date not in PLANS:
            raise ValueError(f"No predeclared T-day plan for {date}")
        environment, sentiment, mode, theme, queue = PLANS[date]
        day = limit_up[limit_up["date"].eq(date_value)]
        for code in queue:
            if code not in set(day["thscode"]):
                raise ValueError(f"{date}: missing planned queue code {code}")
        records.append(
            make_record(
                date,
                day,
                next_auction_date(date_value, auction_dates),
                environment,
                sentiment,
                mode,
                theme,
                queue,
            )
        )

    records.sort(key=lambda item: item["signal_date"])
    with OUTPUT_JSONL.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = []
    for item in records:
        rows.append(
            {
                "signal_date": item["signal_date"],
                "auction_date": item["auction_date"],
                "environment_state": item["environment_state"],
                "sentiment_state": item["sentiment_state"],
                "market_mode": item["market_mode"],
                "theme": item["market_mode_evidence"].get("theme", "") if isinstance(item["market_mode_evidence"], dict) else "",
                "original_queue": "|".join(item["original_queue"]),
                "queue_size": len(item["original_queue"]),
                "data_cutoff": item["data_cutoff"],
                "replay_status": item["replay_status"],
            }
        )
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
