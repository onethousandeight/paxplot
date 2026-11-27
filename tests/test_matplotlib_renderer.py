from __future__ import annotations

import numpy as np
import pytest
from matplotlib import pyplot as plt
from matplotlib import rc_context, rcParams
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

import paxplot as pax


@pytest.mark.parametrize("values", [[0.0, 1.0], ["low", "high"]])
@pytest.mark.parametrize(
    "visibility",
    [
        {},
        {"spine_visible": False},
        {"label_visible": False},
        {"tick_marks_visible": False},
        {"tick_labels_visible": False},
        {"tick_marks_visible": False, "tick_labels_visible": False},
        {
            "spine_visible": False,
            "label_visible": False,
            "tick_marks_visible": False,
            "tick_labels_visible": False,
        },
    ],
    ids=[
        "default",
        "no-spine",
        "no-title",
        "no-marks",
        "no-values",
        "no-ticks",
        "none",
    ],
)
def test_axis_elements_are_independent_and_preserve_data(values, visibility) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[value, value] for value in values])
        .set_axis(
            0,
            title=pax.AxisTitle(text="Configured axis"),
            ticks=pax.AxisTicks(
                values=values, labels=pax.AxisTickLabels(text=["Bottom", "Top"])
            ),
        )
        .set_axis(1, ticks=pax.AxisTicks(values=[]))
        .set_axis(
            0,
            title=pax.AxisTitle(
                text="Configured axis", visible=visibility.get("label_visible", True)
            ),
            spine=pax.AxisSpine(visible=visibility.get("spine_visible", True)),
            ticks=pax.AxisTicks(
                values=values,
                marks=pax.AxisTickMarks(
                    visible=visibility.get("tick_marks_visible", True)
                ),
                labels=pax.AxisTickLabels(
                    text=["Bottom", "Top"],
                    visible=visibility.get("tick_labels_visible", True),
                ),
            ),
        )
    )

    fig = plot.render()
    try:
        ax = fig.axes[0]
        # Renderer layers contain data, axis spines, and tick marks respectively.
        data = [item for item in ax.collections if item.get_zorder() == 2]
        spines = [item for item in ax.collections if item.get_zorder() == 3]
        marks = [item for item in ax.collections if item.get_zorder() == 4]
        assert len(data) == 1
        np.testing.assert_array_equal(
            data[0].get_segments(), [[[0.0, 0.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 1.0]]]
        )
        assert len(spines) == 1 + int(visibility.get("spine_visible", True))
        assert len(marks) == 2 * int(visibility.get("tick_marks_visible", True))
        texts = {text.get_text() for text in ax.texts}
        assert ("Configured axis" in texts) == visibility.get("label_visible", True)
        assert ("Bottom" in texts) == visibility.get("tick_labels_visible", True)
        assert ("Top" in texts) == visibility.get("tick_labels_visible", True)
        assert "Axis 2" in texts
        assert ax.get_xlim() == pytest.approx((-0.2, 1.2))
    finally:
        plt.close(fig)


def test_render_returns_figure_with_line_collection_and_axis_text() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, "low"], [1.0, "high"]])
        .set_axis_label(0, "Column A")
        .set_axis(1, scale=pax.AxisScale(categories=["low", "high"]))
        .set_default_line_style(width=2.0)
    )

    fig = plot.render(figsize=(4, 3))
    ax = fig.axes[0]

    assert isinstance(fig, Figure)
    assert any(isinstance(collection, LineCollection) for collection in ax.collections)
    assert "Column A" in [text.get_text() for text in ax.texts]
    assert {"low", "high"}.issubset({text.get_text() for text in ax.texts})


def test_render_adds_colorbar_with_label() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, 10.0], [1.0, 20.0]])
        .set_colorbar(1, title=pax.ColorbarTitle(text="B scale"))
    )

    fig = plot.render()

    assert len(fig.axes) == 2
    assert fig.axes[1].get_ylabel() == "B scale"


def test_colorbar_title_visibility_preserves_text_and_encoding(tmp_path) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0], [1]])
        .set_colorbar(0, title=pax.ColorbarTitle(text="Retained"))
    )
    state = plot.state.model_dump()
    state["presentation"]["lines"]["color_encoding"]["colorbar"]["title"]["visible"] = (
        False
    )
    hidden = pax.ParallelPlot(pax.PlotState.model_validate(state))
    path = tmp_path / "colorbar.json"
    hidden.to_json(path)
    hidden = pax.ParallelPlot.from_json(path)
    fig = hidden.render()
    try:
        assert len(fig.axes) == 2
        assert fig.axes[1].get_ylabel() == ""
        title = hidden.state.presentation.lines.color_encoding.colorbar.title
        assert title.text == "Retained" and not title.visible
    finally:
        plt.close(fig)


