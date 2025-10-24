"""cost_calculator.py - コスト計算"""
from loguru import logger
from typing import Dict
from nfops_observability.models import CostMetrics


class CostCalculator:
    """Cost and CO2 calculator"""
    
    def __init__(
        self,
        electricity_price_usd_per_kwh: float = 0.12,
        carbon_intensity_kg_per_kwh: float = 0.5,
        gpu_rate_usd_per_hour: float = 1.5
    ):
        """
        Args:
            electricity_price_usd_per_kwh: Electricity price
            carbon_intensity_kg_per_kwh: Carbon intensity (regional)
            gpu_rate_usd_per_hour: GPU cost per hour
        """
        self.electricity_price = electricity_price_usd_per_kwh
        self.carbon_intensity = carbon_intensity_kg_per_kwh
        self.gpu_rate = gpu_rate_usd_per_hour
    
    def calculate(
        self,
        energy_kwh: float = 0.0,
        gpu_hours: float = 0.0
    ) -> CostMetrics:
        """Calculate cost and CO2"""
        logger.info(f"Calculating cost: energy={energy_kwh:.3f}kWh, gpu_hours={gpu_hours:.2f}h")
        
        # CO2 emissions
        co2_kg = energy_kwh * self.carbon_intensity
        
        # Cost
        electricity_cost = energy_kwh * self.electricity_price
        gpu_cost = gpu_hours * self.gpu_rate
        total_cost = electricity_cost + gpu_cost
        
        metrics = CostMetrics(
            energy_kwh=energy_kwh,
            co2_kg=co2_kg,
            cost_usd=total_cost
        )
        
        logger.info(
            f"Cost:  (electricity=, "
            f"gpu=), CO2={co2_kg:.3f}kg"
        )
        
        return metrics
