# src/phase14/index_backends.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
from .embeddings import embed_texts
from .normalizer import save_json

def _rows_to_texts(rows: List[Dict[str,Any]]) -> list[str]:
    return [r["text"] for r in rows]

class JsonlIndex:
    def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
        save_json(out_dir/"index.jsonl", rows)  # BM25は将来
        return len(rows)

class FaissIndex:
    def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
        try:
            import numpy as np, faiss, json
            X = embed_texts(_rows_to_texts(rows))
            xb = np.array(X, dtype="float32")
            index = faiss.IndexFlatIP(xb.shape[1])  # 内積（normalize済みならcos類似）
            index.add(xb)
            faiss.write_index(index, str(out_dir/"faiss.index"))
            (out_dir/"faiss.meta.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), "utf-8")
            return len(rows)
        except Exception:
            return JsonlIndex().build(rows, out_dir)

class OpenSearchIndex:
    def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
        import os, json
        url = os.getenv("OPENSEARCH_URL"); index = os.getenv("OPENSEARCH_INDEX","phase14")
        if not url:
            return JsonlIndex().build(rows, out_dir)
        try:
            from opensearchpy import OpenSearch
            client = OpenSearch(hosts=[url], http_auth=(os.getenv("OPENSEARCH_USER",""), os.getenv("OPENSEARCH_PASS","")))
            # 最小マッピング（dense_vector）— 依存環境により不可なら create失敗→フォールバック
            mapping = {"mappings":{"properties":{"text":{"type":"text"},"vec":{"type":"dense_vector","dims":64}}}}
            try: client.indices.create(index=index, body=mapping, ignore=400)
            except: pass
            X = embed_texts(_rows_to_texts(rows))
            docs = [{"text": r["text"], "meta": r.get("meta",{}), "vec": X[i]} for i,r in enumerate(rows)]
            for i,d in enumerate(docs):
                client.index(index=index, id=i, body=d, refresh=False)
            client.indices.refresh(index=index)
            (out_dir/"opensearch.meta.json").write_text(json.dumps({"indexed":len(rows),"index":index}, indent=2, ensure_ascii=False),"utf-8")
            return len(rows)
        except Exception:
            return JsonlIndex().build(rows, out_dir)

class PgVectorIndex:
    def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
        import os, json
        dsn = os.getenv("PG_DSN"); table = os.getenv("PG_TABLE","phase14_index")
        if not dsn:
            return JsonlIndex().build(rows, out_dir)
        try:
            import psycopg2, psycopg2.extras
            conn = psycopg2.connect(dsn); cur = conn.cursor()
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} (id SERIAL PRIMARY KEY, text TEXT, vec vector(64));")
            X = embed_texts(_rows_to_texts(rows))
            for i,r in enumerate(rows):
                cur.execute(f"INSERT INTO {table}(text,vec) VALUES (%s, %s)", (r['text'], X[i]))
            conn.commit(); cur.close(); conn.close()
            (out_dir/"pgvector.meta.json").write_text(json.dumps({"indexed":len(rows),"table":table}, indent=2, ensure_ascii=False),"utf-8")
            return len(rows)
        except Exception:
            return JsonlIndex().build(rows, out_dir)

def build_with_backend(rows: List[Dict[str,Any]], out_dir: Path) -> int:
    import os
    backend = os.getenv("PHASE14_INDEX_BACKEND","jsonl").lower()
    if backend=="faiss": return FaissIndex().build(rows, out_dir)
    if backend=="opensearch": return OpenSearchIndex().build(rows, out_dir)
    if backend=="pgvector": return PgVectorIndex().build(rows, out_dir)
    return JsonlIndex().build(rows, out_dir)
