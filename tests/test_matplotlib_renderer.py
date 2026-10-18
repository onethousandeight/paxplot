from __future__ import annotations

from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

import paxplot as pax


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
