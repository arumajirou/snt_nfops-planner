"""observability_runner.py - 監視実行CLI"""
import click
import time
from pathlib import Path
from loguru import logger
from nfops_observability.collectors.metrics_collector import MetricsCollector
from nfops_observability.calculators.cost_calculator import CostCalculator
from nfops_observability.generators.dashboard_generator import DashboardGenerator
from nfops_observability.generators.alert_rule_generator import AlertRuleGenerator
from nfops_observability.utils.audit_logger import AuditLogger


@click.command()
@click.option('--collect-metrics', is_flag=True, help='Collect system metrics')
@click.option('--calculate-cost', is_flag=True, help='Calculate cost and CO2')
@click.option('--generate-dashboards', is_flag=True, help='Generate Grafana dashboards')
@click.option('--generate-alerts', is_flag=True, help='Generate alert rules')
@click.option('--log-audit', is_flag=True, help='Generate sample audit log')
@click.option('--energy-kwh', default=10.0, type=float, help='Energy consumed (kWh)')
@click.option('--gpu-hours', default=5.0, type=float, help='GPU hours used')
@click.option('--out-dir', default='grafana/dashboards', help='Output directory for dashboards')
@click.option('--rules-dir', default='prometheus/rules', help='Output directory for alert rules')
def main(
    collect_metrics,
    calculate_cost,
    generate_dashboards,
    generate_alerts,
    log_audit,
    energy_kwh,
    gpu_hours,
    out_dir,
    rules_dir
):
    """Observability Runner - Phase 12"""
    logger.info("Starting observability operations...")
    
    start_time = time.time()
    
    try:
        # 1. Collect Metrics
        if collect_metrics:
            logger.info("=== Collecting Metrics ===")
            collector = MetricsCollector()
            
            # System metrics
            sys_metrics = collector.collect_system_metrics()
            
            # Add to samples
            collector.add_sample("nf_gpu_util", sys_metrics.gpu_util, {"gpu_uuid": "GPU-0"})
            collector.add_sample("nf_vram_used_gb", sys_metrics.vram_used_gb, {"gpu_uuid": "GPU-0"})
            collector.add_sample("nf_cpu_percent", sys_metrics.cpu_percent, {"node": "node-1"})
            collector.add_sample("nf_ram_used_gb", sys_metrics.ram_used_gb, {"node": "node-1"})
            
            # Export to Prometheus format
            prom_text = collector.export_prometheus()
            
            # Save
            metrics_file = Path("monitor/metrics.txt")
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            metrics_file.write_text(prom_text, encoding='utf-8')
            
            logger.success(f"Metrics exported: {metrics_file}")
            logger.info(f"Collected {len(collector.samples)} samples")
        
        # 2. Calculate Cost
        if calculate_cost:
            logger.info("=== Calculating Cost and CO2 ===")
            calculator = CostCalculator(
                electricity_price_usd_per_kwh=0.12,
                carbon_intensity_kg_per_kwh=0.5,
                gpu_rate_usd_per_hour=1.5
            )
            
            cost_metrics = calculator.calculate(
                energy_kwh=energy_kwh,
                gpu_hours=gpu_hours
            )
            
            logger.success(
                f"Results: Energy={cost_metrics.energy_kwh:.2f}kWh, "
                f"CO2={cost_metrics.co2_kg:.2f}kg, Cost="
            )
        
        # 3. Generate Dashboards
        if generate_dashboards:
            logger.info("=== Generating Dashboards ===")
            dashboard_gen = DashboardGenerator(Path(out_dir))
            
            dashboard_gen.generate_overview()
            dashboard_gen.generate_audit()
            
            logger.success("Dashboards generated")
        
        # 4. Generate Alert Rules
        if generate_alerts:
            logger.info("=== Generating Alert Rules ===")
            alert_gen = AlertRuleGenerator(Path(rules_dir))
            
            alert_gen.generate_slo_rules()
            alert_gen.generate_gpu_rules()
            alert_gen.generate_co2_rules()
            
            logger.success("Alert rules generated")
        
        # 5. Audit Logging
        if log_audit:
            logger.info("=== Generating Sample Audit Log ===")
            audit_logger = AuditLogger(Path("logs/audit"))
            
            # Sample events
            audit_logger.log_event(
                event="PROMOTE",
                actor_type="user",
                actor_id="user123",
                actor_role="admin",
                request_id="req-001",
                status_ok=True,
                status_code=200,
                latency_ms=84.5,
                run_id="run-001",
                model_name="sales_demand_D",
                model_version=27
            )
            
            audit_logger.log_event(
                event="PREDICT",
                actor_type="service",
                actor_id="api-service",
                actor_role="service",
                request_id="req-002",
                status_ok=True,
                status_code=200,
                latency_ms=42.3,
                model_name="sales_demand_D",
                model_version=27
            )
            
            logger.success("Audit events logged")
        
        # Summary
        elapsed = time.time() - start_time
        logger.success(f"Observability operations completed in {elapsed:.1f}s")
        
        return 0
    
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
