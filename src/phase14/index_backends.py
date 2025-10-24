from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
from .embeddings import embed_texts
from .normalizer import save_json


def _rows_to_texts(rows: List[Dict[str,Any]]) -> list[str]:
return [r["text"] for r in rows]


class JsonlIndex:
def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
save_json(out_dir/"index.jsonl", rows)
return len(rows)


class FaissIndex:
def build(self, rows: List[Dict[str,Any]], out_dir: Path) -> int:
try:
import numpy as np, faiss, json
X = embed_texts(_rows_to_texts(rows))
xb = np.array(X, dtype="float32")
index = faiss.IndexFlatIP(xb.shape[1]) # normalize 済なら cosine 相当
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
