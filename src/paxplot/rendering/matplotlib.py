"""Matplotlib renderer for PaxPlot."""

from __future__ import annotations

import warnings
from collections import defaultdict

import numpy as np
from matplotlib import rcParams
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.text import Text

from paxplot.rendering._styles import resolve_palette
from paxplot.rendering.data import RenderData
from paxplot.state import FontSpec

# CSS weight names that matplotlib does not accept directly.
_WEIGHT_MAP = {"thin": 100, "extra light": 200}


def _matplotlib_weight(weight: str) -> str | int:
    """Translate renderer-neutral weight names to matplotlib values."""

    mapped = _WEIGHT_MAP.get(weight)
    if mapped is None:
        return weight
    warnings.warn(
        f"font weight {weight!r} is not supported by matplotlib; using {mapped}",
        UserWarning,
        stacklevel=3,
    )
    return mapped


def _apply_font(text: Text, font: FontSpec) -> None:
    """Apply explicit overrides without replacing role-specific defaults.

    Implements the FontSpec portability contract for matplotlib: only
    fields the user set are applied, and unset fields keep matplotlib's
    role-specific defaults.
    """

    values = font.model_dump(exclude_none=True)
    if "weight" in values:
        values["weight"] = _matplotlib_weight(values["weight"])
    text.set(**{f"font{name}": value for name, value in values.items()})


def _segments(render_data: RenderData) -> np.ndarray:
    x = np.broadcast_to(render_data.x, render_data.y.shape)
    return np.stack((x, render_data.y), axis=-1)


def _points_to_data(fig, ax, points: float) -> float:
    """Convert a physical length in points to data units along the x-axis."""

    bbox = ax.bbox
    left, right = ax.get_xlim()
    if bbox.width <= 0 or right <= left:
        return points / 72.0
    return points * (fig.dpi / 72.0) * (right - left) / bbox.width


def _right_limit_for_labels(
    fig, ax, labels: list[Text], base_right: float, margin_px: float = 16.0
) -> float:
    """Return a right x-limit that keeps right-side labels clear of the colorbar."""

    if not labels:
        return base_right

    try:
        renderer = fig.canvas.get_renderer()
    except AttributeError:
        longest = max(len(label.get_text()) for label in labels)
        return max(base_right, 0.1 + 0.04 * longest)

    left, right = ax.get_xlim()
    bbox = ax.bbox
    if bbox.width <= 0 or right <= left:
        return base_right

    boundary = fig.bbox.x1 - margin_px
    if len(fig.axes) > 1:
        boundary = min(boundary, fig.axes[-1].bbox.x0 - margin_px)

    required = right
    for label in labels:
        extent = label.get_window_extent(renderer=renderer)
        x_data = label.get_position()[0]
        available = boundary - extent.width - bbox.x0
        if available > 0:
            candidate = left + (x_data - left) * bbox.width / available
        else:
            overflow = extent.width - (boundary - bbox.x0)
            candidate = right + overflow * (right - left) / bbox.width
        required = max(required, candidate)

    return max(base_right, required)


