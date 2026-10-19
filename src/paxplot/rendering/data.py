"""Internal render-ready data containers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from paxplot.state import LineStyle


@dataclass
class RenderAxis:
    label: str
    x: float
    tick_positions: list[float]
    tick_labels: list[str]
    spine_visible: bool
    label_visible: bool
    tick_marks_visible: bool
    tick_labels_visible: bool


@dataclass
class RenderColorbar:
    axis: int
    palette: str | list[str]
    label: str | None
    lower: float
    upper: float


@dataclass
class RenderData:
    x: np.ndarray
    y: np.ndarray
    axes: list[RenderAxis]
    default_line_style: LineStyle
    line_colors: np.ndarray | None = None
    line_widths: np.ndarray | None = None
    line_alphas: np.ndarray | None = None
    line_linestyles: np.ndarray | None = None
    line_zorders: np.ndarray | None = None
    colorbar: RenderColorbar | None = None
