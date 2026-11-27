"""Render-time line style resolution."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, Normalize, to_rgba

from paxplot._values import finite_float, is_missing, padded_bounds
from paxplot.state import ColorEncoding, LineStyle, LineStyleOverride


def resolve_palette(palette: str | list[str]) -> Colormap:
    """Resolve a matplotlib colormap from a name or color list."""

    if isinstance(palette, str):
        return colormaps[palette]
    return LinearSegmentedColormap.from_list("paxplot_palette", palette)


def resolve_color_bounds(
    values: list[object],
    encoding: ColorEncoding,
) -> tuple[float, float]:
    """Resolve color normalization bounds."""

    numeric: list[float] = []
    for value in values:
        if is_missing(value):
            continue
        numeric.append(finite_float(value, kind="color"))

    lower = min(numeric) if encoding.lower is None and numeric else encoding.lower
    upper = max(numeric) if encoding.upper is None and numeric else encoding.upper
    lower = 0.0 if lower is None else lower
    upper = 1.0 if upper is None else upper
    if not math.isfinite(lower) or not math.isfinite(upper):
        msg = "color encoding bounds must be finite"
        raise ValueError(msg)
    if lower > upper:
        msg = "color encoding lower limit cannot be greater than upper limit"
        raise ValueError(msg)
    return padded_bounds(lower, upper)


def color_for_value(
    value: Any, cmap: Colormap, norm: Normalize, fallback: str
) -> tuple[float, ...]:
    """Map one value to RGBA, preserving a fallback for missing data."""

    if is_missing(value):
        return to_rgba(fallback)
    return cmap(norm(finite_float(value, kind="color")))


def resolve_colors(
    values: list[object],
    palette: str | list[str],
    lower: float,
    upper: float,
    fallback: str,
) -> list[tuple[float, ...] | str]:
    """Resolve one color per value using already-resolved bounds."""

    cmap = resolve_palette(palette)
    norm = Normalize(vmin=lower, vmax=upper, clip=True)
    return [color_for_value(value, cmap, norm, fallback) for value in values]


def resolve_line_styles(
    row_count: int,
    default: LineStyle,
    overrides: dict[int, LineStyleOverride],
    *,
    base_colors: list[tuple[float, ...] | str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Resolve style precedence into arrays aligned to rows."""

    fallback_color = default.color or "C0"
    colors: list[tuple[float, ...] | str] = (
        list(base_colors)
        if base_colors is not None
        else [fallback_color for _ in range(row_count)]
    )

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

    if not np.all(np.isfinite(widths)):
        msg = "line widths must be finite"
        raise ValueError(msg)

    rgba = [
        to_rgba(color, alpha=alpha) for color, alpha in zip(colors, alphas, strict=True)
    ]
    return (
        np.asarray(rgba, dtype=float),
        np.asarray(widths, dtype=float),
        np.asarray(linestyles, dtype=object),
        np.asarray(zorders, dtype=float),
    )
