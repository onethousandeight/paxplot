"""Matplotlib renderer for PaxPlot."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize

from paxplot.rendering._styles import resolve_palette
from paxplot.rendering.data import RenderData


def _segments(render_data: RenderData) -> np.ndarray:
    x = np.broadcast_to(render_data.x, render_data.y.shape)
    return np.stack((x, render_data.y), axis=-1)


def render_matplotlib(render_data: RenderData, **kwargs):
    """Draw render-ready data with matplotlib and return a Figure."""

    import matplotlib.pyplot as plt

    figsize = kwargs.pop("figsize", None)
    fig, ax = plt.subplots(figsize=figsize, **kwargs)

    segments = _segments(render_data)
    zorders = (
        render_data.line_zorders
        if render_data.line_zorders is not None
        else np.full(render_data.y.shape[0], np.nan)
    )
    groups: dict[float, list[int]] = defaultdict(list)
    for index, zorder in enumerate(zorders):
        key = 2.0 if np.isnan(zorder) else float(zorder)
        groups[key].append(index)

    for zorder, indices in sorted(groups.items()):
        collection = LineCollection(
            segments[indices],
            colors=None
            if render_data.line_colors is None
            else render_data.line_colors[indices],
            linewidths=(
                None
                if render_data.line_widths is None
                else render_data.line_widths[indices]
            ),
            linestyles=(
                "solid"
                if render_data.line_linestyles is None
                else render_data.line_linestyles[indices].tolist()
            ),
            zorder=zorder,
        )
        ax.add_collection(collection)

    axis_color = "0.2"
    tick_color = "0.35"
    tick_half_width = 0.035
    for axis in render_data.axes:
        if axis.spine_visible:
            ax.vlines(axis.x, 0.0, 1.0, color=axis_color, linewidth=1.0, zorder=3)
        if axis.label_visible:
            ax.text(
                axis.x,
                1.04,
                axis.label,
                ha="center",
                va="bottom",
                fontsize="medium",
            )
        for position, label in zip(axis.tick_positions, axis.tick_labels, strict=True):
            if axis.tick_marks_visible:
                ax.hlines(
                    position,
                    axis.x - tick_half_width,
                    axis.x + tick_half_width,
                    color=tick_color,
                    linewidth=0.8,
                    zorder=4,
                )
            if axis.tick_labels_visible:
                ax.text(
                    axis.x - tick_half_width * 1.8,
                    position,
                    label,
                    ha="right",
                    va="center",
                    fontsize="small",
                )

    ax.set_xlim(float(render_data.x.min()) - 0.2, float(render_data.x.max()) + 0.2)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    if render_data.colorbar is not None:
        cmap = resolve_palette(render_data.colorbar.palette)
        norm = Normalize(
            vmin=render_data.colorbar.lower, vmax=render_data.colorbar.upper
        )
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])
        colorbar = fig.colorbar(mappable, ax=ax)
        if render_data.colorbar.label is not None:
            colorbar.set_label(render_data.colorbar.label)

    return fig
