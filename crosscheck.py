#!/usr/bin/env python3
"""Check the Yahoo Finance prices against a second source, CoinGecko.

CoinGecko's free API gives the last 365 days without a key. Its daily point is
taken at 00:00 UTC, Yahoo's close at 23:59 UTC the day before, so the two are
matched one day apart. Prints the median and 95th-percentile gap.

  python3 crosscheck.py                 # against the live data on birdbrain.wtf
  python3 crosscheck.py data/data.json  # against a local copy
"""
import json, sys, time, urllib.request, urllib.error, datetime as dt

def get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": "birdbrain.wtf ksm-dot crosscheck"})
    for n in range(tries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code != 429 or n == tries - 1:
                raise
            time.sleep(20 * (n + 1))   # CoinGecko's free tier rate-limits; wait and retry

src = sys.argv[1] if len(sys.argv) > 1 else "https://birdbrain.wtf/tools/ksm-dot/data.json"
rows = get(src)["rows"] if src.startswith("http") else json.load(open(src))["rows"]
ours = {d: (k, p) for d, k, p in rows}

for i, (coin, col, unit) in enumerate([("kusama", 0, "KSM"), ("polkadot", 1, "DOT")]):
    if i:
        time.sleep(3)   # be polite to the free tier
    cg = get(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=365&interval=daily")["prices"]
    gaps = []
    for ms, price in cg:
        if ms % 86_400_000:
            continue   # CoinGecko's last point is the live price, not a daily one
        d = (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc) - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        if d in ours and ours[d][col]:
            gaps.append((abs(ours[d][col] / price - 1), d))
    gaps.sort()
    print(f"{unit}: {len(gaps)} days compared, median gap {gaps[len(gaps) // 2][0] * 100:.2f}%, "
          f"95th percentile {gaps[int(len(gaps) * .95)][0] * 100:.2f}%, largest {gaps[-1][0] * 100:.2f}% on {gaps[-1][1]}")
