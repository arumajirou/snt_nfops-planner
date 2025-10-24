"""app.py - FastAPI アプリケーション"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import time
import uuid
from loguru import logger
from pathlib import Path

from nfops_inference.models import (
    PredictionRequest,
    PredictionResponse,
    PredictionOutput,
    HealthResponse,
    VersionInfo
)
from nfops_inference.core.cache import SimpleCache
from nfops_inference.core.predictor import Predictor
from nfops_inference.core.circuit_breaker import CircuitBreaker
from nfops_inference.utils.audit_logger import AuditLogger


# Initialize
app = FastAPI(
    title="NFOps Inference API",
    version="1.0.0",
    description="Production inference API for time series forecasting"
)

# Global state
cache = SimpleCache(max_size=1000)
predictor = Predictor()
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
audit_logger = AuditLogger(Path("logs/inference"))

# Model info
MODEL_INFO = {
    "model_name": "sales_demand_D",
    "version": 27,
    "stage": "Production",
    "api_version": "1.0.0"
}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model_loaded": predictor.model is not None
    }


@app.get("/version", response_model=VersionInfo)
async def version():
    """Version information endpoint"""
    return MODEL_INFO


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    cache_stats = cache.stats()
    cb_state = circuit_breaker.get_state()
    
    metrics_text = f"""
# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate {cache_stats['hit_rate']}

# HELP cache_size Current cache size
# TYPE cache_size gauge
cache_size {cache_stats['size']}

# HELP circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)
# TYPE circuit_breaker_state gauge
circuit_breaker_state {0 if cb_state == 'closed' else 1 if cb_state == 'open' else 2}
"""
    
    return JSONResponse(content=metrics_text, media_type="text/plain")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, req: Request):
    """Prediction endpoint"""
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        f"Prediction request: {request_id} | "
        f"{len(request.items)} items | "
        f"quantiles={request.quantiles}"
    )
    
    try:
        # Check cache for each item
        cached_results = []
        uncached_items = []
        
        for item in request.items:
            cache_key = cache.get_cache_key(
                model_name=request.model_name,
                version=MODEL_INFO["version"],
                scenario_id=request.scenario_id,
                unique_id=item.unique_id,
                ds=item.ds,
                exog=item.exog
            )
            
            cached = cache.get(cache_key)
            if cached:
                cached_results.extend(cached)
            else:
                uncached_items.append(item.dict())
        
        # Predict uncached items
        if uncached_items:
            def predict_func():
                return predictor.predict(
                    items=uncached_items,
                    quantiles=request.quantiles
                )
            
            pred_df = circuit_breaker.call(predict_func)
            
            # Convert to output format
            new_results = []
            for _, row in pred_df.iterrows():
                output = PredictionOutput(
                    unique_id=row['unique_id'],
                    ds=row['ds'],
                    q=row['q'],
                    y_hat=row['y_hat'],
                    pi_low_90=row.get('pi_low_90'),
                    pi_high_90=row.get('pi_high_90')
                )
                new_results.append(output)
            
            # Cache results for each item
            for item in uncached_items:
                item_results = [
                    r for r in new_results
                    if r.unique_id == item['unique_id'] and r.ds == item['ds']
                ]
                
                cache_key = cache.get_cache_key(
                    model_name=request.model_name,
                    version=MODEL_INFO["version"],
                    scenario_id=request.scenario_id,
                    unique_id=item['unique_id'],
                    ds=item['ds'],
                    exog=item.get('exog')
                )
                cache.set(cache_key, item_results)
            
            all_results = cached_results + new_results
        else:
            all_results = cached_results
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Audit log
        audit_logger.log(
            request_id=request_id,
            route="/predict",
            model_name=request.model_name,
            model_version=MODEL_INFO["version"],
            scenario_id=request.scenario_id,
            latency_ms=latency_ms,
            status=200,
            cache_hit=len(uncached_items) == 0,
            n_items=len(request.items)
        )
        
        logger.success(
            f"Prediction completed: {request_id} | "
            f"{latency_ms:.1f}ms | "
            f"cache_hit={len(uncached_items) == 0}"
        )
        
        return {
            "run_id": "prod_run_001",
            "model_version": MODEL_INFO["version"],
            "scenario_id": request.scenario_id,
            "preds": all_results,
            "request_id": request_id,
            "cache_hit": len(uncached_items) == 0
        }
    
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        audit_logger.log(
            request_id=request_id,
            route="/predict",
            model_name=request.model_name,
            model_version=MODEL_INFO["version"],
            scenario_id=request.scenario_id,
            latency_ms=latency_ms,
            status=500,
            cache_hit=False,
            n_items=len(request.items),
            error=str(e)
        )
        
        logger.exception(f"Prediction failed: {request_id}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
