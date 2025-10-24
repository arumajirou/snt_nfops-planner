"""preproc_runner.py - CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_preprocess.core import SplitManager, MetadataWriter
from nfops_preprocess.transforms.y_transform import YTransformApplier
from nfops_preprocess.scalers.scaler_factory import ScalerFactory
from nfops_preprocess.utils.logging_config import setup_logging


@click.command()
@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--y-type', default='raw', type=click.Choice(['raw', 'diff', 'rolling_sum', 'cumsum']))
@click.option('--window', type=int, default=None)
@click.option('--scaler', default='standard', type=click.Choice(['standard', 'robust', 'minmax', 'log1p']))
@click.option('--scope', default='per_series', type=click.Choice(['global', 'per_series']))
@click.option('--h', default=24, type=int, help='Forecast horizon')
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='transform/')
def main(input, y_type, window, scaler, scope, h, emit_mlflow, out_dir):
    """Preprocessing Runner - Phase 3"""
    setup_logging()
    logger.info("Starting preprocessing...")
ECHO is on.
    try:
        # 1. データ読込
        logger.info(f"Loading data from {input}")
        if input.endswith('.parquet'):
            df = pd.read_parquet(input)
        else:
            df = pd.read_csv(input, parse_dates=['ds'])
        logger.info(f"Loaded {len^(df^)} rows")
ECHO is on.
        # 2. Split決定
        split_mgr = SplitManager(h=h)
        split = split_mgr.resolve_split(df)
ECHO is on.
        # 3. Y変換
        applier = YTransformApplier(y_type=y_type, window=window)
        df, y_meta = applier.apply(df, split)
ECHO is on.
        # 4. スケーリング
        scaler_obj = ScalerFactory.create(scaler, scope)
        scaler_obj.fit(df, split)
        df = scaler_obj.transform(df)
ECHO is on.
        # 5. メタデータ保存
        writer = MetadataWriter(Path(out_dir))
        writer.save_y_transform(y_meta)
        writer.save_scaler(scaler_obj)
ECHO is on.
        # 6. 処理済みデータ保存
        output_path = Path(out_dir) / "preprocessed_data.parquet"
        df.to_parquet(output_path)
        logger.success(f"Saved: {output_path}")
ECHO is on.
        # 7. サマリ
        logger.success(f"Preprocessing completed: y_type={y_type}, scaler={scaler}")
        return 0
ECHO is on.
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
