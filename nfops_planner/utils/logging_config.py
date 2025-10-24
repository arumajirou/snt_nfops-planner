# -*- coding: utf-8 -*-
"""Logging configuration helpers (placeholder)."""
from __future__ import annotations

import logging
from logging import Logger


def configure_basic(level: int = logging.INFO) -> Logger:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return logging.getLogger("nfops_planner")
