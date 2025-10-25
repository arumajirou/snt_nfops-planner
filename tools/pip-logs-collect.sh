#!/usr/bin/env bash
set -euo pipefail
mkdir -p pip-logs
if [ -f requirements.txt ]; then
  pip -vv install -r requirements.txt 2>&1 | tee pip-logs/pip_install_verbose.log
else
  pip -vv install -e . 2>&1 | tee pip-logs/pip_install_verbose.log || true
fi
