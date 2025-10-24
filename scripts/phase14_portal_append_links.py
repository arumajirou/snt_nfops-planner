# scripts/phase14_portal_append_links.py
from __future__ import annotations
import os, json
from pathlib import Path


root = Path('.')
# 最新の Phase14 出力
bdir = root / "outputs" / "phase14"
if not bdir.exists():
raise SystemExit("no phase14 outputs")
latest = sorted(bdir.glob("*"), key=lambda p: p.stat().st_mtime)[-1]
clog = latest / "connectors.log"
if not clog.exists():
raise SystemExit("no connectors.log")


data = json.loads(clog.read_text(encoding='utf-8'))
base_g = (os.getenv("GRAFANA_URL") or "").rstrip("/")
base_k = (os.getenv("KIBANA_URL") or "").rstrip("/")


lines: list[str] = []
# Grafana
for it in (data.get("grafana", {}) or {}).get("search", [])[:5]:
title = it.get("title") or it.get("name") or "grafana"
if it.get("url"):
link = base_g + it["url"]
elif it.get("uid"):
link = f"{base_g}/d/{it['uid']}"
else:
continue
lines.append(f"- [Grafana] {title} — {link}")
# Kibana
for it in (data.get("kibana", {}) or {}).get("searches", {}).get("saved_objects", [])[:5]:
sid = it.get("id"); title = (it.get("attributes") or {}).get("title", "kibana")
if sid and base_k:
link = f"{base_k}/app/discover#/view/{sid}"
