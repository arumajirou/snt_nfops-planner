"""dashboard_generator.py - Grafanaダッシュボード生成"""
import json
from pathlib import Path
from loguru import logger


class DashboardGenerator:
    """Grafana dashboard generator"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_overview(self, filename: str = "00_overview.json"):
        """Generate overview dashboard"""
        logger.info("Generating overview dashboard")
        
        dashboard = {
            "uid": "nf-overview",
            "title": "NF Ops — Overview",
            "tags": ["nfops", "overview"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-24h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "title": "GPU Utilization (avg)",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "avg(nf_gpu_util)",
                        "refId": "A"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"value": 0, "color": "red"},
                                    {"value": 40, "color": "yellow"},
                                    {"value": 60, "color": "green"}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "Inference p95 Latency",
                    "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "histogram_quantile(0.95, sum by (le) (rate(nf_infer_latency_ms_bucket[5m])))",
                        "refId": "A"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "ms",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"value": 0, "color": "green"},
                                    {"value": 200, "color": "yellow"},
                                    {"value": 300, "color": "red"}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "CO2 Emissions (7d)",
                    "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "sum(increase(nf_co2_kg[7d]))",
                        "refId": "A"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "kg",
                            "decimals": 2
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "Total Cost (7d)",
                    "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "sum(increase(nf_cost_usd[7d]))",
                        "refId": "A"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyUSD",
                            "decimals": 2
                        }
                    }
                },
                {
                    "id": 5,
                    "type": "graph",
                    "title": "GPU Utilization Over Time",
                    "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "nf_gpu_util",
                        "legendFormat": "GPU {{gpu_uuid}}",
                        "refId": "A"
                    }],
                    "yaxes": [
                        {"format": "percent", "label": "Utilization"},
                        {"format": "short"}
                    ]
                },
                {
                    "id": 6,
                    "type": "graph",
                    "title": "Request Rate",
                    "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "sum(rate(nf_infer_requests_total[5m]))",
                        "legendFormat": "RPS",
                        "refId": "A"
                    }],
                    "yaxes": [
                        {"format": "reqps", "label": "Requests/s"},
                        {"format": "short"}
                    ]
                }
            ]
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)
        
        logger.success(f"Dashboard saved: {output_path}")
    
    def generate_audit(self, filename: str = "40_audit.json"):
        """Generate audit dashboard"""
        logger.info("Generating audit dashboard")
        
        dashboard = {
            "uid": "nf-audit",
            "title": "NF Ops — Audit",
            "tags": ["nfops", "audit"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 1,
            "time": {
                "from": "now-24h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "title": "Audit Events (24h)",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "sum(increase(nf_audit_events_total[24h]))",
                        "refId": "A"
                    }]
                },
                {
                    "id": 2,
                    "type": "table",
                    "title": "Recent Audit Events",
                    "gridPos": {"x": 0, "y": 4, "w": 24, "h": 8},
                    "targets": [{
                        "expr": "{app=\"api\"} |= \"audit\" | json",
                        "refId": "A"
                    }]
                },
                {
                    "id": 3,
                    "type": "graph",
                    "title": "Events by Type",
                    "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "sum by (event) (rate(nf_audit_events_total[5m]))",
                        "legendFormat": "{{event}}",
                        "refId": "A"
                    }]
                }
            ]
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)
        
        logger.success(f"Dashboard saved: {output_path}")
