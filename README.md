# KSM and DOT, before and after the cap

The data and the sums behind [birdbrain.wtf/tools/ksm-dot](https://birdbrain.wtf/tools/ksm-dot),
so anyone can check them.

On 14 March 2026 Polkadot cut new DOT by more than half and capped the supply at 2.1 billion
([referendum 1710](https://polkadot.subsquare.io/referenda/1710)). Kusama kept issuing at about
10% a year. On 13 November 2026 Lederstrumpf wrote on the
[Polkadot forum](https://forum.polkadot.network/t/proposal-discussion-adapting-kusama-to-demand-and-its-jam-future/17141/23)
that KSM trades closely with DOT, that KSM/DOT is doing better than before the cap, and that KSM
held its ground. The page tests those three claims against daily prices. This repository lets you
test the page.

## Check it yourself

Everything is Python 3 with nothing to install.

```sh
git clone https://github.com/Birdbrain-wtf/ksm-dot && cd ksm-dot
python3 verify.py        # recompute every price figure on the page from the live data
python3 crosscheck.py    # compare the prices with CoinGecko, a second source
python3 issuance.py      # read each chain's total supply at the two blocks the page used
python3 issuance.py --days 180   # or take a fresh reading up to the latest block
```

`verify.py data/data.csv --as-of 2026-11-13` reproduces the figures as first published.

## What is here

| File | What it does |
| --- | --- |
| `data/data.csv`, `data/data.json` | Daily US dollar closes, KSM from 12 Dec 2019, DOT from 20 Aug 2020 (after its redenomination). Same rows in two formats. Updated daily |
| `data/issuance-blocks.json` | The Asset Hub block numbers the issuance figures were read at |
| `fetch.py` | Pulls the prices from Yahoo Finance and writes both data files |
| `verify.py` | The page's arithmetic, line for line, in Python |
| `crosscheck.py` | Matches the last 365 days against CoinGecko |
| `issuance.py` | Reads `Balances.TotalIssuance` and `Timestamp.now` from each Asset Hub over public RPC |
| `index.html` | The page itself. All of its sums run in the browser, in the `<script>` at the bottom |
| `daily.sh` | What Birdbrain's server runs at 06:15 UTC each day to refresh the page |
| `.github/workflows/daily.yml` | At 06:45 UTC, copies what the page is serving into `data/`, reruns `verify.py` and commits |

The commit history of `data/` is the record of what the page showed on each day.

## How the numbers are made

- **KSM in DOT** is the KSM price divided by the DOT price on the same day. The ratio shows their
  relative price. It does not remove every market influence or isolate the effect of issuance.
- **How closely they move** is the Pearson correlation of daily log returns, ln(price today /
  price yesterday), for each coin over the same days.
- **Before and after** are plain averages of KSM in DOT over the same number of months either side
  of 14 March 2026. The 14 March itself counts as after.
- **The longer baseline** is the average over the twelve months before the cap was proposed
  (15 August 2024 to 14 August 2025).
- **Issuance** is the growth in total supply between two blocks about 179 days apart, compounded
  to a yearly rate.

## What the numbers said on 13 November 2026

| | |
| --- | --- |
| Correlation of daily moves, last two years | 0.80 (0.77 since the cap) |
| KSM in DOT, eight months before the cap | 3.65 average |
| KSM in DOT, since the cap | 3.77 average, +3% |
| KSM in DOT on 14 March 2026 | 3.12 |
| KSM in DOT on 13 November 2026 | 3.63, +16% since the cap |
| KSM in DOT, year before the cap was proposed | 4.12 average. The months since the cap sit 8% below it |
| Lowest ever | 2.92 on 28 February 2026, two weeks before the cap |
| Kusama issuance | 10.5% a year, about 1.87 million KSM, blocks 16,896,724 to 23,766,227 |
| Polkadot issuance | 3.4% a year, about 56 million DOT, blocks 15,904,935 to 23,079,279 |

## Limits

- Eight months is short, and prices answer to many things at once. This cannot show that issuance
  does not matter. It can show whether the effect people predicted is visible yet.
- Where you start counting changes the answer. From the day the cap took effect, KSM has gained on
  DOT. Against the year before the cap was proposed, it has not. The page shows both.
- The last row is the price so far today. It settles into a close the next day.
- Yahoo and CoinGecko agree to 0.1% on a typical day (0.4% at the 95th percentile). On a handful of
  very volatile days they differ by more, because each takes its daily price at a slightly
  different moment. One day moves an eight-month average by a few hundredths of a percent.
- The issuance figures on the page are a fixed reading, not live. `issuance.py --days 180` gives
  a fresh one.

## Sources and licence

Prices are Yahoo Finance's, reproduced here so the sums can be checked. Supply figures are read
directly from Kusama Asset Hub and Polkadot Asset Hub. The code is Apache-2.0.

Birdbrain is a Decent initiative that tests, learns and educates in public. Found a mistake?
Open an issue.
