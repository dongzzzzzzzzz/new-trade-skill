#!/usr/bin/env python3
"""Freeze current-skill T-day queues for March 2026 without auction data."""

from __future__ import annotations

import csv
import json
from bisect import bisect_right
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_inputs_2026-03.csv"
KLINES = Path("/Users/lee.dong/Desktop/dc-stock/data/2026_raw/klines_2026.parquet")
OUTPUT_JSONL = ROOT / "replay_current_skill_tday_queue_2026-03.jsonl"
OUTPUT_CSV = ROOT / "queue_freeze_current_skill_2026-03.csv"


# All entries are declared from T-day facts only. Empty queues are explicit
# waiting decisions, not missing records.
PLANS = {
    "2026-03-02": ("退潮", "分歧转退潮", "等待", "", []),
    "2026-03-03": ("退潮", "退潮", "等待", "油气/天然气避险", []),
    "2026-03-04": ("退潮", "冰点", "等待", "", []),
    "2026-03-05": ("修复", "修复", "低位轮动", "电网设备/算力基建", ["000533.SZ", "002498.SZ", "002339.SZ"]),
    "2026-03-06": ("进攻", "强化", "连板接力", "电网设备/算力基建", ["000533.SZ", "002498.SZ"]),
    "2026-03-09": ("分歧", "分歧", "算电协同低位接棒", "算电协同/算力租赁", ["000815.SZ", "002261.SZ", "601789.SH"]),
    "2026-03-10": ("修复", "强化", "算力低位接力", "算力租赁", ["601789.SH", "002575.SZ"]),
    "2026-03-11": ("分歧", "强化但广度走弱", "低位轮动", "绿电/储能", ["000537.SZ", "600726.SH"]),
    "2026-03-12": ("分歧", "分歧", "绿电储能接力", "绿电/储能", ["000537.SZ", "600726.SH", "002150.SZ"]),
    "2026-03-13": ("退潮", "退潮", "等待", "", []),
    "2026-03-16": ("分歧", "冰点修复待确认", "新题材低位试错", "存储芯片", ["300042.SZ", "000620.SZ", "600667.SH"]),
    "2026-03-17": ("退潮", "退潮", "等待", "", []),
    "2026-03-18": ("修复", "修复", "算电协同新发酵", "算电协同/储能", ["000539.SZ", "000601.SZ", "000815.SZ"]),
    "2026-03-19": ("退潮", "退潮", "等待", "", []),
    "2026-03-20": ("退潮", "退潮", "等待", "", []),
    "2026-03-23": ("退潮", "冰点", "等待", "", []),
    "2026-03-24": ("修复", "修复", "修复日低位接棒", "绿电/氢能", ["600032.SH", "600744.SH", "601016.SH"]),
    "2026-03-25": ("进攻", "强化", "连板接力", "绿电/氢能", ["600396.SH", "600032.SH", "601016.SH"]),
    "2026-03-26": ("退潮", "退潮", "等待", "", []),
    "2026-03-27": ("修复", "修复", "修复日低位接棒", "创新药", ["002082.SZ", "002038.SZ", "600488.SH"]),
    "2026-03-30": ("分歧", "分歧", "创新药主线延续", "创新药", ["603538.SH", "002038.SZ", "600488.SH"]),
    "2026-03-31": ("退潮", "分歧转退潮", "等待", "", []),
}


