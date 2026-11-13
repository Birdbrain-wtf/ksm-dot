#!/bin/sh
# Runs on Birdbrain's box from /etc/cron.d/ksm-dot. Refreshes the prices the page reads,
# then commits the same files to github.com/Birdbrain-wtf/ksm-dot so every day's data
# has a public, dated history that nobody can quietly rewrite.
set -e
REPO=/opt/ksm-dot
WEB=/var/www/birdbrain-static/tools/ksm-dot
cd "$REPO"
git pull -q --ff-only
python3 fetch.py "$WEB/data.json"
cp "$WEB/data.json" "$WEB/data.csv" data/
git add data/data.json data/data.csv
if ! git diff --cached --quiet; then
  git commit -q -m "Prices to $(tail -1 data/data.csv | cut -d, -f1)"
  git push -q
fi
