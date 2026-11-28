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
        .set_axis(0, scale=pax.AxisScale(categories=["low", "medium", "high"]))
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


@pytest.mark.parametrize("values", [[0.0, 4.0], ["low", "high"]])
def test_empty_tick_values_configure_zero_ticks(values) -> None:
    plot = pax.ParallelPlot().set_data([[value] for value in values])
    baseline = prepare_render_data(plot.state)
    plot.set_axis_ticks(0, values=[])

    prepared = prepare_render_data(plot.state)

    assert prepared.axes[0].tick_positions == []
    assert prepared.axes[0].tick_labels == []
    assert prepared.axes[0].tick_marks_visible
    assert prepared.axes[0].tick_labels_visible
    np.testing.assert_array_equal(prepared.y, baseline.y)


@pytest.mark.parametrize("values", [[0.0, 4.0, None], ["low", "high", None]])
def test_hidden_decorations_preserve_geometry_and_tick_configuration(values) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[value, value] for value in values])
        .set_axis(
            0,
            scale=pax.AxisScale(inverted=True),
            ticks=pax.AxisTicks(
                values=values[:2], labels=pax.AxisTickLabels(text=["Bottom", "Top"])
            ),
        )
    )
    if isinstance(values[0], float):
        plot.set_axis_limits(0, lower=-2.0, upper=6.0)
        plot.set_colorbar(0, title=pax.ColorbarTitle(text="Hidden axis scale"))
    else:
        plot.set_axis(0, scale=pax.AxisScale(categories=["high", "low"], inverted=True))
    baseline = prepare_render_data(plot.state)

    plot.set_axis(
        0,
        title=pax.AxisTitle(visible=False),
        ticks=pax.AxisTicks(
            values=values[:2],
            marks=pax.AxisTickMarks(visible=False),
            labels=pax.AxisTickLabels(text=["Bottom", "Top"], visible=False),
        ),
        spine=pax.AxisSpine(visible=False),
    )
    prepared = prepare_render_data(plot.state)

    np.testing.assert_array_equal(prepared.x, baseline.x)
    np.testing.assert_array_equal(prepared.y, baseline.y)
    np.testing.assert_array_equal(prepared.line_colors, baseline.line_colors)
    assert prepared.colorbar == baseline.colorbar
    assert len(prepared.axes) == 2
    assert prepared.axes[0].tick_positions == baseline.axes[0].tick_positions
    assert prepared.axes[0].tick_labels == ["Bottom", "Top"]
    assert not prepared.axes[0].spine_visible
    assert not prepared.axes[0].label_visible
    assert not prepared.axes[0].tick_marks_visible
    assert not prepared.axes[0].tick_labels_visible
    assert prepared.axes[1] == baseline.axes[1]


def test_hiding_tick_labels_does_not_bypass_validation() -> None:
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]])
    plot.set_axis(
        0,
        ticks=pax.AxisTicks(
            marks=pax.AxisTickMarks(visible=False),
            labels=pax.AxisTickLabels(visible=False),
        ),
    )

    with pytest.raises(ValueError, match="same length"):
        plot.set_axis_ticks(0, values=[0.0, 1.0], labels=["Only one"])


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


def test_tick_labels_without_values_apply_to_automatic_ticks() -> None:
    numeric = (
        pax.ParallelPlot()
        .set_data([[0], [10]])
        .set_axis(
            0,
            ticks=pax.AxisTicks(
                labels=pax.AxisTickLabels(text=["zero", "a", "b", "c", "ten"])
            ),
        )
    )
    categorical = (
        pax.ParallelPlot()
        .set_data([["low"], ["high"]])
        .set_axis(
            0,
            ticks=pax.AxisTicks(labels=pax.AxisTickLabels(text=["Low", "High"])),
        )
    )

    assert prepare_render_data(numeric.state).axes[0].tick_labels == [
        "zero",
        "a",
        "b",
        "c",
        "ten",
    ]
    assert prepare_render_data(categorical.state).axes[0].tick_labels == [
        "Low",
        "High",
    ]


def test_tick_label_count_mismatch_fails_during_preparation() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([["low"], ["high"]])
        .set_axis(
            0,
            ticks=pax.AxisTicks(labels=pax.AxisTickLabels(text=["only one"])),
        )
    )

    with pytest.raises(ValueError, match="tick labels must match"):
        prepare_render_data(plot.state)


@pytest.mark.parametrize(
    "edit",
    [
        lambda plot: plot.set_data([[0.0], [float("inf")]]),
        lambda plot: plot.set_axis_limits(0, lower=float("inf")),
        lambda plot: plot.set_default_line_style(width=float("inf")),
        lambda plot: plot.set_colorbar(0, limits=(0.0, float("inf"))),
    ],
)
def test_non_finite_values_fail_during_preparation(edit) -> None:
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]])
    edit(plot)

    with pytest.raises(ValueError, match="finite"):
        prepare_render_data(plot.state)


def test_single_sided_limits_that_invert_data_fail_during_preparation() -> None:
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]]).set_axis_limits(0, lower=10)

    with pytest.raises(ValueError, match="lower limit cannot be greater"):
        prepare_render_data(plot.state)


def test_empty_axis_title_is_preserved() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [1.0]])
        .set_axis(0, title=pax.AxisTitle(text=""))
    )

    assert prepare_render_data(plot.state).axes[0].label == ""


def test_colorbar_requires_numeric_axis() -> None:
    plot = pax.ParallelPlot().set_data([["low"], ["high"]])

    with pytest.raises(ValueError, match="numeric axes"):
        plot.set_colorbar(0)


@pytest.mark.parametrize("values", [[0, 0], [None, None], ["only", "only"]])
def test_constant_and_missing_columns_have_usable_positions(values) -> None:
    plot = pax.ParallelPlot().set_data([[value] for value in values])
    prepared = prepare_render_data(plot.state)
    if values[0] is None:
        assert np.isnan(prepared.y).all()
        assert prepared.axes[0].tick_positions == [0, 0.25, 0.5, 0.75, 1]
    else:
        assert prepared.y[:, 0].tolist() == [0.5, 0.5]


def test_color_mapping_preserves_missing_fallback_and_explicit_bounds() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0], [None], [10]])
        .set_default_line_style(color="black", alpha=0.5)
        .set_colorbar(0, palette=["blue", "red"], limits=(0, 5))
    )
    prepared = prepare_render_data(plot.state)
    assert prepared.colorbar.lower == 0 and prepared.colorbar.upper == 5
    np.testing.assert_allclose(
        prepared.line_colors, [[0, 0, 1, 0.5], [0, 0, 0, 0.5], [1, 0, 0, 0.5]]
    )


def test_tick_count_and_explicit_values_precedence() -> None:
    plot = pax.ParallelPlot().set_data([[0], [10]])
    plot.set_axis(0, ticks=pax.AxisTicks(count=3))
    assert prepare_render_data(plot.state).axes[0].tick_positions == [0, 0.5, 1]
    plot.set_axis_ticks(0, [0, 10])
    assert plot.state.presentation.axes[0].ticks.count == 3
    assert prepare_render_data(plot.state).axes[0].tick_positions == [0, 1]
    with pytest.raises(ValueError):
        plot.set_axis(0, ticks=pax.AxisTicks(count=1))
