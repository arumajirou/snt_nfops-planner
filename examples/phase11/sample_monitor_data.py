"""sample_monitor_data.py - サンプル監視データ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# Generate reference data (normal)
n_ref = 1000
dates_ref = pd.date_range('2025-07-01', periods=n_ref, freq='H')

reference = pd.DataFrame({
    'unique_id': np.random.choice(['S001', 'S002', 'S003'], n_ref),
    'ds': dates_ref,
    'y': np.random.normal(100, 10, n_ref),
    'y_hat': np.random.normal(100, 10, n_ref),
    'y_hat_q0.1': np.random.normal(85, 10, n_ref),
    'y_hat_q0.9': np.random.normal(115, 10, n_ref),
    'feature_1': np.random.normal(50, 5, n_ref),
    'feature_2': np.random.normal(30, 3, n_ref),
    'feature_3': np.random.choice([0, 1], n_ref, p=[0.7, 0.3])
})

# Generate current data (with drift)
n_cur = 200
dates_cur = pd.date_range('2025-10-15', periods=n_cur, freq='H')

current = pd.DataFrame({
    'unique_id': np.random.choice(['S001', 'S002', 'S003'], n_cur),
    'ds': dates_cur,
    'y': np.random.normal(100, 10, n_cur),
    'y_hat': np.random.normal(105, 12, n_cur),  # Worse predictions
    'y_hat_q0.1': np.random.normal(90, 12, n_cur),
    'y_hat_q0.9': np.random.normal(120, 12, n_cur),
    'feature_1': np.random.normal(55, 6, n_cur),  # Drift in mean
    'feature_2': np.random.normal(30, 5, n_cur),  # Drift in variance
    'feature_3': np.random.choice([0, 1], n_cur, p=[0.5, 0.5])  # Drift in distribution
})

# Save
output_dir = Path('examples/phase11')
output_dir.mkdir(parents=True, exist_ok=True)

reference.to_parquet(output_dir / 'reference.parquet')
current.to_parquet(output_dir / 'current.parquet')

print(f"Generated {len(reference)} reference rows")
print(f"Generated {len(current)} current rows")
print(f"Saved to {output_dir}")
