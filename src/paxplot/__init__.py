"""PaxPlot public API."""

from paxplot.datasets import hydroclimate_model_evaluation, tradeoff
from paxplot.plot import ParallelPlot
from paxplot.state import (
    AxisConfig,
    ColorbarConfig,
    ColorEncoding,
    LineStyle,
    LineStyleOverride,
    PlotState,
    TickConfig,
)

__all__ = [
    "AxisConfig",
    "ColorbarConfig",
    "ColorEncoding",
    "LineStyle",
    "LineStyleOverride",
    "ParallelPlot",
    "PlotState",
    "TickConfig",
    "hydroclimate_model_evaluation",
    "tradeoff",
]
