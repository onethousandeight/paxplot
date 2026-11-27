"""Tick resolution helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from paxplot._values import finite_float
from paxplot.rendering._scaling import (
    apply_inversion,
    scale_categorical_value,
    scale_numeric_value,
)
from paxplot.state import AxisPresentation


def format_tick(value: float) -> str:
    """Format readable numeric tick labels."""

    return f"{value:g}"


def _resolve_labels(
    configured: list[str] | None,
    defaults: list[str],
    *,
    kind: str,
) -> list[str]:
    labels = configured if configured is not None else defaults
    if len(labels) != len(defaults):
        msg = f"{kind} tick labels must match the number of tick values"
        raise ValueError(msg)
    return labels


def resolve_numeric_ticks(
    axis: AxisPresentation,
    lower: float,
    upper: float,
) -> tuple[list[float], list[str]]:
    """Resolve numeric tick positions and labels."""

    if axis.ticks.values is not None:
        values = axis.ticks.values
        for value in values:
            finite_float(value, kind="numeric tick")
        positions = [scale_numeric_value(value, lower, upper) for value in values]
        default_labels = [str(value) for value in values]
    else:
        count = axis.ticks.count or 5
        values = np.linspace(lower, upper, count).tolist()
        positions = [scale_numeric_value(value, lower, upper) for value in values]
        default_labels = [format_tick(value) for value in values]

    labels = _resolve_labels(
        axis.ticks.labels.text,
        default_labels,
        kind="numeric",
    )
    scaled = apply_inversion(np.asarray(positions, dtype=float), axis.scale.inverted)
    return scaled.tolist(), labels


def resolve_categorical_ticks(
    axis: AxisPresentation,
    categories: Sequence[str],
    positions: Mapping[str, int],
) -> tuple[list[float], list[str]]:
    """Resolve categorical tick positions and labels."""

    values = axis.ticks.values if axis.ticks.values is not None else list(categories)
    tick_positions = [
        scale_categorical_value(value, positions, len(categories)) for value in values
    ]
    default_labels = [str(value) for value in values]
    labels = _resolve_labels(
        axis.ticks.labels.text,
        default_labels,
        kind="categorical",
    )
    scaled = apply_inversion(
        np.asarray(tick_positions, dtype=float), axis.scale.inverted
    )
    return scaled.tolist(), labels
