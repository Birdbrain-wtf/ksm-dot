#!/usr/bin/env python3
"""Measure how fast KSM and DOT are being issued, straight from each chain.

Reads Balances.TotalIssuance and Timestamp.now on Kusama Asset Hub and Polkadot
Asset Hub at two blocks, then annualises the growth. Stdlib only, plain JSON-RPC
over HTTPS, so anyone can rerun it without installing anything.

  python3 issuance.py                      # the blocks the page was measured at
  python3 issuance.py --days 180           # fresh reading: latest block vs ~180 days back
  python3 issuance.py --kusama A B --polkadot C D   # any two blocks you choose
"""
import argparse, json, urllib.request, datetime as dt

# Storage keys are twox128("Balances")+twox128("TotalIssuance") and
# twox128("Timestamp")+twox128("Now"). Constant on every Substrate chain.
TOTAL_ISSUANCE = "0xc2261276cc9d1f8598ea4b6a74b15c2f57c875e4cff74148e4628f264b974c80"
TIMESTAMP_NOW = "0xf0c365c3cf59d671eb72da0e7a4113c49f1f0515f462cdcf84e0f1d6045dfcbb"

CHAINS = {
    "kusama": {"rpc": "https://kusama-asset-hub-rpc.polkadot.io", "decimals": 12, "unit": "KSM"},
    "polkadot": {"rpc": "https://polkadot-asset-hub-rpc.polkadot.io", "decimals": 10, "unit": "DOT"},
}
# The two blocks behind the figures on birdbrain.wtf/tools/ksm-dot (written by --pin).
BLOCKS = __file__.replace("issuance.py", "data/issuance-blocks.json")

def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, body, {"Content-Type": "application/json", "User-Agent": "birdbrain.wtf ksm-dot"})
    out = json.load(urllib.request.urlopen(req, timeout=30))
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]

def le_int(hexstr):
    return int.from_bytes(bytes.fromhex(hexstr[2:]), "little")

def read(chain, block):
    c = CHAINS[chain]
    h = rpc(c["rpc"], "chain_getBlockHash", [block])
    iss = le_int(rpc(c["rpc"], "state_getStorage", [TOTAL_ISSUANCE, h])) / 10 ** c["decimals"]
    ts = le_int(rpc(c["rpc"], "state_getStorage", [TIMESTAMP_NOW, h])) / 1000
    return {"block": block, "hash": h, "time": ts, "issuance": iss}

def head(chain):
    return int(rpc(CHAINS[chain]["rpc"], "chain_getHeader", [])["number"], 16)

def block_days_back(chain, end, days):
    target = read(chain, end)["time"] - days * 86400
    b, rate = end - int(days * 86400 / 6), 6.0
    for _ in range(6):
        t = read(chain, b)["time"]
        b = max(1, b + round((target - t) / rate))
        rate = (read(chain, end)["time"] - t) / max(1, end - b) or 6.0
    return b

def report(chain, a, b):
    x, y = read(chain, a), read(chain, b)
    days = (y["time"] - x["time"]) / 86400
    grown = y["issuance"] - x["issuance"]
    rate = (y["issuance"] / x["issuance"]) ** (365 / days) - 1
    u = CHAINS[chain]["unit"]
    fmt = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"{chain}: block {a} ({fmt(x['time'])}) {x['issuance']:,.2f} {u}")
    print(f"{' ' * len(chain)}  block {b} ({fmt(y['time'])}) {y['issuance']:,.2f} {u}")
    print(f"{' ' * len(chain)}  {days:.1f} days, +{grown:,.0f} {u}, about {grown / days * 365:,.0f} {u} a year, {rate * 100:.2f}% a year compounded\n")
    return {"from": x, "to": y}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=float, help="fresh reading: latest block against this many days back")
    p.add_argument("--kusama", nargs=2, type=int)
    p.add_argument("--polkadot", nargs=2, type=int)
    p.add_argument("--pin", action="store_true", help="save the blocks used to data/issuance-blocks.json")
    a = p.parse_args()
    out = {}
    for chain in CHAINS:
        if getattr(a, chain):
            blocks = getattr(a, chain)
        elif a.days:
            end = head(chain)
            blocks = [block_days_back(chain, end, a.days), end]
        else:
            blocks = json.load(open(BLOCKS))[chain]
        out[chain] = report(chain, *blocks)
    if a.pin:
        json.dump({c: [v["from"]["block"], v["to"]["block"]] for c, v in out.items()},
                  open(BLOCKS, "w"), indent=2)
