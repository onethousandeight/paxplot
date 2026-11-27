"""Shared value helpers for data handling and rendering."""

from __future__ import annotations

import functools
import math
from collections.abc import Iterable
from typing import Any

import numpy as np


@functools.cache
def _pandas_sentinels() -> tuple[object, ...]:
    """Return pandas missing singletons when pandas is available."""

    try:
        from pandas import NA, NaT
    except ImportError:
        return ()
    return (NA, NaT)


def is_missing(value: Any) -> bool:
    """Return True for None, NaN-like values, and pandas missing sentinels."""

    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    if isinstance(value, np.floating):
        return bool(np.isnan(value))
    return any(value is sentinel for sentinel in _pandas_sentinels())


def finite_float(value: Any, *, kind: str) -> float:
    """Convert a numeric value, rejecting non-finite or unrepresentable inputs."""

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        msg = f"{kind} value {value!r} is not a finite number"
        raise ValueError(msg) from exc
    if not math.isfinite(number):
        msg = f"non-finite {kind} value {value!r}"
        raise ValueError(msg)
    return number


def resolve_categories(
    values: Iterable[object], categories: Iterable[str] | None = None
) -> list[str]:
    """Resolve categorical order from configuration or first appearance."""

    if categories is not None:
        return list(categories)

    resolved: list[str] = []
    seen: set[str] = set()
    for value in values:
        if is_missing(value):
            continue
        category = str(value)
        if category not in seen:
            seen.add(category)
            resolved.append(category)
    return resolved


def category_positions(categories: Iterable[str]) -> dict[str, int]:
    """Map category names to their normalized position index."""

    return {category: index for index, category in enumerate(categories)}


def padded_bounds(lower: float, upper: float) -> tuple[float, float]:
    """Expand a degenerate range so a constant column still has a scale."""

    if lower != upper:
        return lower, upper
    padding = abs(lower) * 0.05 or 0.5
    return lower - padding, upper + padding
