"""sample_data_phase6.py - サンプルデータ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

# サンプルデータ生成
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=300, freq='D')
series_ids = ['S001', 'S002', 'S003']

data = []
for sid in series_ids:
    base = np.random.randint(50, 100)
    trend = np.linspace(0, 30, len(dates))
    seasonal = 15 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
    noise = np.random.randn(len(dates)) * 8
ECHO is on.
    for i, date in enumerate(dates):
        value = base + trend[i] + seasonal[i] + noise[i]
        data.append({
            'unique_id': sid,
            'ds': date,
            'y': value,
            'y_scaled': (value - 60) / 30
        })

df = pd.DataFrame(data)

# 保存
output_dir = Path('examples/phase6')
output_dir.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_dir / 'sample_train.parquet')

# Create future scenario
future_dates = pd.date_range('2024-10-27', periods=30, freq='D')
future_data = []
for sid in series_ids:
    for date in future_dates:
        future_data.append({
            'unique_id': sid,
            'ds': date
        })

futr_df = pd.DataFrame(future_data)
scenarios_dir = output_dir / 'scenarios'
scenarios_dir.mkdir(exist_ok=True)
futr_df.to_csv(scenarios_dir / 'base.csv', index=False)

print(f"Generated {len^(df^)} rows")
print(f"Generated {len^(futr_df^)} future records")
print(f"Saved to {output_dir}")
