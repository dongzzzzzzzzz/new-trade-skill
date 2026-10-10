#!/usr/bin/env python3
"""Fetch index OHLC facts from Tencent's public daily-kline endpoint.

Tencent returns index volume but not turnover amount. The output keeps the
existing replay schema by storing volume in the amount slot and explicitly
marks it as a proxy. Market-wide turnover remains sourced from stock bars.
"""

from __future__ import annotations

import argparse
import json
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


INDICES = {
    "shanghai_composite": "sh000001",
    "shenzhen_component": "sz399001",
    "chinext": "sz399006",
}


def fetch(symbol: str, start: str, end: str) -> dict:
    params = {
        "param": f"{symbol},day,{start[:4]}-{start[4:6]}-{start[6:]},{end[:4]}-{end[4:6]}-{end[6:]},1000,qfq",
    }
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    # The local desktop proxy presents a self-signed certificate to this
    # public read-only endpoint; no credentials or user data are transmitted.
    with urlopen(request, timeout=20, context=ssl._create_unverified_context()) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("code") != 0 or not payload.get("data", {}).get(symbol):
        raise RuntimeError(f"Tencent index request failed for {symbol}: {payload}")
    return {"url": url, "payload": payload}


def normalize_payload(record: dict, symbol: str) -> dict:
    rows = record["payload"]["data"][symbol]["day"]
    normalized = []
    previous_close = None
    for row in rows:
        date, open_, close, high, low, volume = row
        close_value = float(close)
        change_pct = 0.0 if previous_close in (None, 0.0) else (close_value / previous_close - 1.0) * 100.0
        normalized.append(
            ",".join(
                [
                    date,
                    open_,
                    close,
                    high,
                    low,
                    volume,
                    volume,
                    f"{change_pct:.8f}",
                ]
            )
        )
        previous_close = close_value
    payload = {"data": {"klines": normalized}}
    return {"url": record["url"], "payload": payload}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="20260101")
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = {}
    for name, symbol in INDICES.items():
        raw = fetch(symbol, args.start, args.end)
        records[name] = {
            "symbol": symbol,
            **normalize_payload(raw, symbol),
        }
        time.sleep(0.2)

    output = {
        "source": "tencent_ifzq_fqkline",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "kline_fields": "date,open,close,high,low,volume,index_volume_proxy,change_pct",
        "index_amount_semantics": "index_volume_proxy; Tencent endpoint does not expose turnover amount",
        "indices": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