@pytest.mark.parametrize("values", [[0, 1], ["Low", "High"]])
def test_axis_fonts_apply_independently_to_titles_and_tick_labels(values) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[value] for value in values])
        .set_axis(
            0,
            title=pax.AxisTitle(
                text="Heading",
                font=pax.FontSpec(
                    family=["DejaVu Serif", "serif"],
                    size=15,
                    weight="bold",
                    style="italic",
                ),
            ),
            ticks=pax.AxisTicks(
                labels=pax.AxisTickLabels(
                    font=pax.FontSpec(
                        family="DejaVu Sans Mono",
                        size=9,
                        weight="semibold",
                        style="oblique",
                    ),
                )
            ),
        )
    )
    fig = plot.render()
    try:
        fig.canvas.draw()
        title, *labels = fig.axes[0].texts
        assert title.get_family() == ["DejaVu Serif", "serif"]
        assert title.get_fontsize() == 15
        assert title.get_fontweight() == "bold"
        assert title.get_fontstyle() == "italic"
        assert labels
        for label in labels:
            assert label.get_family() == ["DejaVu Sans Mono"]
            assert label.get_fontsize() == 9
            assert label.get_fontweight() == "semibold"
            assert label.get_fontstyle() == "oblique"
    finally:
        plt.close(fig)


@pytest.mark.parametrize("visible", [True, False])
def test_colorbar_fonts_and_label_visibility_include_offset_and_minor_ticks(
    visible,
) -> None:
    with rc_context({"ytick.minor.visible": True}):
        plot = (
            pax.ParallelPlot()
            .set_data([[1_000_000], [1_000_002]])
            .set_colorbar(
                0,
                title=pax.ColorbarTitle(
                    text="Scale",
                    font=pax.FontSpec(family="DejaVu Serif", size=15, weight="bold"),
                ),
                ticks=pax.ColorbarTicks(
                    labels=pax.ColorbarTickLabels(
                        visible=visible,
                        font=pax.FontSpec(
                            family="DejaVu Sans Mono", size=9, style="italic"
                        ),
                    )
                ),
            )
        )
        fig = plot.render()
        try:
            fig.canvas.draw()
            axis = fig.axes[1].yaxis
            assert axis.label.get_family() == ["DejaVu Serif"]
            assert axis.label.get_fontsize() == 15
            assert axis.label.get_fontweight() == "bold"
            assert axis.get_minor_ticks()
            offset = axis.get_offset_text()
            assert offset.get_text()
            assert offset.get_visible() == visible
            for tick in (*axis.get_major_ticks(), *axis.get_minor_ticks()):
                assert tick.tick2line.get_visible()
                assert tick.label2.get_visible() == visible
                for label in (tick.label1, tick.label2):
                    assert label.get_family() == ["DejaVu Sans Mono"]
                    assert label.get_fontsize() == 9
                    assert label.get_fontstyle() == "italic"
            assert offset.get_family() == ["DejaVu Sans Mono"]
            assert offset.get_fontsize() == 9
            assert offset.get_fontstyle() == "italic"
            # A second draw at a different size can create more automatic ticks.
            fig.set_size_inches(8, 7)
            fig.canvas.draw()
            for tick in axis.get_major_ticks():
                assert tick.label2.get_fontsize() == 9
                assert tick.label2.get_fontstyle() == "italic"
                assert tick.label2.get_visible() == visible
        finally:
            plt.close(fig)


def test_partial_fonts_preserve_role_defaults_and_do_not_modify_rcparams() -> None:
    settings = {
        "font.family": ["DejaVu Serif"],
        "font.size": 17,
        "font.weight": "light",
        "font.style": "oblique",
        "axes.labelsize": 19,
        "axes.labelweight": "semibold",
        "ytick.labelsize": 9,
    }
    with rc_context(settings):
        original = {key: rcParams[key] for key in settings}
        plot = (
            pax.ParallelPlot()
            .set_data([[0], [1]])
            .set_axis(
                0,
                title=pax.AxisTitle(font=pax.FontSpec(weight="bold")),
                ticks=pax.AxisTicks(
                    labels=pax.AxisTickLabels(
                        font=pax.FontSpec(weight="bold"),
                    )
                ),
            )
            .set_colorbar(
                0,
                title=pax.ColorbarTitle(
                    text="Scale", font=pax.FontSpec(style="italic")
                ),
                ticks=pax.ColorbarTicks(
                    labels=pax.ColorbarTickLabels(
                        font=pax.FontSpec(weight="bold"),
                    )
                ),
            )
        )
        fig = plot.render()
        try:
            fig.canvas.draw()
            title, *labels = fig.axes[0].texts
            assert (
                title.get_fontsize()
                == FontProperties(size="medium").get_size_in_points()
            )
            for label in labels:
                assert (
                    label.get_fontsize()
                    == FontProperties(size="small").get_size_in_points()
                )
            for label in (title, *labels):
                assert label.get_family() == ["DejaVu Serif"]
                assert label.get_fontstyle() == "oblique"
                assert label.get_fontweight() == "bold"
            axis = fig.axes[1].yaxis
            assert axis.label.get_fontsize() == 19
            assert axis.label.get_fontweight() == "semibold"
            assert axis.label.get_fontstyle() == "italic"
            for label in axis.get_ticklabels():
                assert label.get_fontsize() == 9
                assert label.get_fontstyle() == "oblique"
                assert label.get_fontweight() == "bold"
            assert {key: rcParams[key] for key in settings} == original
        finally:
            plt.close(fig)


