# scripts/phase14_knn_search.py
from __future__ import annotations
import os, json
from pathlib import Path
from src.phase14.embeddings import embed_texts


def search_opensearch(q: str, k: int = 5):
from opensearchpy import OpenSearch
url = os.getenv("OPENSEARCH_URL"); idx = os.getenv("OPENSEARCH_INDEX", "phase14")
client = OpenSearch(hosts=[url], http_auth=(os.getenv("OPENSEARCH_USER", ""), os.getenv("OPENSEARCH_PASS", "")))
vec = embed_texts([q])[0]
body = {"size": k, "query": {"knn": {"vec": {"vector": vec, "k": k}}}, "_source": ["text", "meta"]}
res = client.search(index=idx, body=body)
return [{"_score": h.get("_score"), "text": h["_source"].get("text")} for h in res["hits"]["hits"]]


def search_faiss(q: str, k: int = 5, base: Path | None = None):
import numpy as np, faiss, json
base = base or sorted(Path("outputs/phase14").glob("*"))[-1]
vec = embed_texts([q])[0]
qb = np.array([vec], dtype="float32")
index = faiss.read_index(str(base / "faiss.index"))
D, I = index.search(qb, k)
metas = json.loads((base / "faiss.meta.json").read_text("utf-8"))
return [{"dist": float(D[0][i]), "text": metas[I[0][i]]["text"]} for i in range(len(I[0]))]


def search_pgvector(q: str, k: int = 5):
import psycopg2
dsn = os.getenv("PG_DSN"); table = os.getenv("PG_TABLE", "phase14_index")
vec = embed_texts([q])[0]
conn = psycopg2.connect(dsn); cur = conn.cursor()
cur.execute(f"SELECT text FROM {table} ORDER BY vec <=> %s LIMIT %s;", (vec, k))
rows = cur.fetchall(); cur.close(); conn.close()
return [{"text": r[0]} for r in rows]


if __name__ == "__main__":
