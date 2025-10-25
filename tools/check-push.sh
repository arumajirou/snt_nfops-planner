#!/usr/bin/env bash
set -euo pipefail

WF="${WF:-CI}"              # workflow名 (デフォルト: CI)
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"
REMOTE="${REMOTE:-origin}"

# リポ名推定
url=$(git remote get-url "$REMOTE")
if [[ "$url" =~ github.com[:/](.+)/(.+)\.git ]]; then
  OWNER="${OWNER:-${BASH_REMATCH[1]}}"
  REPO="${REPO:-${BASH_REMATCH[2]}}"
else
  echo "origin が GitHub ではありません: $url" >&2; exit 2
fi

git fetch "$REMOTE" "$BR" --prune

LOCAL_SHA=$(git rev-parse "$BR")
REMOTE_SHA=$(git ls-remote --heads "$REMOTE" "$BR" | awk '{print $1}')
read BEHIND AHEAD < <(git rev-list --left-right --count "$REMOTE/$BR...$BR")

echo "branch=$BR"
echo "local_sha=$LOCAL_SHA"
echo "remote_sha=$REMOTE_SHA"
echo "ahead=$AHEAD"
echo "behind=$BEHIND"

if [[ "$LOCAL_SHA" = "$REMOTE_SHA" && "$AHEAD" = "0" && "$BEHIND" = "0" ]]; then
  echo "verdict=OK"
else
  echo "verdict=NG"
  exit 1
fi

# PR 状態
PR_JSON=$(gh pr list -R "$OWNER/$REPO" --head "$BR" --state all --json number,state,isDraft,mergeable 2>/dev/null || true)
echo "pr=$(jq -c '.[0]' <<<"$PR_JSON" 2>/dev/null || echo null)"

# 直近 CI
RUN_JSON=$(gh run list -R "$OWNER/$REPO" --workflow "$WF" --branch "$BR" --limit 1 \
  --json status,conclusion,headSha,displayTitle,htmlUrl 2>/dev/null || true)
echo "ci=$(jq -c '.[0]' <<<"$RUN_JSON" 2>/dev/null || echo null)"
