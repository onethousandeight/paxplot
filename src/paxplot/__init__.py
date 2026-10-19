"""PaxPlot public API."""

from paxplot.datasets import hydroclimate_model_evaluation, tradeoff
from paxplot.plot import ParallelPlot
from paxplot.state import (
    AxisConfig,
    AxisSpineStyle,
    ColorbarConfig,
    ColorEncoding,
    LineStyle,
    LineStyleOverride,
    PlotState,
    TextStyle,
    TickConfig,
    TickMarkStyle,
)

__all__ = [
    "AxisConfig",
    "AxisSpineStyle",
    "ColorbarConfig",
    "ColorEncoding",
    "LineStyle",
    "LineStyleOverride",
    "ParallelPlot",
    "PlotState",
    "TextStyle",
    "TickConfig",
    "TickMarkStyle",
    "hydroclimate_model_evaluation",
    "tradeoff",
]
