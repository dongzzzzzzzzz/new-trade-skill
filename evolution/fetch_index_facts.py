#!/usr/bin/env python3
"""Fetch point-in-time index facts used by the replay environment step."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


INDICES = {
    "shanghai_composite": "1.000001",
    "shenzhen_component": "0.399001",
    "chinext": "0.399006",
}


def fetch(secid: str, start: str, end: str) -> dict:
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        "klt": "101",
        "fqt": "1",
        "beg": start,
        "end": end,
    }
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("rc") != 0 or not payload.get("data"):
        raise RuntimeError(f"index request failed for {secid}: {payload}")
    return {"url": url, "payload": payload}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="20260101")
    parser.add_argument("--end", default="20260131")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = {}
    for name, secid in INDICES.items():
        records[name] = {"secid": secid, **fetch(secid, args.start, args.end)}
        time.sleep(0.2)

    output = {
        "source": "eastmoney_push2his",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "kline_fields": "date,open,close,high,low,volume,amount,change_pct",
        "indices": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