def test_last_axis_ticks_and_labels_face_outward() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, 0.0], [1.0, 1.0]])
        .set_axis(0, ticks=pax.AxisTicks(values=[0.0, 1.0]))
        .set_axis(1, ticks=pax.AxisTicks(values=[0.0, 1.0]))
    )
    fig = plot.render()
    try:
        ax = fig.axes[0]
        segments = [
            segment
            for item in ax.collections
            if item.get_zorder() == 4
            for segment in item.get_segments()
        ]

        # Interior axes point left; the last axis points right.
        left_marks = [
            segment for segment in segments if np.isclose(segment[:, 0].max(), 0.0)
        ]
        right_marks = [
            segment for segment in segments if np.isclose(segment[:, 0].min(), 1.0)
        ]
        assert left_marks and right_marks
        for segment in left_marks:
            assert segment[0, 0] < 0.0
            assert segment[1, 0] == pytest.approx(0.0)
        for segment in right_marks:
            assert segment[0, 0] == pytest.approx(1.0)
            assert segment[1, 0] > 1.0

        fig.canvas.draw()
        for segment in segments:
            start = ax.transData.transform(segment[0])
            end = ax.transData.transform(segment[1])
            length_points = np.hypot(*(end - start)) * 72.0 / fig.dpi
            assert length_points == pytest.approx(3.5)

        spine = next(item for item in ax.collections if item.get_zorder() == 3)
        mark = next(item for item in ax.collections if item.get_zorder() == 4)
        np.testing.assert_allclose(mark.get_colors(), spine.get_colors())
        assert mark.get_linewidths()[0] == pytest.approx(spine.get_linewidths()[0])
        assert spine.get_capstyle() == "projecting"
        assert mark.get_capstyle() == "butt"

        for text in ax.texts:
            x, _ = text.get_position()
            if x < 0:
                assert text.get_ha() == "right"
            elif x > 1:
                assert text.get_ha() == "left"
    finally:
        plt.close(fig)


@pytest.mark.parametrize(
    "figsize",
    [(6.4, 4.8), (5.0, 5.0), (8.0, 4.0), (10.0, 4.0), (4.0, 6.0), (4.0, 8.0)],
)
def test_tick_geometry_is_physical_across_figure_sizes(figsize) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, 0.0], [1.0, 1.0]])
        .set_axis(0, ticks=pax.AxisTicks(values=[0.0, 1.0]))
        .set_axis(1, ticks=pax.AxisTicks(values=[0.0, 1.0]))
        .set_colorbar(0, title=pax.ColorbarTitle(text="A"))
    )
    fig = plot.render(figsize=figsize)
    try:
        fig.canvas.draw()
        ax = fig.axes[0]
        marks = [item for item in ax.collections if item.get_zorder() == 4]
        assert marks
        for item in marks:
            for segment in item.get_segments():
                start = ax.transData.transform(segment[0])
                end = ax.transData.transform(segment[1])
                length_points = np.hypot(*(end - start)) * 72.0 / fig.dpi
                assert length_points == pytest.approx(3.5)

        # Labels sit one tick length plus a 3.5 pt pad from the axis.
        for text in ax.texts:
            if text.get_ha() not in {"left", "right"}:
                continue
            x, y = text.get_position()
            axis_x = 1.0 if text.get_ha() == "left" else 0.0
            anchor = ax.transData.transform((axis_x, y))
            label = ax.transData.transform((x, y))
            offset_points = abs(label[0] - anchor[0]) * 72.0 / fig.dpi
            assert offset_points == pytest.approx(7.0)
    finally:
        plt.close(fig)


def test_last_axis_labels_do_not_overlap_colorbar() -> None:
    labels = ["a very long tick label", "another very long tick label"]
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, 0.0], [1.0, 1.0]])
        .set_axis(
            1,
            ticks=pax.AxisTicks(
                values=[0.0, 1.0],
                labels=pax.AxisTickLabels(text=labels),
            ),
        )
        .set_colorbar(0, title=pax.ColorbarTitle(text="A"))
    )
    fig = plot.render()
    try:
        fig.canvas.draw()
        ax, colorbar_axis = fig.axes
        right_labels = [
            text
            for text in ax.texts
            if text.get_position()[0] > 1 and text.get_text() in labels
        ]
        assert len(right_labels) == 2
        for label in right_labels:
            assert label.get_ha() == "left"
            assert label.get_window_extent().x1 < colorbar_axis.bbox.x0
    finally:
        plt.close(fig)
