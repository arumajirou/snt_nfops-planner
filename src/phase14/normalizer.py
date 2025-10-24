# src/phase14/normalizer.py
from __future__ import annotations
import json, re, hashlib, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List

PII_PATTERNS = [
    re.compile(r"(?i)[\\w.+-]+@[\\w-]+\\.[\\w.-]+"),
    re.compile(r"\\b\\d{3}-\\d{4}-\\d{4}\\b"),
]

@dataclass
class NormalizedItem:
    key: Dict[str, Any]     # {run_id,batch_id,model_name,model_version,phase,scenario_id}
    refs: Dict[str, Any]    # {mlflow_run_url,grafana_uid,kibana_saved_search,s3_paths}
    metrics: Dict[str, Any] # {valid_SMAPE,test_CRPS,...,co2_eq_kg}
    text: str               # 本文（要約・説明・抜粋）

def mask_pii(text: str) -> str:
    masked = text
    for pat in PII_PATTERNS:
        masked = pat.sub("[REDACTED]", masked)
    return masked

def normalize(inputs: Dict[str, Any]) -> NormalizedItem:
    # 最小化: Phase13成果物があれば拾い、無ければダミー
    key = {"run_id": inputs.get("run_id","unknown"),
           "batch_id": inputs.get("batch_id","unknown"),
           "model_name": inputs.get("model_name","unknown"),
           "model_version": inputs.get("model_version","unknown"),
           "phase": "14", "scenario_id": inputs.get("scenario_id","default")}
    refs = inputs.get("refs", {})
    m = inputs.get("metrics", {"valid_SMAPE": inputs.get("sMAPE", 0.18)})
    text = inputs.get("text", "Phase14 normalized record.")
    return NormalizedItem(key=key, refs=refs, metrics=m, text=mask_pii(text))

def chunks_for_index(doc: NormalizedItem) -> List[Dict[str, Any]]:
    """段落粒度の簡易分割（行ごと）"""
    rows = []
    for i, line in enumerate(doc.text.splitlines(), start=1):
        if not line.strip(): continue
        emb = hashlib.sha1(line.encode("utf-8")).hexdigest()[:16]  # 疑似埋め込み（将来置換）
        rows.append({"chunk_id": f"{doc.key['batch_id']}-{i}",
                     "text": line, "meta": {**doc.key, **doc.metrics}, "vec": emb})
    return rows

def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
