#!/usr/bin/env bash
set -euo pipefail
mkdir -p pip-logs
if [ -f requirements.txt ]; then
  pip -vv install -r requirements.txt 2>&1 | tee pip-logs/pip_install_verbose.log
else
  # fallback: プロジェクト自体を -e で入れてログ確保（失敗してもログは残す）
  pip -vv install -e . 2>&1 | tee pip-logs/pip_install_verbose.log || true
fi
