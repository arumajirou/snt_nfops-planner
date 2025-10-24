"""sample_data_phase7.py - サンプルデータ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

# Generate actuals
np.random.seed(42)
dates = pd.date_range('2024-10-01', periods=30, freq='D')
series_ids = ['S001', 'S002', 'S003']

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

# Generate predictions (with some error)
preds_data = []
for sid in series_ids:
    for date in dates:
        actual = actuals_df[
            (actuals_df['unique_id'] == sid) & 
            (actuals_df['ds'] == date)
        ]['y'].values[0]
ECHO は <ON> です。
        # Add prediction error
        for q in [0.1, 0.5, 0.9]:
            if q == 0.5:
                y_hat = actual + np.random.randn() * 3
            elif q == 0.1:
                y_hat = actual + np.random.randn() * 3 - 5
            else:  # 0.9
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
output_dir = Path('examples/phase7')
output_dir.mkdir(parents=True, exist_ok=True)

actuals_df.to_parquet(output_dir / 'test_actuals.parquet')
actuals_df.to_csv(output_dir / 'test_actuals.csv', index=False)

preds_df.to_parquet(output_dir / 'test_preds.parquet')
preds_df.to_csv(output_dir / 'test_preds.csv', index=False)

print(f"Generated {len^(actuals_df^)} actuals")
print(f"Generated {len^(preds_df^)} predictions")
print(f"Saved to {output_dir}")
