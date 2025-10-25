#!/usr/bin/env bash
set -euo pipefail
mkdir -p pip-logs
pip -v install -r requirements.txt 2>&1 | tee pip-logs/pip_install_verbose.log || true
