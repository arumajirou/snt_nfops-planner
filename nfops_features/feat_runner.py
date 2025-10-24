# -*- coding: utf-8 -*-
"""Feature CLI (placeholder)."""
from __future__ import annotations

import sys
import click


@click.command()
@click.option("--spec", type=click.Path(exists=False), required=False, help="Path to feature spec.")
def main(spec: str | None = None) -> None:
    """Minimal no-op to keep the module syntactically valid."""
    click.echo("nfops_features.feat_runner: placeholder")
    if spec:
        click.echo(f"spec={spec}")
    sys.exit(0)


if __name__ == "__main__":
    main()
