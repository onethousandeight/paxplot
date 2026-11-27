"""Axis scaling helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np

from paxplot._values import finite_float, is_missing, padded_bounds
from paxplot.state import AxisScale


def numeric_bounds(numbers: np.ndarray, scale: AxisScale) -> tuple[float, float]:
    """Resolve numeric bounds from a column array of prepared numeric values."""

    infinite = np.isinf(numbers)
    if infinite.any():
        msg = f"numeric value {numbers[infinite][0]!r} is not a finite number"
        raise ValueError(msg)

    finite = numbers[np.isfinite(numbers)]
    data_lower = float(finite.min()) if finite.size else 0.0
    data_upper = float(finite.max()) if finite.size else 1.0
    lower = data_lower if scale.limits[0] is None else scale.limits[0]
    upper = data_upper if scale.limits[1] is None else scale.limits[1]
    if not math.isfinite(lower) or not math.isfinite(upper):
        msg = "axis limits must be finite"
        raise ValueError(msg)
    if lower > upper:
        msg = "axis lower limit cannot be greater than upper limit"
        raise ValueError(msg)
    return padded_bounds(lower, upper)


def scale_numeric_value(value: object, lower: float, upper: float) -> float:
    """Scale one numeric value to normalized coordinates."""

    if is_missing(value):
        return float("nan")
    number = finite_float(value, kind="numeric")
    return (number - lower) / (upper - lower)


def scale_categorical_value(
    value: object, positions: Mapping[str, int], category_count: int
) -> float:
    """Scale one categorical value to normalized coordinates."""

    if is_missing(value):
        return float("nan")
    category = str(value)
    try:
        index = positions[category]
    except KeyError as exc:
        msg = f"unknown category {category!r}"
        raise ValueError(msg) from exc
    if category_count == 1:
        return 0.5
    return index / (category_count - 1)


def apply_inversion(values: np.ndarray, inverted: bool) -> np.ndarray:
    """Apply axis inversion after scaling."""

    if not inverted:
        return values
    return 1.0 - values