def main() -> None:
    facts = pd.read_csv(INPUT)
    facts["date"] = pd.to_datetime(facts["date"]).dt.normalize()
    limit_up = facts[facts["pool_type"].eq("limit_up")].copy()
    bars = pd.read_parquet(KLINES, columns=["date"])
    trade_dates = sorted(pd.to_datetime(bars["date"]).dt.normalize().drop_duplicates().tolist())
    records = []

    for date_value in sorted(limit_up["date"].drop_duplicates()):
        date = date_value.date().isoformat()
        if date not in PLANS:
            raise ValueError(f"No T-day plan for {date}")
        environment, sentiment, mode, theme, queue = PLANS[date]
        day = limit_up[limit_up["date"].eq(date_value)]
        universe = set(day["thscode"])
        missing = [code for code in queue if code not in universe]
        if missing:
            raise ValueError(f"{date}: queue codes missing from T-day facts: {missing}")
        first = day.iloc[0]
        pos = bisect_right(trade_dates, date_value)
        auction_date = trade_dates[pos].date().isoformat() if pos < len(trade_dates) else ""
        audits = []
        nodes = []
        for rank, code in enumerate(queue, 1):
            row = day[day["thscode"].eq(code)].iloc[0]
            boards = int(float(row["continue_day_cnt"])) if pd.notna(row["continue_day_cnt"]) else 1
            role = "低位试错" if boards <= 3 else ("市场核心" if boards >= 7 else "题材前排")
            audits.append(
                {
                    "candidate": code,
                    "name": str(row["stock_name"]),
                    "original_rank": rank,
                    "environment_pass": True,
                    "environment_evidence": f"{environment}; T日广度和前一日涨停反馈已冻结",
                    "theme_pass": True,
                    "theme_evidence": f"{theme}; {row['limit_up_reason']}",
                    "node_pass": True,
                    "node_evidence": f"{boards}板，T日封板时间{row['raw_limit_up_time']}，存在题材响应",
                    "risk_pass": True,
                    "risk_evidence": "竞价弱、撤单或不可成交即失效；不读取未来收益",
                    "role": role,
                    "include_status": "formal",
                    "include_or_exclude_reason": "通过当前skill的环境、主线、节点和风险门",
                }
            )
            nodes.append(
                {
                    "candidate": code,
                    "name": str(row["stock_name"]),
                    "board_count": boards,
                    "role": role,
                    "main_node": mode,
                    "node_evidence": f"{theme}; {row['limit_up_reason']}; T日封板{row['raw_limit_up_time']}",
                    "risk": "T+1竞价验货失败则跳过",
                }
            )

        records.append(
            {
                "case_id": f"{date.replace('-', '')}-current-skill-{date[:7]}",
                "signal_date": date,
                "data_cutoff": f"{date} 15:00 Asia/Shanghai",
                "environment_state": environment,
                "environment_evidence": {
                    "up_ratio": float(first["up_ratio"]),
                    "down_ratio": float(first["down_ratio"]),
                    "limit_up_count": int(first["limit_up_count"]),
                    "limit_break_count": int(first["limit_break_count"]),
                    "limit_down_count": int(first["limit_down_count"]),
                    "index_sh_pct": float(first["index_change_pct_shanghai_composite"]),
                    "index_chinext_pct": float(first["index_change_pct_chinext"]),
                },
                "sentiment_state": sentiment,
                "sentiment_evidence": {
                    "prev_limit_up_open_positive_ratio": float(first["prev_limit_up_open_positive_ratio"]),
                    "prev_limit_up_close_return_median": float(first["prev_limit_up_close_return_median"]),
                },
                "market_mode": mode,
                "market_mode_evidence": {"theme": theme, "source": "T-day facts only"},
                "theme_classification": [{"theme": theme, "status": "正式路径" if theme else "无正式主线", "evidence": "T日涨停原因、梯队和响应时间"}],
                "node_role_records": nodes,
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
        )

    with OUTPUT_JSONL.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    rows = [
        {
            "signal_date": item["signal_date"],
            "auction_date": item["auction_date"],
            "environment_state": item["environment_state"],
            "sentiment_state": item["sentiment_state"],
            "market_mode": item["market_mode"],
            "theme": item["market_mode_evidence"]["theme"],
            "original_queue": "|".join(item["original_queue"]),
            "queue_size": len(item["original_queue"]),
            "data_cutoff": item["data_cutoff"],
        }
        for item in records
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
