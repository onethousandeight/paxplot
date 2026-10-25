"""Axis scaling helpers."""

from __future__ import annotations

from collections.abc import Sequence
from math import isnan
from typing import Any

import numpy as np

from paxplot.state import AxisScale


def is_missing(value: Any) -> bool:
    """Return True for None and NaN-like values."""

    if value is None:
        return True
    try:
        return bool(isnan(value))
    except TypeError:
        return False


def numeric_bounds(values: Sequence[object], scale: AxisScale) -> tuple[float, float]:
    """Resolve numeric bounds from configured limits and data."""

    finite = [float(value) for value in values if not is_missing(value)]
    data_lower = min(finite) if finite else 0.0
    data_upper = max(finite) if finite else 1.0
    lower = data_lower if scale.limits[0] is None else scale.limits[0]
    upper = data_upper if scale.limits[1] is None else scale.limits[1]
    if lower == upper:
        padding = abs(lower) * 0.05 or 0.5
        return lower - padding, upper + padding
    return lower, upper


def scale_numeric_value(value: object, lower: float, upper: float) -> float:
    """Scale one numeric value to normalized coordinates."""

    if is_missing(value):
        return float("nan")
    return (float(value) - lower) / (upper - lower)


def resolve_categories(values: Sequence[object], scale: AxisScale) -> list[str]:
    """Resolve categorical order from config or first appearance."""

    if scale.categories is not None:
        return scale.categories

    categories: list[str] = []
    for value in values:
        if is_missing(value):
            continue
        category = str(value)
        if category not in categories:
            categories.append(category)
    return categories


def scale_categorical_value(value: object, categories: Sequence[str]) -> float:
    """Scale one categorical value to normalized coordinates."""

    if is_missing(value):
        return float("nan")
    category = str(value)
    if category not in categories:
        msg = f"unknown category {category!r}"
        raise ValueError(msg)
    if len(categories) == 1:
        return 0.5
    return categories.index(category) / (len(categories) - 1)


def apply_inversion(values: np.ndarray, inverted: bool) -> np.ndarray:
    """Apply axis inversion after scaling."""

    if not inverted:
        return values
    return 1.0 - values
