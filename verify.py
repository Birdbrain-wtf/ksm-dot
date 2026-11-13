#!/usr/bin/env python3
"""Recompute every price figure on birdbrain.wtf/tools/ksm-dot from the raw data.

The page does its sums in your browser. This is the same arithmetic in Python,
stdlib only, so you can check it without trusting the page.

  python3 verify.py                    # the live data from birdbrain.wtf
  python3 verify.py data/data.csv      # a local copy (CSV or JSON)
  python3 verify.py --as-of 2026-11-13 # stop the data at a date, to reproduce an old reading
"""
import csv, json, math, sys, urllib.request, argparse, datetime as dt

LIVE = "https://birdbrain.wtf/tools/ksm-dot/data.json"
PROPOSED, APPROVED, CAP = "2025-08-15", "2025-09-14", "2026-03-14"   # Polkadot referendum 1710

def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "birdbrain.wtf ksm-dot verify"})
        rows = json.load(urllib.request.urlopen(req, timeout=30))["rows"]
    elif src.endswith(".json"):
        rows = json.load(open(src))["rows"]
    else:
        rows = [[r["date"], float(r["ksm_usd"]) if r["ksm_usd"] else None, float(r["dot_usd"]) if r["dot_usd"] else None]
                for r in csv.DictReader(open(src))]
    return rows

def add_months(s, m):
    d = dt.date.fromisoformat(s)
    y, mo = divmod(d.month - 1 + m, 12)
    return dt.date(d.year + y, mo + 1, min(d.day, 28)).isoformat()   # every date used here is the 13th-15th

def corr(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return sab / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("src", nargs="?", default=LIVE)
    p.add_argument("--as-of")
    a = p.parse_args()
    rows = load(a.src)
    # Days where both prices exist; KSM in DOT is simply KSM_USD / DOT_USD.
    both = [{"d": d, "k": k, "p": q, "r": k / q} for d, k, q in rows if k and q and (not a.as_of or d <= a.as_of)]
    for i in range(1, len(both)):
        both[i]["lk"] = math.log(both[i]["k"] / both[i - 1]["k"])
        both[i]["lp"] = math.log(both[i]["p"] / both[i - 1]["p"])
    last = both[-1]
    mean = lambda lo, hi: (lambda v: sum(v) / len(v))([x["r"] for x in both if lo <= x["d"] < hi])
    on = lambda d: [x for x in both if x["d"] <= d][-1]

    print(f"Data: {len(both)} days with both prices, {both[0]['d']} to {last['d']}\n")

    two_y = add_months(last["d"], -24)
    w = [x for x in both if x["d"] > two_y and "lk" in x]
    c2y = corr([x["lk"] for x in w], [x["lp"] for x in w])
    w = [x for x in both if x["d"] >= CAP and "lk" in x]
    cap_c = corr([x["lk"] for x in w], [x["lp"] for x in w])
    print("1. KSM moves with DOT")
    print(f"   correlation of daily log returns, {two_y} to {last['d']}: {c2y:.2f}")
    print(f"   same, since {CAP}: {cap_c:.2f}\n")

    months = max(1, round((dt.date.fromisoformat(last["d"]) - dt.date.fromisoformat(CAP)).days / 30.44))
    before, after = mean(add_months(CAP, -months), CAP), mean(CAP, "9999")
    print("2. KSM/DOT is doing better than before the cap")
    print(f"   average KSM in DOT, {months} months before {CAP}: {before:.2f}")
    print(f"   average KSM in DOT, since {CAP}: {after:.2f}")
    print(f"   change: {(after / before - 1) * 100:+.1f}%\n")

    oc, pre = on(CAP), mean(add_months(PROPOSED, -12), PROPOSED)
    low = min(both, key=lambda x: x["r"])
    print("3. KSM held its ground against DOT")
    print(f"   KSM in DOT on {oc['d']}: {oc['r']:.2f}, on {last['d']}: {last['r']:.2f} ({(last['r'] / oc['r'] - 1) * 100:+.1f}%)")
    print(f"   average in the 12 months before the cap was proposed: {pre:.2f} (today is {(last['r'] / pre - 1) * 100:+.1f}%)")
    print(f"   average since the cap against that year: {(after / pre - 1) * 100:+.1f}%")
    print(f"   lowest ever: {low['r']:.2f} on {low['d']}\n")

    print("Slider on the page (months either side of the cap):")
    for m in range(1, months + 1):
        b, f = mean(add_months(CAP, -m), CAP), mean(CAP, add_months(CAP, m))
        print(f"   {m}: before {b:.2f}  after {f:.2f}  change {(f / b - 1) * 100:+.1f}%")

if __name__ == "__main__":
    main()
