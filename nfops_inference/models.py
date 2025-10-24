"""Data models for inference"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionItem(BaseModel):
    """Single prediction item"""
    unique_id: str = Field(..., description="Series identifier")
    ds: str = Field(..., description="Datetime in ISO format")
    exog: Optional[Dict[str, float]] = Field(None, description="Exogenous variables")


class PredictionRequest(BaseModel):
    """Prediction request"""
    model_name: str = Field(..., description="Model name")
    version_or_stage: str = Field(default="Production", description="Model version or stage")
    quantiles: List[float] = Field(default=[0.1, 0.5, 0.9], description="Quantiles to predict")
    scenario_id: str = Field(default="base", description="Scenario identifier")
    items: List[PredictionItem] = Field(..., description="Items to predict")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")


class PredictionOutput(BaseModel):
    """Single prediction output"""
    unique_id: str
    ds: str
    q: float
    y_hat: float
    pi_low_90: Optional[float] = None
    pi_high_90: Optional[float] = None


class PredictionResponse(BaseModel):
    """Prediction response"""
    run_id: str
    model_version: int
    scenario_id: str
    preds: List[PredictionOutput]
    request_id: Optional[str] = None
    cache_hit: bool = False


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    model_loaded: bool = True


class VersionInfo(BaseModel):
    """Version information"""
    model_name: str
    version: int
    stage: str
    api_version: str
