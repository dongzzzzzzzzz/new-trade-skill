#!/usr/bin/env python3
"""Freeze May 2026 queues from T-day facts using the current skill."""

from __future__ import annotations

import build_march_tday_queue_freeze as base


base.INPUT = base.ROOT / "replay_inputs_2026-05.csv"
base.OUTPUT_JSONL = base.ROOT / "replay_current_skill_tday_queue_2026-05.jsonl"
base.OUTPUT_CSV = base.ROOT / "queue_freeze_current_skill_2026-05.csv"

# These are T-day-only decisions. Broad or unrelated clusters remain waiting;
# formal queues require a concrete catalyst/industry relationship and a
# compatible environment.
base.PLANS = {
    "2026-05-06": ("进攻", "强化", "锂电固态材料主线", "锂盐/固态电池/电池材料", ["603399.SH", "603937.SH", "002805.SZ"]),
    "2026-05-07": ("进攻", "强化", "算力液冷接力", "算力/液冷/数据中心", ["600673.SH", "603158.SH", "000818.SZ"]),
    "2026-05-08": ("进攻", "强化", "算力通信主线", "算力租赁/光纤/数据中心", ["002929.SZ", "603636.SH", "002491.SZ"]),
    "2026-05-11": ("修复", "强化", "光通信与PCB接力", "光模块/PCB/数据中心", ["603459.SH", "002491.SZ", "603738.SH"]),
    "2026-05-12": ("退潮", "退潮", "等待", "", []),
    "2026-05-13": ("修复", "强化", "绿电央企主线", "绿电/火电/储能", ["601991.SH", "600396.SH", "000601.SZ"]),
    "2026-05-14": ("退潮", "冰点", "等待", "", []),
    "2026-05-15": ("退潮", "退潮", "等待", "", []),
    "2026-05-18": ("分歧", "退潮转分歧", "等待", "", []),
    "2026-05-19": ("修复", "修复", "算力液冷主线", "液冷/算力/数据中心", ["002421.SZ", "002272.SZ", "300657.SZ"]),
    "2026-05-20": ("退潮", "分歧", "等待", "", []),
    "2026-05-21": ("退潮", "退潮", "等待", "", []),
    "2026-05-22": ("进攻", "修复强化", "AI硬件主线", "AI算力/PCB/服务器", ["000636.SZ", "002938.SZ", "603661.SH"]),
    "2026-05-25": ("分歧", "分歧", "等待", "", []),
    "2026-05-26": ("退潮", "退潮", "等待", "", []),
    "2026-05-27": ("退潮", "冰点", "等待", "", []),
    "2026-05-28": ("修复", "修复", "PCB与算力硬件", "PCB/光模块/AI服务器", ["002579.SZ", "603011.SH"]),
    "2026-05-29": ("退潮", "退潮", "等待", "", []),
}


if __name__ == "__main__":
    base.main()
