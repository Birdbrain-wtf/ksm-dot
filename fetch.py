#!/usr/bin/env python3
"""Daily KSM and DOT closing prices in USD since each began trading -> data.json and data.csv.

Runs on Birdbrain's box from cron (see README.md). Source: Yahoo Finance daily
chart API (KSM-USD from 12 Dec 2019, DOT-USD from 20 Aug 2020, post-redenomination).
Stdlib only. Writes atomically, keeps the last good file if a fetch fails.
"""
import json, os, sys, time, urllib.request, datetime as dt

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "data.json")

def series(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1500000000&period2={int(time.time())}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (birdbrain.wtf ksm-dot)"})
    r = json.load(urllib.request.urlopen(req, timeout=30))["chart"]["result"][0]
    out = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c:
            out[dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")] = round(c, 6)
    return out

ksm, dot = series("KSM-USD"), series("DOT-USD")
if len(ksm) < 2000 or len(dot) < 1800:
    sys.exit(f"too few rows (ksm {len(ksm)}, dot {len(dot)}), keeping the old file")
days = sorted(set(ksm) | set(dot))
data = {
    "source": "Yahoo Finance daily close, USD (KSM-USD, DOT-USD)",
    "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    "rows": [[d, ksm.get(d), dot.get(d)] for d in days],
}
tmp = OUT + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f, separators=(",", ":"))
os.replace(tmp, OUT)
csv_out = OUT[:-5] + ".csv"
with open(csv_out + ".tmp", "w") as f:
    f.write("date,ksm_usd,dot_usd\n")
    for d in days:
        f.write(f"{d},{ksm.get(d) if ksm.get(d) is not None else ''},{dot.get(d) if dot.get(d) is not None else ''}\n")
os.replace(csv_out + ".tmp", csv_out)
print(f"{OUT}: {len(days)} days, last {days[-1]}")
