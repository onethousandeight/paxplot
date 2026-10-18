from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from matplotlib import pyplot as plt

import paxplot as pax
from paxplot.rendering import prepare_render_data


def summarize(plot: pax.ParallelPlot) -> dict[str, object]:
    render_data = prepare_render_data(plot.state)
    return {
        "state": plot.state.model_dump(mode="json"),
        "render": {
            "x": render_data.x.tolist(),
            "y": np.nan_to_num(render_data.y, nan=-999.0).round(4).tolist(),
            "axes": [
                {
                    "label": axis.label,
                    "ticks": list(
                        zip(axis.tick_positions, axis.tick_labels, strict=True)
                    ),
                }
                for axis in render_data.axes
            ],
            "colorbar": None
            if render_data.colorbar is None
            else {
                "axis": render_data.colorbar.axis,
                "label": render_data.colorbar.label,
                "lower": render_data.colorbar.lower,
                "upper": render_data.colorbar.upper,
            },
            "colors": render_data.line_colors.round(4).tolist(),
            "alphas": render_data.line_alphas.tolist(),
            "zorders": [
                None if np.isnan(value) else float(value)
                for value in render_data.line_zorders
            ],
            "widths": render_data.line_widths.tolist(),
            "linestyles": render_data.line_linestyles.tolist(),
        },
    }


@dataclass
class WorkflowResult:
    plot: pax.ParallelPlot
    png_path: Path
    json_path: Path
    summary: dict[str, object]


def run_workflow(
    plot: pax.ParallelPlot, output_prefix: Path, figsize: tuple[float, float]
) -> WorkflowResult:
    png_path = output_prefix.with_suffix(".png")
    json_path = output_prefix.with_suffix(".json")

    fig = plot.render(figsize=figsize)
    try:
        fig.savefig(png_path)
    finally:
        plt.close(fig)

    plot.to_json(json_path)
    summary = summarize(plot)

    return WorkflowResult(plot, png_path, json_path, summary)


def assert_workflow_results(
    original: WorkflowResult, restored: WorkflowResult, snapshot
) -> None:
    assert original.summary == snapshot
    assert restored.plot.state == original.plot.state
    assert restored.summary == original.summary

    for result in (original, restored):
        for path in (result.png_path, result.json_path):
            assert path.is_file()
            assert path.stat().st_size > 0

    assert json.loads(original.json_path.read_text(encoding="utf-8")) == json.loads(
        restored.json_path.read_text(encoding="utf-8")
    )


def assert_snapshot_and_roundtrip(
    plot: pax.ParallelPlot, tmp_path: Path, snapshot
) -> None:
    figsize = (max(6.0, 1.5 * len(plot.state.axes)), 4.0)
    original = run_workflow(plot, tmp_path / "plot", figsize)

    restored_plot = pax.ParallelPlot.from_json(original.json_path)
    restored = run_workflow(restored_plot, tmp_path / "restored", figsize)

    assert_workflow_results(original, restored, snapshot)


@pytest.mark.integration
def test_standard_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    numeric = [0.0, 1.0, 4.0]
    categorical = ["medium", "low", "high"]
    # Columns are defined separately so each feature has a visible baseline.
    columns = [
        numeric,  # 1: numeric defaults; no axis configuration
        numeric,  # 2: axis label only
        numeric,  # 3: custom limits only
        numeric,  # 4: custom tick values
        numeric,  # 5: same tick values with custom labels
        numeric,  # 6: automatic tick count
        numeric,  # 7: inversion only
        categorical,  # 8: categorical defaults, in first-appearance order
        categorical,  # 9: explicit category order
        categorical,  # 10: selected categorical ticks
        categorical,  # 11: same selected ticks with custom labels
        [0.0, None, 4.0],  # 12: missing numeric value
        ["medium", None, "high"],  # 13: missing categorical value
    ]
    plot = (
        pax.ParallelPlot()
        .set_data(list(zip(*columns, strict=True)))
        .set_axis_label(1, "Label only")
        .set_axis_limits(2, lower=-2.0, upper=6.0)
        .set_axis_ticks(3, values=[0.0, 1.0, 4.0])
        .set_axis_ticks(
            4, values=[0.0, 1.0, 4.0], labels=["Minimum", "Target", "Maximum"]
        )
        .set_axis(5, tick_count=3)
        .invert_axis(6)
        .set_axis(8, categories=["low", "medium", "high"])
        .set_axis_ticks(9, values=["medium", "high"])
        .set_axis_ticks(10, values=["medium", "high"], labels=["Medium", "High"])
    )

    assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)


@pytest.mark.integration
def test_colorbar_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [1.0], [2.0]])
        .set_axis_label(0, "A")
        .set_default_line_style(color="black", width=1.25, linestyle="--")
        .set_colorbar(0, palette="viridis", label="A scale")
        .set_line_style(2, color="crimson", width=2.5, linestyle="-")
    )

    assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)


@pytest.mark.integration
def test_line_style_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[value, 5.0 - value] for value in range(6)])
        .set_default_line_style(color="steelblue", alpha=0.6, width=1.2, linestyle="--")
        # Row 0 inherits every default; each other row overrides one property.
        .set_line_style(1, color="crimson")
        .set_line_style(2, width=2.5)
        .set_line_style(3, alpha=0.25)
        .set_line_style(4, linestyle=":")
        .set_line_style(5, zorder=10.0)
    )

    assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)


@pytest.mark.integration
def test_axis_interaction_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, 0.0], [1.0, 1.0], [4.0, 4.0]])
        .set_axis(
            1,
            limits=(-2.0, 6.0),
            ticks=[-2.0, 1.0, 6.0],
            tick_labels=["Minimum", "Target", "Maximum"],
        )
        .invert_axis(1)
    )

    assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)
