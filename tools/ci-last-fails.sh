#!/usr/bin/env bash
set -euo pipefail
REMOTE="${REMOTE:-origin}"
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"
LIMIT="${LIMIT:-5}"

url=$(git remote get-url "$REMOTE")
[[ "$url" =~ github\.com[:/](.+)/(.+)\.git ]] || { echo "not GitHub: $url" >&2; exit 2; }
OWNER="${OWNER:-${BASH_REMATCH[1]}}"; REPO="${REPO:-${BASH_REMATCH[2]}}"

RUNS_JSON=$(gh run list -R "$OWNER/$REPO" --branch "$BR" --limit "$LIMIT" \
  --json databaseId,workflowName,headSha,status,conclusion,url 2>/dev/null || echo "[]")
echo "== recent runs =="
echo "$RUNS_JSON" | jq -c '.[] | {run_id:.databaseId, workflow:.workflowName, status, conclusion, url, head:.headSha}'

RID=$(echo "$RUNS_JSON" | jq -r '[.[] | select(.conclusion=="failure" or .status=="in_progress" or .status=="queued")] | .[0].databaseId // empty')
if [[ -n "$RID" ]]; then
  echo "== failed run detail (run_id=$RID) =="
  gh api -H "Accept: application/vnd.github+json" \
    "/repos/$OWNER/$REPO/actions/runs/$RID/jobs?per_page=100" --paginate \
    -q '.jobs[] | {job_id:.id, job:.name, status:.status, conclusion:.conclusion, url:.html_url,
        failed_steps: ([.steps[] | select(.conclusion=="failure") | {name:.name, number:.number}] // []) }'
  echo "== tip: show logs of a failed job =="
  echo "gh run view -R $OWNER/$REPO \$RUN_ID --job <job_id> --log"
else
  echo "== no failed runs found =="
fi
