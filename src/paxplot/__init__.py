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
    ColorbarTickLabels,
    ColorbarTicks,
    ColorbarTitle,
    ColorEncoding,
    ColumnSpec,
    FontSpec,
    PlotData,
    PlotPresentation,
    PlotState,
)

__all__ = [
    "AxisPresentation",
    "AxisScale",
    "AxisSpine",
    "AxisTickLabels",
    "AxisTickMarks",
    "AxisTicks",
    "AxisTitle",
    "ColorbarTickLabels",
    "ColorbarTicks",
    "ColorbarTitle",
    "ColorEncoding",
    "ColumnSpec",
    "FontSpec",
    "PlotData",
    "PlotPresentation",
    "PlotState",
    "ParallelPlot",
    "hydroclimate_model_evaluation",
    "tradeoff",
]
