"""Render-time line style resolution."""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba

from paxplot.rendering._scaling import is_missing
from paxplot.state import ColorEncoding, LineStyle, LineStyleOverride


def resolve_palette(palette: str | list[str]):
    """Resolve a matplotlib colormap from a name or color list."""

    if isinstance(palette, str):
        return colormaps[palette]
    return LinearSegmentedColormap.from_list("paxplot_palette", palette)


def resolve_color_bounds(
    values: list[object],
    encoding: ColorEncoding,
) -> tuple[float, float]:
    """Resolve color normalization bounds."""

    numeric = [float(value) for value in values if not is_missing(value)]
    lower = min(numeric) if encoding.lower is None and numeric else encoding.lower
    upper = max(numeric) if encoding.upper is None and numeric else encoding.upper
    lower = 0.0 if lower is None else lower
    upper = 1.0 if upper is None else upper
    if lower == upper:
        padding = abs(lower) * 0.05 or 0.5
        return lower - padding, upper + padding
    return lower, upper


def color_for_value(
    value: Any, cmap, norm: Normalize, fallback: str
) -> tuple[float, ...]:
    """Map one value to RGBA, preserving a fallback for missing data."""

    if is_missing(value):
        return to_rgba(fallback)
    return cmap(norm(float(value)))


def resolve_line_styles(
    row_count: int,
    default: LineStyle,
    overrides: dict[int, LineStyleOverride],
    color_values: list[object] | None = None,
    encoding: ColorEncoding | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Resolve style precedence into arrays aligned to rows."""

    fallback_color = default.color or "C0"
    colors: list[tuple[float, ...] | str] = [fallback_color for _ in range(row_count)]

    if color_values is not None and encoding is not None:
        lower, upper = resolve_color_bounds(color_values, encoding)
        cmap = resolve_palette(encoding.palette)
        norm = Normalize(vmin=lower, vmax=upper, clip=True)
        colors = [
            color_for_value(value, cmap, norm, fallback_color) for value in color_values
        ]

    widths = [default.width for _ in range(row_count)]
    alphas = [default.alpha for _ in range(row_count)]
    linestyles = [default.linestyle for _ in range(row_count)]
    zorders = [
        default.zorder if default.zorder is not None else np.nan
        for _ in range(row_count)
    ]

    for index, override in overrides.items():
        if override.color is not None:
            colors[index] = override.color
        if override.width is not None:
            widths[index] = override.width
        if override.alpha is not None:
            alphas[index] = override.alpha
        if override.linestyle is not None:
            linestyles[index] = override.linestyle
        if override.zorder is not None:
            zorders[index] = override.zorder

    rgba = [
        to_rgba(color, alpha=alpha) for color, alpha in zip(colors, alphas, strict=True)
    ]
    return (
        np.asarray(rgba, dtype=float),
        np.asarray(widths, dtype=float),
        np.asarray(alphas, dtype=float),
        np.asarray(linestyles, dtype=object),
        np.asarray(zorders, dtype=float),
    )
