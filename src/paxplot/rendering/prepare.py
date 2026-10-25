"""Convert serializable plot state into render-ready arrays."""

from __future__ import annotations

import numpy as np

from paxplot.rendering._scaling import (
    apply_inversion,
    numeric_bounds,
    resolve_categories,
    scale_categorical_value,
    scale_numeric_value,
)
from paxplot.rendering._styles import resolve_color_bounds, resolve_line_styles
from paxplot.rendering._ticks import resolve_categorical_ticks, resolve_numeric_ticks
from paxplot.rendering.data import RenderAxis, RenderColorbar, RenderData
from paxplot.state import PlotState


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
    render_axes: list[RenderAxis] = []

    for axis_index, axis in enumerate(axes):
        column = [row[axis_index] for row in rows]
        if state.data.columns[axis_index].dtype == "numeric":
            lower, upper = numeric_bounds(column, axis.scale)
            scaled = np.asarray(
                [scale_numeric_value(value, lower, upper) for value in column],
                dtype=float,
            )
            tick_positions, tick_labels = resolve_numeric_ticks(axis, lower, upper)
        else:
            categories = resolve_categories(column, axis.scale)
            scaled = np.asarray(
                [scale_categorical_value(value, categories) for value in column],
                dtype=float,
            )
            tick_positions, tick_labels = resolve_categorical_ticks(axis, categories)

        y[:, axis_index] = apply_inversion(scaled, axis.scale.inverted)
        render_axes.append(
            RenderAxis(
                label=axis.title.text or f"Axis {axis_index + 1}",
                x=float(x[axis_index]),
                tick_positions=tick_positions,
                tick_labels=tick_labels,
                spine_visible=axis.spine.visible,
                label_visible=axis.title.visible,
                tick_marks_visible=axis.ticks.marks.visible,
                tick_labels_visible=axis.ticks.labels.visible,
            )
        )

    encoding = lines.color_encoding
    color_values = None
    colorbar = None
    if encoding is not None:
        color_values = [row[encoding.axis] for row in rows]
        lower, upper = resolve_color_bounds(color_values, encoding)
        colorbar = RenderColorbar(
            axis=encoding.axis,
            palette=encoding.palette,
            label=encoding.colorbar.title.text,
            title_visible=encoding.colorbar.title.visible,
            lower=lower,
            upper=upper,
        )

    colors, widths, alphas, linestyles, zorders = resolve_line_styles(
        row_count,
        lines.default,
        lines.overrides,
        color_values=color_values,
        encoding=encoding,
    )

    return RenderData(
        x=x,
        y=y,
        axes=render_axes,
        default_line_style=lines.default,
        line_colors=colors,
        line_widths=widths,
        line_alphas=alphas,
        line_linestyles=linestyles,
        line_zorders=zorders,
        colorbar=colorbar,
    )
