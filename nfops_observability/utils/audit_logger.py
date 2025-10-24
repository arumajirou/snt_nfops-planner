"""audit_logger.py - 監査ログ"""
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from nfops_observability.models import AuditEvent


class AuditLogger:
    """Audit logger"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.log"
    
    def log_event(
        self,
        event: str,
        actor_type: str,
        actor_id: str,
        actor_role: str,
        request_id: str,
        status_ok: bool,
        status_code: int,
        latency_ms: float,
        run_id: str = None,
        model_name: str = None,
        model_version: int = None
    ):
        """Log audit event"""
        
        audit_event = AuditEvent(
            ts=datetime.now().isoformat(),
            event=event,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_role=actor_role,
            request_id=request_id,
            run_id=run_id,
            model_name=model_name,
            model_version=model_version,
            status_ok=status_ok,
            status_code=status_code,
            latency_ms=latency_ms
        )
        
        # Write JSONL
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_event.to_dict()) + '\n')
        
        logger.info(
            f"Audit: {event} | {actor_id} ({actor_role}) | "
            f"status={status_code} | {latency_ms:.1f}ms"
        )
