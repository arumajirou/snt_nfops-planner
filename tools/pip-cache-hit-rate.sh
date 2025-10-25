#!/usr/bin/env bash
set -euo pipefail
LOG="${1:-pip-logs/pip_install_verbose.log}"
mkdir -p pip-logs
if [ ! -f "$LOG" ]; then
  echo "no log: $LOG" | tee pip-logs/cache_hit_rate.txt
  exit 0
fi
CACHED=$(grep -E "Using cached" "$LOG" | wc -l || true)
DOWN=$(grep -E "Downloading" "$LOG" | wc -l || true)
TOTAL=$((CACHED+DOWN))
RATE="0.0"
if [ "$TOTAL" -gt 0 ]; then RATE=$(awk -v c=$CACHED -v t=$TOTAL 'BEGIN{printf "%.1f", (c/t)*100}'); fi
{
  echo "cached=$CACHED"
  echo "downloading=$DOWN"
  echo "total=$TOTAL"
  echo "hit_rate_pct=$RATE"
} | tee pip-logs/cache_hit_rate.txt
