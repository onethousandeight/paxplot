"""Internal render-ready data containers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from paxplot.state import FontSpec


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
    title_font: FontSpec
    tick_labels_font: FontSpec


@dataclass
class RenderColorbar:
    axis: int
    palette: str | list[str]
    label: str | None
    lower: float
    upper: float
    title_visible: bool
    title_font: FontSpec
    tick_labels_font: FontSpec
    tick_labels_visible: bool


@dataclass
class RenderData:
    x: np.ndarray
    y: np.ndarray
    axes: list[RenderAxis]
    line_colors: np.ndarray
    line_widths: np.ndarray
    line_linestyles: np.ndarray
    line_zorders: np.ndarray
    colorbar: RenderColorbar | None = None
