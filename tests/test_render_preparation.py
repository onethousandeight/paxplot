from __future__ import annotations

import math

import numpy as np
import pytest

import paxplot as pax
from paxplot.rendering import prepare_render_data


def test_numeric_normalization_limits_inversion_and_missing_values() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [1.0], [None]])
        .set_axis_limits(0, lower=-1.0, upper=3.0)
        .invert_axis(0)
    )

    render_data = prepare_render_data(plot.state)

    assert render_data.y[0, 0] == pytest.approx(0.75)
    assert render_data.y[1, 0] == pytest.approx(0.5)
    assert math.isnan(render_data.y[2, 0])


def test_categorical_mapping_and_ticks() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([["medium"], ["low"], ["high"]])
        .set_axis(0, categories=["low", "medium", "high"])
    )

    render_data = prepare_render_data(plot.state)

    assert render_data.y[:, 0].tolist() == [0.5, 0.0, 1.0]
    assert render_data.axes[0].tick_positions == [0.0, 0.5, 1.0]
    assert render_data.axes[0].tick_labels == ["low", "medium", "high"]


def test_explicit_numeric_ticks_are_scaled() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [10.0]])
        .set_axis_ticks(0, values=[0.0, 5.0, 10.0], labels=["zero", "five", "ten"])
    )

    render_data = prepare_render_data(plot.state)

    assert render_data.axes[0].tick_positions == [0.0, 0.5, 1.0]
    assert render_data.axes[0].tick_labels == ["zero", "five", "ten"]


def test_line_style_precedence_with_colorbar_and_override() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [1.0], [2.0]])
        .set_default_line_style(color="black", alpha=0.4, width=1.5)
        .set_colorbar(0, palette=["blue", "red"])
        .set_line_style(1, color="crimson", width=3.0, zorder=10)
    )

    render_data = prepare_render_data(plot.state)

    assert render_data.colorbar is not None
    assert render_data.colorbar.lower == 0.0
    assert render_data.colorbar.upper == 2.0
    assert render_data.line_widths.tolist() == [1.5, 3.0, 1.5]
    assert render_data.line_zorders.tolist()[1] == 10.0
    assert np.allclose(render_data.line_colors[1], [0.862745, 0.078431, 0.235294, 0.4])


def test_colorbar_requires_numeric_axis() -> None:
    plot = pax.ParallelPlot().set_data([["low"], ["high"]])

    with pytest.raises(ValueError, match="numeric axes"):
        plot.set_colorbar(0)
