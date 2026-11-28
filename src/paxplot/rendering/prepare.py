"""Convert serializable plot state into render-ready arrays."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from paxplot._values import category_positions, resolve_categories
from paxplot.rendering._scaling import (
    apply_inversion,
    numeric_bounds,
    scale_categorical_value,
)
from paxplot.rendering._styles import (
    resolve_color_bounds,
    resolve_colors,
    resolve_line_styles,
)
from paxplot.rendering._ticks import resolve_categorical_ticks, resolve_numeric_ticks
from paxplot.rendering.data import RenderAxis, RenderColorbar, RenderData
from paxplot.state import PlotState


def _numeric_array(column: Sequence[object]) -> np.ndarray:
    """Convert a validated numeric column to floats; missing values become NaN."""

    try:
        return np.asarray(column, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        msg = "numeric columns support numbers and missing values only"
        raise ValueError(msg) from exc


def prepare_render_data(state: PlotState) -> RenderData:
    """Prepare normalized coordinates and resolved drawing metadata."""

    axes = state.presentation.axes
    lines = state.presentation.lines
    rows = state.data.rows
    if not axes:
        msg = "cannot render a plot without data"
        raise ValueError(msg)

    row_count = len(rows)
    axis_count = len(axes)
    y = np.full((row_count, axis_count), np.nan, dtype=float)
    x = np.arange(axis_count, dtype=float)
    columns = list(zip(*rows, strict=True))
    render_axes: list[RenderAxis] = []

    for axis_index, axis in enumerate(axes):
        column = columns[axis_index]
        if state.data.columns[axis_index].dtype == "numeric":
            numbers = _numeric_array(column)
            lower, upper = numeric_bounds(numbers, axis.scale)
            scaled = (numbers - lower) / (upper - lower)
            tick_positions, tick_labels = resolve_numeric_ticks(axis, lower, upper)
        else:
            categories = resolve_categories(column, axis.scale.categories)
            positions = category_positions(categories)
            scaled = np.asarray(
                [
                    scale_categorical_value(value, positions, len(categories))
                    for value in column
                ],
                dtype=float,
            )
            tick_positions, tick_labels = resolve_categorical_ticks(
                axis, categories, positions
            )

        y[:, axis_index] = apply_inversion(scaled, axis.scale.inverted)
        render_axes.append(
            RenderAxis(
                label=(
                    axis.title.text
                    if axis.title.text is not None
                    else f"Axis {axis_index + 1}"
                ),
                x=float(x[axis_index]),
                tick_positions=tick_positions,
                tick_labels=tick_labels,
                spine_visible=axis.spine.visible,
                label_visible=axis.title.visible,
                tick_marks_visible=axis.ticks.marks.visible,
                tick_labels_visible=axis.ticks.labels.visible,
                title_font=axis.title.font,
                tick_labels_font=axis.ticks.labels.font,
            )
        )

    encoding = lines.color_encoding
    base_colors = None
    colorbar = None
    if encoding is not None:
        color_values = [row[encoding.axis] for row in rows]
        lower, upper = resolve_color_bounds(color_values, encoding)
        base_colors = resolve_colors(
            color_values,
            encoding.palette,
            lower,
            upper,
            fallback=lines.default.color or "C0",
        )
        colorbar = RenderColorbar(
            axis=encoding.axis,
            palette=encoding.palette,
            label=encoding.colorbar.title.text,
            title_visible=encoding.colorbar.title.visible,
            title_font=encoding.colorbar.title.font,
            tick_labels_font=encoding.colorbar.ticks.labels.font,
            tick_labels_visible=encoding.colorbar.ticks.labels.visible,
            lower=lower,
            upper=upper,
        )

    colors, widths, linestyles, zorders = resolve_line_styles(
        row_count,
        lines.default,
        lines.overrides,
        base_colors=base_colors,
    )

    return RenderData(
        x=x,
        y=y,
        axes=render_axes,
        line_colors=colors,
        line_widths=widths,
        line_linestyles=linestyles,
        line_zorders=zorders,
        colorbar=colorbar,
    )
