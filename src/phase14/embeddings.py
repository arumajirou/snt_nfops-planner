# src/phase14/embeddings.py
from __future__ import annotations
import os, hashlib
from typing import List
_EMBED = None
_ERR  = None

def _init():
    global _EMBED, _ERR
    if _EMBED is not None or _ERR is not None: return
    model = os.getenv("PHASE14_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    try:
        from sentence_transformers import SentenceTransformer
        _EMBED = SentenceTransformer(model, device=os.getenv("PHASE14_EMBED_DEVICE","cpu"))
    except Exception as e:
        _ERR = e

def embed_texts(texts: List[str]) -> List[List[float]]:
    _init()
    if _EMBED is not None:
        try:
            vecs = _EMBED.encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist()
            return vecs
        except Exception as e:
            pass
    # フォールバック（安定挙動）：固定長64のハッシュベクトル
    out = []
    for t in texts:
        b = hashlib.sha256(t.encode("utf-8")).digest()
        # 32byte -> 64dimに展開（符号付き）
        v = [((b[i//2] if i%2==0 else b[i//2]^0xAA) - 128)/128.0 for i in range(64)]
        out.append(v)
    return out
