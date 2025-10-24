# src/phase14/connectors/kibana_connector.py
from __future__ import annotations
import os, requests, json
def fetch_saved_search() -> dict:
    url = os.getenv("KIBANA_URL"); token = os.getenv("KIBANA_TOKEN")
    if not url or not token: return {}
    headers={"kbn-xsrf":"true","Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{url.rstrip('/')}/api/saved_objects/_find?type=search&per_page=10", headers=headers, timeout=10)
        r.raise_for_status()
        return {"searches": r.json()}
    except Exception as e:
        return {"error": str(e)}
