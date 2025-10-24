"""sample_data_phase8.py - サンプルデータ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

# Use Phase 7 data as base
np.random.seed(42)
dates = pd.date_range('2024-10-01', periods=30, freq='D')
series_ids = ['S001', 'S002', 'S003']

# Generate features
features_data = []
for sid in series_ids:
    base = np.random.randint(60, 90)
    for i, date in enumerate(dates):
        value = base + i * 0.5 + np.random.randn() * 3
ECHO は <ON> です。
        features_data.append({
            'unique_id': sid,
            'ds': date,
            'y_scaled': value / 100,
            'h_lag_1_y': value / 100 - 0.01,
            'h_lag_7_y': value / 100 - 0.05,
            'h_r7_mean_y': value / 100,
            'cal_dow': date.dayofweek,
            'cal_month': date.month,
            'price_pctchg_1': np.random.uniform(-0.05, 0.05),
            'promo_flag': np.random.choice([0, 0, 0, 1]),
            's_cluster_id': np.random.choice([1, 2, 3])
        })

features_df = pd.DataFrame(features_data)

# Generate actuals
actuals_data = []
for sid in series_ids:
    base = np.random.randint(60, 90)
    for date in dates:
        value = base + np.random.randn() * 5
        actuals_data.append({
            'unique_id': sid,
            'ds': date,
            'y': value
        })

actuals_df = pd.DataFrame(actuals_data)

# Generate predictions
preds_data = []
for sid in series_ids:
    for date in dates:
        actual = actuals_df[
            (actuals_df['unique_id'] == sid) & 
            (actuals_df['ds'] == date)
        ]['y'].values[0]
ECHO は <ON> です。
        for q in [0.1, 0.5, 0.9]:
            if q == 0.5:
                y_hat = actual + np.random.randn() * 3
            elif q == 0.1:
                y_hat = actual + np.random.randn() * 3 - 5
            else:
                y_hat = actual + np.random.randn() * 3 + 5
ECHO は <ON> です。
            preds_data.append({
                'unique_id': sid,
                'ds': date,
                'model': 'TestModel',
                'run_id': 'test_run',
                'scenario_id': 'base',
                'q': q,
                'y_hat': y_hat
            })

preds_df = pd.DataFrame(preds_data)

# Save
output_dir = Path('examples/phase8')
output_dir.mkdir(parents=True, exist_ok=True)

features_df.to_parquet(output_dir / 'test_features.parquet')
actuals_df.to_parquet(output_dir / 'test_actuals.parquet')
preds_df.to_parquet(output_dir / 'test_preds.parquet')

print(f"Generated {len^(features_df^)} feature records")
print(f"Generated {len^(actuals_df^)} actuals")
print(f"Generated {len^(preds_df^)} predictions")
print(f"Saved to {output_dir}")
