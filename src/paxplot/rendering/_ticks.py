"""Tick resolution helpers."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from paxplot.rendering._scaling import (
    apply_inversion,
    scale_categorical_value,
    scale_numeric_value,
)
from paxplot.state import AxisPresentation


def format_tick(value: float) -> str:
    """Format readable numeric tick labels."""

    return f"{value:g}"


def resolve_numeric_ticks(
    axis: AxisPresentation,
    lower: float,
    upper: float,
) -> tuple[list[float], list[str]]:
    """Resolve numeric tick positions and labels."""

    if axis.ticks.values is not None:
        positions = [
            scale_numeric_value(value, lower, upper) for value in axis.ticks.values
        ]
        labels = axis.ticks.labels.text or [str(value) for value in axis.ticks.values]
    else:
        count = axis.ticks.count or 5
        values = np.linspace(lower, upper, count).tolist()
        positions = [scale_numeric_value(value, lower, upper) for value in values]
        labels = [format_tick(value) for value in values]

    scaled = apply_inversion(np.asarray(positions, dtype=float), axis.scale.inverted)
    return scaled.tolist(), labels


def resolve_categorical_ticks(
    axis: AxisPresentation,
    categories: Sequence[str],
) -> tuple[list[float], list[str]]:
    """Resolve categorical tick positions and labels."""

    values = axis.ticks.values if axis.ticks.values is not None else list(categories)
    positions = [scale_categorical_value(value, categories) for value in values]
    labels = axis.ticks.labels.text or [str(value) for value in values]
    scaled = apply_inversion(np.asarray(positions, dtype=float), axis.scale.inverted)
    return scaled.tolist(), labels
