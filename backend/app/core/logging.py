"""Logging configuration (WBS 1.7.4).

Sets up a single structured (key=value) stream handler so container logs are
greppable and ready for a central aggregator. Idempotent so repeated app
factory calls in tests don't stack handlers.
"""
from __future__ import annotations

import logging

_CONFIGURED = False
_FORMAT = "%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_FORMAT))
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
