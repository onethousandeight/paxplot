from __future__ import annotations

import numpy as np
import pytest
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

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
            0, label="Configured axis", ticks=values, tick_labels=["Bottom", "Top"]
        )
        .set_axis(1, ticks=[])
        .set_axis(0, **visibility)
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
        .set_axis(1, categories=["low", "high"])
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
        .set_colorbar(1, label="B scale")
    )

    fig = plot.render()

    assert len(fig.axes) == 2
    assert fig.axes[1].get_ylabel() == "B scale"
