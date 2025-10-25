#!/usr/bin/env bash
set -euo pipefail
REMOTE="${REMOTE:-origin}"
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"

# リポ推定
url=$(git remote get-url "$REMOTE")
[[ "$url" =~ github.com[:/](.+)/(.+)\.git ]] || { echo "not GitHub: $url" >&2; exit 2; }
OWNER="${OWNER:-${BASH_REMATCH[1]}}"; REPO="${REPO:-${BASH_REMATCH[2]}}"

git fetch "$REMOTE" "$BR" --prune >/dev/null
HEAD_SHA=$(git rev-parse "$BR")

echo "== Workflows =="
gh workflow list -R "$OWNER/$REPO" || true

echo "== Latest runs on $BR =="
gh run list -R "$OWNER/$REPO" --branch "$BR" --limit 10 --json databaseId,workflowName,headSha,status,conclusion,htmlUrl || true

echo "== Check-runs for HEAD ($HEAD_SHA) =="
gh api -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/commits/$HEAD_SHA/check-runs" \
  -q '.check_runs[] | {name: .name, status: .status, conclusion: .conclusion, app: .app.slug}' || true

echo "== Status contexts (legacy API) =="
gh api "/repos/$OWNER/$REPO/commits/$HEAD_SHA/status" \
  -q '.statuses[] | {context, state, description}' || true

echo "TIP: 上記の name/context を required_status_checks に設定すると保護要件になります。"
