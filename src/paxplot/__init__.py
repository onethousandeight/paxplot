"""PaxPlot public API."""

from paxplot.datasets import hydroclimate_model_evaluation, tradeoff
from paxplot.plot import ParallelPlot
from paxplot.state import (
    AxisPresentation,
    AxisScale,
    AxisSpine,
    AxisTickLabels,
    AxisTickMarks,
    AxisTicks,
    AxisTitle,
    ColorbarPresentation,
    ColorbarTitle,
    ColorEncoding,
    ColumnSpec,
    LinePresentation,
    LineStyle,
    LineStyleOverride,
    PlotData,
    PlotPresentation,
    PlotState,
    TextAppearance,
)

__all__ = [
    "AxisPresentation",
    "AxisScale",
    "AxisSpine",
    "AxisTickLabels",
    "AxisTickMarks",
    "AxisTicks",
    "AxisTitle",
    "ColorbarPresentation",
    "ColorbarTitle",
    "ColorEncoding",
    "ColumnSpec",
    "LinePresentation",
    "LineStyle",
    "LineStyleOverride",
    "PlotData",
    "PlotPresentation",
    "PlotState",
    "TextAppearance",
    "ParallelPlot",
    "hydroclimate_model_evaluation",
    "tradeoff",
]
