"""CLI エントリーポインチE""
import click
from loguru import logger
from pathlib import Path


@click.command()
@click.option('--dry-run', is_flag=True, help='Dry-run mode')
@click.option('--spec', type=click.Path(exists=True), required=True)
@click.option('--invalid', type=click.Path(exists=True))
@click.option('--time-budget', default='12h')
@click.option('--max-combos', default=500, type=int)
@click.option('--out-dir', default='plan/')
def main(dry_run, spec, invalid, time_budget, max_combos, out_dir):
    """nfops-planner CLI"""
    logger.info("Starting planner...")
    logger.info(f"Spec: {spec}")
    logger.info(f"Max combos: {max_combos}")
    click.echo("Planning completed ^(skeleton^)")


if __name__ == '__main__':
    main()
