"""audit_logger.py - 監査ログ"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from loguru import logger


class AuditLogger:
    """Audit logger for inference"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "inference.log"
    
    def log(
        self,
        request_id: str,
        route: str,
        model_name: str,
        model_version: int,
        scenario_id: str,
        latency_ms: float,
        status: int,
        cache_hit: bool,
        n_items: int,
        error: str = None
    ):
        """Log inference event"""
        
        entry = {
            "ts": datetime.now().isoformat(),
            "request_id": request_id,
            "route": route,
            "model": model_name,
            "version": model_version,
            "scenario": scenario_id,
            "latency_ms": latency_ms,
            "status": status,
            "cache_hit": cache_hit,
            "n_items": n_items,
            "err": error
        }
        
        # Write JSONL
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        logger.info(
            f"Audit: {request_id} | {model_name}:v{model_version} | "
            f"{latency_ms:.1f}ms | status={status}"
        )
