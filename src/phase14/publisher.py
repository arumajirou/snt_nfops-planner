# src/phase14/publisher.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

PAGE = """# Run/Batch ポータル
- batch_id: {batch_id}
- model: {model_name} ({model_version})
- 指標: sMAPE={smape}
- Gatekeeper: {register}
- 成果物: {ref_dir}

## ダイジェスト
{summary}
"""

def publish_portal(payload: Dict[str, Any], out_dir: Path, index_md: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    page = PAGE.format(**payload)
    page_path = out_dir / f"{payload['batch_id']}.md"
    page_path.write_text(page, encoding="utf-8")
    # index追記（先頭に追加）
    line = f"- [{payload['batch_id']}]({page_path.name}) — sMAPE={payload['smape']}\n"
    current = index_md.read_text(encoding="utf-8")
    parts = current.splitlines()
    # 3行目以降に差し込み
    new_md = "\n".join(parts[:3] + [line] + parts[3:])
    index_md.write_text(new_md, encoding="utf-8")
    return page_path
