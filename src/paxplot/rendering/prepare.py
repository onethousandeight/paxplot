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

    if not state.axes:
        msg = "cannot render a plot without data"
        raise ValueError(msg)

    row_count = len(state.data)
    axis_count = len(state.axes)
    y = np.full((row_count, axis_count), np.nan, dtype=float)
    x = np.arange(axis_count, dtype=float)
    render_axes: list[RenderAxis] = []

    for axis_index, axis in enumerate(state.axes):
        column = [row[axis_index] for row in state.data]
        if axis.dtype == "numeric":
            lower, upper = numeric_bounds(column, axis)
            scaled = np.asarray(
                [scale_numeric_value(value, lower, upper) for value in column],
                dtype=float,
            )
            tick_positions, tick_labels = resolve_numeric_ticks(axis, lower, upper)
        else:
            categories = resolve_categories(column, axis)
            scaled = np.asarray(
                [scale_categorical_value(value, categories) for value in column],
                dtype=float,
            )
            tick_positions, tick_labels = resolve_categorical_ticks(axis, categories)

        y[:, axis_index] = apply_inversion(scaled, axis.inverted)
        render_axes.append(
            RenderAxis(
                label=axis.label or f"Axis {axis_index + 1}",
                x=float(x[axis_index]),
                tick_positions=tick_positions,
                tick_labels=tick_labels,
                spine_visible=axis.spine_style.visible,
                label_visible=axis.label_style.visible,
                tick_marks_visible=axis.ticks.mark_style.visible,
                tick_labels_visible=axis.ticks.label_style.visible,
            )
        )

    color_values = None
    colorbar = None
    if state.color_encoding is not None:
        color_values = [row[state.color_encoding.axis] for row in state.data]
        lower, upper = resolve_color_bounds(color_values, state.color_encoding)
        colorbar = RenderColorbar(
            axis=state.color_encoding.axis,
            palette=state.color_encoding.palette,
            label=state.color_encoding.colorbar.label,
            lower=lower,
            upper=upper,
        )

    colors, widths, alphas, linestyles, zorders = resolve_line_styles(
        row_count,
        state.default_line_style,
        state.line_styles,
        color_values=color_values,
        encoding=state.color_encoding,
    )

    return RenderData(
        x=x,
        y=y,
        axes=render_axes,
        default_line_style=state.default_line_style,
        line_colors=colors,
        line_widths=widths,
        line_alphas=alphas,
        line_linestyles=linestyles,
        line_zorders=zorders,
        colorbar=colorbar,
    )
