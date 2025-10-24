# src/phase14/connectors/grafana_connector.py
from __future__ import annotations
import os, requests

def fetch_panels() -> dict:
    url = os.getenv("GRAFANA_URL"); token = os.getenv("GRAFANA_TOKEN")
    if not url or not token: return {}
    headers={"Authorization": f"Bearer {token}"}
    # 例: /api/search?query=retrain でダッシュ一覧を得る
    try:
        r = requests.get(f"{url.rstrip('/')}/api/search?query=retrain", headers=headers, timeout=10)
        r.raise_for_status()
        return {"search": r.json()[:10]}
    except Exception as e:
        return {"error": str(e)}
