# src/phase14/connectors/prometheus_connector.py
from __future__ import annotations
import os, requests, time
def query_range(q: str="up") -> dict:
    url = os.getenv("PROM_URL")
    if not url: return {}
    try:
        e = int(time.time()); s = e-300
        r = requests.get(f"{url.rstrip('/')}/api/v1/query_range", params={"query": q, "start": s, "end": e, "step": 30}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}
