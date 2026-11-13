#!/bin/sh
# Runs on Birdbrain's box from /etc/cron.d/ksm-dot at 06:15 UTC. Refreshes the prices the
# page reads. At 06:45 a GitHub Action in this repo copies what the page then serves into
# data/ and commits it (.github/workflows/daily.yml), so no key for GitHub lives on the box.
set -e
cd /opt/ksm-dot
git pull -q --ff-only
python3 fetch.py /var/www/birdbrain-static/tools/ksm-dot/data.json
