"""Data models for observability"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetricSample:
    """Metric sample"""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str]
    
    def to_prometheus(self) -> str:
        """Convert to Prometheus text format"""
        labels_str = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
        if labels_str:
            return f"{self.name}{{{labels_str}}} {self.value} {int(self.timestamp * 1000)}"
        else:
            return f"{self.name} {self.value} {int(self.timestamp * 1000)}"


@dataclass
class ResourceMetrics:
    """Resource metrics"""
    gpu_util: float
    vram_used_gb: float
    cpu_percent: float
    ram_used_gb: float
    
    def to_dict(self) -> Dict:
        return {
            "gpu_util": self.gpu_util,
            "vram_used_gb": self.vram_used_gb,
            "cpu_percent": self.cpu_percent,
            "ram_used_gb": self.ram_used_gb
        }


@dataclass
class CostMetrics:
    """Cost and CO2 metrics"""
    energy_kwh: float
    co2_kg: float
    cost_usd: float
    
    def to_dict(self) -> Dict:
        return {
            "energy_kwh": self.energy_kwh,
            "co2_kg": self.co2_kg,
            "cost_usd": self.cost_usd
        }


@dataclass
class AuditEvent:
    """Audit event"""
    ts: str
    event: str
    actor_type: str
    actor_id: str
    actor_role: str
    request_id: str
    run_id: Optional[str]
    model_name: Optional[str]
    model_version: Optional[int]
    status_ok: bool
    status_code: int
    latency_ms: float
    
    def to_dict(self) -> Dict:
        return {
            "ts": self.ts,
            "event": self.event,
            "actor": {
                "type": self.actor_type,
                "id": self.actor_id,
                "role": self.actor_role
            },
            "request_id": self.request_id,
            "run_id": self.run_id,
            "model": {
                "name": self.model_name,
                "version": self.model_version
            } if self.model_name else None,
            "status": {
                "ok": self.status_ok,
                "code": self.status_code
            },
            "latency_ms": self.latency_ms
        }
