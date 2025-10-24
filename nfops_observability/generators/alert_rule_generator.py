"""alert_rule_generator.py - アラートルール生成""" 
import yaml
from pathlib import Path
from loguru import logger

class AlertRuleGenerator:
    """Prometheus alert rule generator"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_slo_rules(self, filename: str = "slo.yaml"):
        """Generate SLO alert rules"""
        logger.info("Generating SLO alert rules")

        rules = {
            "groups": [
                {
                    "name": "slo.rules",
                    "rules": [
                        {
                            "alert": "InferenceLatencyHigh",
                            "expr": "histogram_quantile(0.95, sum by (le) (rate(nf_infer_latency_ms_bucket[5m]))) > 250",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Inference p95 latency above SLO",
                                "description": "p95 latency is {{ $value }}ms (threshold: 250ms)"
                            }
                        },
                        {
                            "alert": "InferenceErrorRateHigh",
                            "expr": "sum(rate(nf_infer_errors_total[5m])) / sum(rate(nf_infer_requests_total[5m])) > 0.005",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Inference error rate above SLO",
                                "description": "Error rate is {{ $value | humanizePercentage }} (threshold: 0.5%)"
                            }
                        }
                    ]
                }
            ]
        }

        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(rules, f, default_flow_style=False, sort_keys=False)

        logger.success(f"Alert rules saved: {output_path}")

    def generate_gpu_rules(self, filename: str = "gpu.yaml"):
        """Generate GPU alert rules"""
        logger.info("Generating GPU alert rules")

        rules = {
            "groups": [
                {
                    "name": "gpu.rules",
                    "rules": [
                        {
                            "alert": "ZombieGPUProcess",
                            "expr": "(nf_gpu_util > 0 or nf_vram_used_gb > 1) and on(gpu_uuid) absent(kube_pod_info)",
                            "for": "5m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Zombie GPU process detected",
                                "description": "GPU {{ $labels.gpu_uuid }} is busy but has no owning Pod"
                            }
                        },
                        {
                            "alert": "GPUUtilizationLow",
                            "expr": "avg(nf_gpu_util) < 20",
                            "for": "30m",
                            "labels": {"severity": "info"},
                            "annotations": {
                                "summary": "GPU utilization is low",
                                "description": "Average GPU utilization is {{ $value }}% (consider scaling down)"
                            }
                        }
                    ]
                }
            ]
        }

        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(rules, f, default_flow_style=False, sort_keys=False)

        logger.success(f"Alert rules saved: {output_path}")

    def generate_co2_rules(self, filename: str = "co2.yaml"):
        """Generate CO2/cost alert rules"""
        logger.info("Generating CO2/cost alert rules")

        rules = {
            "groups": [
                {
                    "name": "co2.rules",
                    "rules": [
                        {
                            "alert": "CO2BudgetExceeded",
                            "expr": "sum(increase(nf_co2_kg[7d])) > 100",
                            "for": "1h",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Weekly CO2 budget exceeded",
                                "description": "7-day CO2 emissions: {{ $value }}kg (budget: 100kg)"
                            }
                        },
                        {
                            "alert": "CostBudgetExceeded",
                            "expr": "sum(increase(nf_cost_usd[7d])) > 1000",
                            "for": "1h",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Weekly cost budget exceeded",
                                "description": "7-day cost: ${{ $value }} (budget: $1000)"
                            }
                        }
                    ]
                }
            ]
        }

        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(rules, f, default_flow_style=False, sort_keys=False)

        logger.success(f"Alert rules saved: {output_path}")
