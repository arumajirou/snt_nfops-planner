"""sample_data_phase3.py - サンプルデータ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

# サンプルデータ生成
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=200, freq='D')
series_ids = ['S001', 'S002', 'S003']

data = []
for sid in series_ids:
    base = np.random.randint(50, 100)
    trend = np.linspace(0, 20, len(dates))
    noise = np.random.randn(len(dates)) * 5
    for i, date in enumerate(dates):
        data.append({
            'unique_id': sid,
            'ds': date,
            'y': base + trend[i] + noise[i],
            'price': np.random.uniform(5.0, 20.0)
        })

df = pd.DataFrame(data)

# 保存
output_dir = Path('examples/phase3')
output_dir.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_dir / 'sample_train.parquet')
df.to_csv(output_dir / 'sample_train.csv', index=False)

print(f"Generated {len(df)} rows")
print(f"Series: {df['unique_id'].nunique()}")
print(f"Date range: {df['ds'].min()} to {df['ds'].max()}")
print(f"Saved to {output_dir}")
