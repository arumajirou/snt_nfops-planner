"""sample_batch_input.py - サンプルバッチデータ生成"""
import pandas as pd
import numpy as np
from pathlib import Path

# Generate sample batch input
np.random.seed(42)
dates = pd.date_range('2025-10-01', periods=100, freq='D')
series_ids = ['S001', 'S002', 'S003']

data = []
for sid in series_ids:
    for date in dates:
        data.append({
            'unique_id': sid,
            'ds': date
        })

df = pd.DataFrame(data)

# Save
output_dir = Path('examples/phase10')
output_dir.mkdir(parents=True, exist_ok=True)

df.to_parquet(output_dir / 'batch_input.parquet')
print(f"Generated {len(df)} rows")
print(f"Saved to {output_dir / 'batch_input.parquet'}")
