"""sample_data_phase5.py - サンプルデータ生成"""
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
output_dir = Path('examples/phase5')
output_dir.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_dir / 'sample_train.parquet')
df.to_csv(output_dir / 'sample_train.csv', index=False)

print(f"Generated {len(df)} rows")
print(f"Series: {df['unique_id'].nunique()}")
print(f"Date range: {df['ds'].min()} to {df['ds'].max()}")
print(f"Saved to {output_dir}")
