"""test_cost_calculator.py"""
import pytest
from nfops_observability.calculators.cost_calculator import CostCalculator


class TestCostCalculator:
    def test_calculate_cost(self):
        """Test cost calculation"""
        calculator = CostCalculator(
            electricity_price_usd_per_kwh=0.12,
            carbon_intensity_kg_per_kwh=0.5,
            gpu_rate_usd_per_hour=1.5
        )
        
        metrics = calculator.calculate(
            energy_kwh=10.0,
            gpu_hours=5.0
        )
        
        # Check calculations
        assert metrics.energy_kwh == 10.0
        assert metrics.co2_kg == 5.0  # 10 * 0.5
        assert metrics.cost_usd == 8.7  # (10 * 0.12) + (5 * 1.5)
