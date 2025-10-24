"""test_metrics_collector.py"""
import pytest
from nfops_observability.collectors.metrics_collector import MetricsCollector


class TestMetricsCollector:
    def test_collect_system_metrics(self):
        """Test system metrics collection"""
        collector = MetricsCollector()
        
        metrics = collector.collect_system_metrics()
        
        # Check metrics exist
        assert metrics.cpu_percent >= 0
        assert metrics.ram_used_gb >= 0
    
    def test_add_sample(self):
        """Test adding metric sample"""
        collector = MetricsCollector()
        
        collector.add_sample("test_metric", 42.0, {"label": "value"})
        
        assert len(collector.samples) == 1
        assert collector.samples[0].name == "test_metric"
        assert collector.samples[0].value == 42.0
    
    def test_export_prometheus(self):
        """Test Prometheus export"""
        collector = MetricsCollector()
        
        collector.add_sample("test_metric", 42.0, {"label": "value"})
        
        prom_text = collector.export_prometheus()
        
        assert "test_metric" in prom_text
        assert "42.0" in prom_text
