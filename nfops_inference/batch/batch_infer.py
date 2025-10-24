"""batch_infer.py - バッチ推論"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_inference.core.predictor import Predictor
from nfops_inference.utils.audit_logger import AuditLogger
import time
import uuid


@click.command()
@click.option('--input', required=True, type=click.Path(exists=True), help='Input parquet file')
@click.option('--output', required=True, type=click.Path(), help='Output parquet file')
@click.option('--model-name', default='sales_demand_D', help='Model name')
@click.option('--version', default=27, type=int, help='Model version')
@click.option('--scenario', default='base', help='Scenario ID')
@click.option('--quantiles', default='0.1,0.5,0.9', help='Quantiles (comma-separated)')
@click.option('--micro-batch', default=1024, type=int, help='Micro batch size')
def main(input, output, model_name, version, scenario, quantiles, micro_batch):
    """Batch Inference CLI - Phase 10"""
    
    logger.info("Starting batch inference...")
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Parse quantiles
        q_list = [float(q.strip()) for q in quantiles.split(',')]
        logger.info(f"Quantiles: {q_list}")
        
        # Load input
        logger.info(f"Loading input from {input}")
        df = pd.read_parquet(input)
        logger.info(f"Loaded {len(df)} rows")
        
        # Initialize predictor
        predictor = Predictor()
        
        # Process in micro batches
        all_results = []
        n_batches = (len(df) + micro_batch - 1) // micro_batch
        
        for i in range(n_batches):
            start_idx = i * micro_batch
            end_idx = min((i + 1) * micro_batch, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            logger.info(f"Processing batch {i+1}/{n_batches} ({len(batch_df)} items)")
            
            # Convert to items
            items = []
            for _, row in batch_df.iterrows():
                item = {
                    'unique_id': row['unique_id'],
                    'ds': str(row['ds'])
                }
                items.append(item)
            
            # Predict
            pred_df = predictor.predict(items, quantiles=q_list)
            
            # Add metadata
            pred_df['model_name'] = model_name
            pred_df['model_version'] = version
            pred_df['scenario_id'] = scenario
            pred_df['request_id'] = request_id
            
            all_results.append(pred_df)
        
        # Combine results
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Save output
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_parquet(output_path)
        
        logger.success(f"Saved {len(final_df)} predictions to {output_path}")
        
        # Audit log
        audit_logger = AuditLogger(Path("logs/inference"))
        latency_ms = (time.time() - start_time) * 1000
        
        audit_logger.log(
            request_id=request_id,
            route="batch_infer",
            model_name=model_name,
            model_version=version,
            scenario_id=scenario,
            latency_ms=latency_ms,
            status=0,
            cache_hit=False,
            n_items=len(df)
        )
        
        elapsed = time.time() - start_time
        logger.success(f"Batch inference completed in {elapsed:.1f}s")
        logger.info(f"Throughput: {len(df)/elapsed:.1f} items/s")
        
        return 0
    
    except Exception as e:
        logger.exception(f"Batch inference failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
