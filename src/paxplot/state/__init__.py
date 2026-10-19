"""Serializable plot state schemas."""

from paxplot.state.schema import (
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
from paxplot.state.serialization import load_state, save_state

__all__ = [
    "AxisConfig",
    "AxisSpineStyle",
    "ColorbarConfig",
    "ColorEncoding",
    "LineStyle",
    "LineStyleOverride",
    "PlotState",
    "TextStyle",
    "TickConfig",
    "TickMarkStyle",
    "load_state",
    "save_state",
]
