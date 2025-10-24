# src/phase14/indexer.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
from .normalizer import NormalizedItem, chunks_for_index, save_json

def build_index(doc: NormalizedItem, out_dir: Path) -> int:
    rows = chunks_for_index(doc)
    save_json(out_dir / "index.jsonl", rows)
    return len(rows)
