from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Iterator


LOGGER_NAME = "sentinelai_aws_agent"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger()


def log_event(event_type: str, **kwargs: Any) -> None:
    payload = {"event_type": event_type, **kwargs}
    logger.info(json.dumps(payload, default=str))


@contextmanager
def trace_span(span_name: str, **metadata: Any) -> Iterator[dict[str, Any]]:
    started = time.perf_counter()
    trace = {"span": span_name, "metadata": metadata}
    log_event("span.started", span_name=span_name, metadata=metadata)
    try:
        yield trace
    finally:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        trace["elapsed_ms"] = elapsed_ms
        log_event("span.finished", span_name=span_name, elapsed_ms=elapsed_ms, metadata=metadata)


def metric(name: str, value: float, unit: str = "Milliseconds", **dimensions: Any) -> None:
    log_event("metric", metric_name=name, value=value, unit=unit, dimensions=dimensions)
