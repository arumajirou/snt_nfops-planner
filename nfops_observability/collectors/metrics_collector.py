"""metrics_collector.py - メトリクス収集"""
import time
import psutil
from loguru import logger
from typing import List, Dict
from nfops_observability.models import MetricSample, ResourceMetrics


class MetricsCollector:
    """Metrics collector"""
    
    def __init__(self):
        self.samples: List[MetricSample] = []
    
    def collect_system_metrics(self) -> ResourceMetrics:
        """Collect system metrics"""
        logger.info("Collecting system metrics")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # RAM
        ram = psutil.virtual_memory()
        ram_used_gb = ram.used / (1024**3)
        
        # GPU (simulated)
        gpu_util = 0.0
        vram_used_gb = 0.0
        
        try:
            # Try to get GPU info (requires pynvml or similar)
            # For now, use dummy values
            gpu_util = 45.0
            vram_used_gb = 8.5
        except:
            pass
        
        metrics = ResourceMetrics(
            gpu_util=gpu_util,
            vram_used_gb=vram_used_gb,
            cpu_percent=cpu_percent,
            ram_used_gb=ram_used_gb
        )
        
        logger.info(
            f"System: GPU={gpu_util:.1f}%, VRAM={vram_used_gb:.1f}GB, "
            f"CPU={cpu_percent:.1f}%, RAM={ram_used_gb:.1f}GB"
        )
        
        return metrics
    
    def add_sample(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None
    ):
        """Add metric sample"""
        sample = MetricSample(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {}
        )
        self.samples.append(sample)
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Group by metric name for HELP and TYPE
        metrics_seen = set()
        
        for sample in self.samples:
            if sample.name not in metrics_seen:
                lines.append(f"# HELP {sample.name} {sample.name}")
                lines.append(f"# TYPE {sample.name} gauge")
                metrics_seen.add(sample.name)
            
            lines.append(sample.to_prometheus())
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear samples"""
        self.samples.clear()
