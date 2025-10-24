"""feat_runner.py - CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_features.core.config_loader import ConfigLoader
from nfops_features.builders.lag_builder import LagBuilder
from nfops_features.builders.rolling_builder import RollingBuilder
from nfops_features.builders.calendar_builder import CalendarBuilder
from nfops_features.builders.price_promo_builder import PricePromoBuilder
from nfops_features.builders.cluster_builder import ClusterBuilder
from nfops_features.encoders.cat_encoder import CategoryEncoder
from nfops_features.core.auditor import FeatureAuditor
from nfops_features.core.catalog_writer import CatalogWriter
from nfops_features.models import FeatureCatalog
from nfops_features.utils.logging_config import setup_logging
import time


@click.command()
@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--clusters', default=8, type=int)
@click.option('--output-format', default='long', type=click.Choice(['long', 'wide']))
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='features/')
def main(input, config, clusters, output_format, emit_mlflow, out_dir):
    """Feature Engineering Runner - Phase 4"""
    setup_logging()
    logger.info("Starting feature engineering...")
ECHO is on.
    start_time = time.time()
ECHO is on.
    try:
        # 1. 設定読込
        config_loader = ConfigLoader()
        spec = config_loader.load(Path(config))
ECHO is on.
        # 2. データ読込
        logger.info(f"Loading data from {input}")
        if input.endswith('.parquet'):
            df = pd.read_parquet(input)
        else:
            df = pd.read_csv(input, parse_dates=['ds'])
        logger.info(f"Loaded {len^(df^)} rows")
ECHO is on.
        # 3. ラグ特徴
        lag_builder = LagBuilder(
            lags=spec.hist.get('lag', []),
            seasonal_lags=spec.hist.get('seasonal_lag', [])
        )
        df = lag_builder.build(df)
ECHO is on.
        # 4. 移動統計
        rolling_builder = RollingBuilder(spe(
"""feat_runner.py - CLI"""
import click
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_features.core.config_loader import ConfigLoader
from nfops_features.builders.lag_builder import LagBuilder
from nfops_features.builders.rolling_builder import RollingBuilder
from nfops_features.builders.calendar_builder import CalendarBuilder
from nfops_features.builders.price_promo_builder import PricePromoBuilder
from nfops_features.builders.cluster_builder import ClusterBuilder
from nfops_features.encoders.cat_encoder import CategoryEncoder
from nfops_features.core.auditor import FeatureAuditor
from nfops_features.core.catalog_writer import CatalogWriter
from nfops_features.models import FeatureCatalog
from nfops_features.utils.logging_config import setup_logging
import time


@click.command()
@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--clusters', default=8, type=int)
@click.option('--output-format', default='long', type=click.Choice(['long', 'wide']))
@click.option('--emit-mlflow', default='no')
@click.option('--out-dir', default='features/')
def main(input, config, clusters, output_format, emit_mlflow, out_dir):
    """Feature Engineering Runner - Phase 4"""
    setup_logging()
    logger.info("Starting feature engineering...")
ECHO is on.
    start_time = time.time()
ECHO is on.
    try:
        # 1. 設定読込
        config_loader = ConfigLoader()
        spec = config_loader.load(Path(config))
ECHO is on.
        # 2. データ読込
        logger.info(f"Loading data from {input}")
        if input.endswith('.parquet'):
            df = pd.read_parquet(input)
        else:
            df = pd.read_csv(input, parse_dates=['ds'])
        logger.info(f"Loaded {len^(df^)} rows")
ECHO is on.
        # 3. ラグ特徴
        lag_builder = LagBuilder(
            lags=spec.hist.get('lag', []),
            seasonal_lags=spec.hist.get('seasonal_lag', [])
        )
        df = lag_builder.build(df)
ECHO is on.
        # 4. 移動統計
        rolling_builder = RollingBuilder(spec.hist.get('rolling', []))
        df = rolling_builder.build(df)
ECHO is on.
        if 'ema' in spec.hist:
            df = rolling_builder.build_ema(df, spec.hist['ema'])
ECHO is on.
        # 5. カレンダー特徴
        calendar_builder = CalendarBuilder(spec.calendar)
        df = calendar_builder.build(df)
ECHO is on.
        # 6. 価格/販促特徴
        if spec.price or spec.promo:
            pp_builder = PricePromoBuilder(spec.price, spec.promo)
            if spec.price:
                df = pp_builder.build_price(df)
            if spec.promo:
                df = pp_builder.build_promo(df)
ECHO is on.
        # 7. クラスタリング
        cluster_builder = ClusterBuilder(k=clusters)
        target_col = 'y_scaled' if 'y_scaled' in df.columns else 'y'
        cluster_labels = cluster_builder.build(df, target_col)
ECHO is on.
        # クラスタIDをマージ
        df = df.merge(cluster_labels[['unique_id', 'cluster_id']], on='unique_id', how='left')
ECHO is on.
        # 8. カテゴリエンコーディング
        if spec.stat:
            encoder = CategoryEncoder(mode='onehot')
            cat_cols = [c for c in spec.stat if c in df.columns and c != 'cluster_id']
            if cat_cols:
                df = encoder.fit_transform(df, cat_cols)
ECHO is on.
        # 9. 品質監査
        auditor = FeatureAuditor()
        quality = auditor.audit(df)
ECHO is on.
        # 10. 出力
        output_dir = Path(out_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
ECHO is on.
        # Features
        features_path = output_dir / "features.parquet"
        df.to_parquet(features_path)
        logger.success(f"Saved: {features_path}")
ECHO is on.
        # Cluster labels
        cluster_path = output_dir / "cluster_labels.parquet"
        cluster_labels.to_parquet(cluster_path)
        logger.success(f"Saved: {cluster_path}")
ECHO is on.
        # Catalog
        catalog = FeatureCatalog(
            version="1.0.0",
            features=[
                {"name": col, "type": "auto", "source": "generated"}
                for col in df.columns
                if col.startswith(('h_', 'cal_', 's_', 'price_', 'promo_'))
            ]
        )
        writer = CatalogWriter(output_dir)
        writer.write(catalog)
ECHO is on.
        # 11. サマリ
        elapsed = time.time() - start_time
        logger.success(f"Feature engineering completed in {elapsed:.1f}s")
        logger.info(f"Total features: {quality.n_features}")
        logger.info(f"NA rate: {quality.na_introduced_rate:.2%%}")
        logger.info(f"Clusters: {clusters}")
ECHO is on.
        return 0
ECHO is on.
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
