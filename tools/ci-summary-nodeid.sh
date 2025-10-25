#!/usr/bin/env bash
set -euo pipefail

# ジョブログを標準入力で受け取り、FAILED/ERROR collecting の最初の nodeid を抽出
nodeid=$(
  awk '
    /^FAILED[[:space:]]+/           {print $2; exit}
    /^ERROR collecting[[:space:]]+/ {print $3; exit}
  '
)

: "${GITHUB_STEP_SUMMARY:?}"

{
  echo "### pytest failure summary"
  if [ -n "${nodeid:-}" ]; then
    echo ""
    echo "- nodeid: \`${nodeid}\`"
    echo "- local reproduce:"
    echo "  \`\`\`bash"
    echo "  pytest -vv -n 0 --maxfail=1 \"${nodeid}\""
    echo "  \`\`\`"
  else
    echo ""
    echo "- no FAILED/ERROR collecting lines; likely pre-collection failure"
  fi
} >> "$GITHUB_STEP_SUMMARY"