def render_matplotlib(render_data: RenderData, **kwargs: object) -> Figure:
    """Draw render-ready data with matplotlib and return a Figure."""

    import matplotlib.pyplot as plt

    figsize = kwargs.pop("figsize", None)
    fig, ax = plt.subplots(figsize=figsize, **kwargs)

    segments = _segments(render_data)
    groups: dict[float, list[int]] = defaultdict(list)
    for index, zorder in enumerate(render_data.line_zorders):
        key = 2.0 if np.isnan(zorder) else float(zorder)
        groups[key].append(index)

    for zorder, indices in sorted(groups.items()):
        collection = LineCollection(
            segments[indices],
            colors=render_data.line_colors[indices],
            linewidths=render_data.line_widths[indices],
            linestyles=render_data.line_linestyles[indices].tolist(),
            zorder=zorder,
        )
        ax.add_collection(collection)

    axis_color = rcParams["axes.edgecolor"]
    axis_linewidth = rcParams["axes.linewidth"]
    # Tick geometry follows matplotlib's ytick.major defaults.
    tick_length_points = rcParams["ytick.major.size"]
    tick_label_offset_points = tick_length_points + rcParams["ytick.major.pad"]
    last_axis_index = len(render_data.axes) - 1
    right_labels: list[Text] = []
    label_specs: list[tuple[Text, str, float]] = []

    for axis_index, axis in enumerate(render_data.axes):
        side = "right" if axis_index == last_axis_index else "left"
        if axis.spine_visible:
            ax.vlines(
                axis.x,
                0.0,
                1.0,
                color=axis_color,
                linewidth=axis_linewidth,
                capstyle="projecting",
                zorder=3,
            )
        if axis.label_visible:
            title = ax.text(
                axis.x,
                1.04,
                axis.label,
                ha="center",
                va="bottom",
                fontsize=rcParams["axes.titlesize"],
                fontweight=rcParams["axes.titleweight"],
            )
            _apply_font(title, axis.title_font)
        if axis.tick_labels_visible:
            horizontal_alignment = "left" if side == "right" else "right"
            for position, label in zip(
                axis.tick_positions, axis.tick_labels, strict=True
            ):
                # Provisional position; corrected once the final x-limit is known.
                tick_label = ax.text(
                    axis.x,
                    position,
                    label,
                    ha=horizontal_alignment,
                    va="center",
                    fontsize=rcParams["ytick.labelsize"],
                )
                _apply_font(tick_label, axis.tick_labels_font)
                label_specs.append((tick_label, side, axis.x))
                if side == "right":
                    right_labels.append(tick_label)

    left_limit = float(render_data.x.min()) - 0.2
    right_limit = float(render_data.x.max()) + 0.2
    ax.set_xlim(left_limit, right_limit)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    if render_data.colorbar is not None:
        cmap = resolve_palette(render_data.colorbar.palette)
        norm = Normalize(
            vmin=render_data.colorbar.lower,
            vmax=render_data.colorbar.upper,
            clip=True,
        )
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])
        colorbar = fig.colorbar(mappable, ax=ax)
        if (
            render_data.colorbar.title_visible
            and render_data.colorbar.label is not None
        ):
            colorbar.set_label(render_data.colorbar.label)
        long_axis = (
            colorbar.ax.yaxis
            if colorbar.orientation == "vertical"
            else colorbar.ax.xaxis
        )
        _apply_font(long_axis.label, render_data.colorbar.title_font)
        for tick in (*long_axis.get_major_ticks(), *long_axis.get_minor_ticks()):
            _apply_font(tick.label1, render_data.colorbar.tick_labels_font)
            _apply_font(tick.label2, render_data.colorbar.tick_labels_font)
        _apply_font(long_axis.get_offset_text(), render_data.colorbar.tick_labels_font)
        if not render_data.colorbar.tick_labels_visible:
            colorbar.ax.tick_params(
                which="both",
                labelleft=False,
                labelright=False,
                labeltop=False,
                labelbottom=False,
            )
            long_axis.get_offset_text().set_visible(False)

    # The colorbar shrinks the axes, so settle right-label space and physical tick
    # geometry after it exists. Moving the labels changes the required right limit,
    # which changes the data-units scale, so iterate until both are stable.
    right_limit = _right_limit_for_labels(fig, ax, right_labels, right_limit)
    for _ in range(16):
        ax.set_xlim(left_limit, right_limit)
        offset = _points_to_data(fig, ax, tick_label_offset_points)
        for text, side, axis_x in label_specs:
            text.set_x(axis_x + offset if side == "right" else axis_x - offset)
        updated = _right_limit_for_labels(fig, ax, right_labels, right_limit)
        if np.isclose(updated, right_limit, rtol=1e-6, atol=1e-9):
            break
        right_limit = updated

    ax.set_xlim(left_limit, right_limit)
    offset = _points_to_data(fig, ax, tick_label_offset_points)
    for text, side, axis_x in label_specs:
        text.set_x(axis_x + offset if side == "right" else axis_x - offset)

    tick_length = _points_to_data(fig, ax, tick_length_points)
    for axis_index, axis in enumerate(render_data.axes):
        if not axis.tick_marks_visible:
            continue
        side = "right" if axis_index == last_axis_index else "left"
        for position in axis.tick_positions:
            if side == "right":
                start, end = axis.x, axis.x + tick_length
            else:
                start, end = axis.x - tick_length, axis.x
            ax.hlines(
                position,
                start,
                end,
                color=axis_color,
                linewidth=axis_linewidth,
                capstyle="butt",
                zorder=4,
            )

    return fig
