#!/usr/bin/env bash
set -euo pipefail

PR="${1:?usage: tools/pr-admin-merge.sh <PR_NUMBER>}"
BASE="${BASE:-main}"
REMOTE="${REMOTE:-origin}"

# repo 推定
url=$(git remote get-url "$REMOTE")
[[ "$url" =~ github.com[:/](.+)/(.+)\.git ]] || { echo "not GitHub: $url" >&2; exit 2; }
OWNER="${OWNER:-${BASH_REMATCH[1]}}"; REPO="${REPO:-${BASH_REMATCH[2]}}"

# 既存保護を最小JSONでバックアップ
BACKUP=tools/branch-protection.${BASE}.backup.json
gh api -H "Accept: application/vnd.github+json" "/repos/$OWNER/$REPO/branches/$BASE/protection" \
| jq '{
  required_status_checks: { strict: .required_status_checks.strict, contexts: (.required_status_checks.contexts // []) },
  enforce_admins: (.enforce_admins.enabled // false),
  required_pull_request_reviews: (if .required_pull_request_reviews
     then { required_approving_review_count: .required_pull_request_reviews.required_approving_review_count,
            dismiss_stale_reviews: .required_pull_request_reviews.dismiss_stale_reviews,
            require_code_owner_reviews: .required_pull_request_reviews.require_code_owner_reviews }
     else null end),
  restrictions: null,
  required_conversation_resolution: (.required_conversation_resolution.enabled // false),
  allow_force_pushes: (.allow_force_pushes.enabled // false),
  allow_deletions: (.allow_deletions.enabled // false)
}' > "$BACKUP"

echo "== backup saved: $BACKUP"; cat "$BACKUP" | jq . >/dev/null

# 一時緩和（レビュー必須/未解決コメント必須/ステータスチェックをOFF）
RELAX=$(cat <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": [] },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_conversation_resolution": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
)
echo "$RELAX" | gh api --method PUT -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/branches/$BASE/protection" --input -

# マージ（管理者権限）
gh pr merge -R "$OWNER/$REPO" "$PR" --squash --delete-branch --admin

# 保護を復元
gh api --method PUT -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/branches/$BASE/protection" --input "$BACKUP"

# 反映検証
git fetch "$REMOTE" "$BASE" >/dev/null
git switch "$BASE" && git pull --ff-only
git --no-pager log --oneline -n 5
