#!/usr/bin/env bash
set -euo pipefail
REMOTE="${REMOTE:-origin}"
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"
LIMIT="${LIMIT:-5}"

url=$(git remote get-url "$REMOTE")
[[ "$url" =~ github.com[:/](.+)/(.+)\.git ]] || { echo "not GitHub: $url" >&2; exit 2; }
OWNER="${OWNER:-${BASH_REMATCH[1]}}"; REPO="${REPO:-${BASH_REMATCH[2]}}"

RUNS_JSON=$(gh run list -R "$OWNER/$REPO" --branch "$BR" --limit "$LIMIT" \
  --json databaseId,workflowName,headSha,status,conclusion,url 2>/dev/null || echo "[]")
echo "== recent runs =="
echo "$RUNS_JSON" | jq -c '.[] | {run_id:.databaseId, workflow:.workflowName, status, conclusion, url, head:.headSha}'

RID=$(echo "$RUNS_JSON" | jq -r '[.[] | select(.conclusion=="failure")] | .[0].databaseId // empty')
if [[ -n "$RID" ]]; then
  echo "== failed run detail (run_id=$RID) =="
  gh run view -R "$OWNER/$REPO" "$RID" --json jobs 2>/dev/null \
    | jq -c '.jobs[] | {job:.name, status:.status, conclusion:.conclusion,
         failed_steps:[.steps[] | select(.conclusion=="failure") | {name:.name, number:.number}] }'
else
  echo "== no failed runs found =="
fi
