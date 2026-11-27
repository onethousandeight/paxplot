from __future__ import annotations

import json
import time
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
                    "spine_visible": axis.spine_visible,
                    "label_visible": axis.label_visible,
                    "tick_marks_visible": axis.tick_marks_visible,
                    "tick_labels_visible": axis.tick_labels_visible,
                    "title_font": axis.title_font.model_dump(mode="json"),
                    "tick_labels_font": axis.tick_labels_font.model_dump(mode="json"),
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
                "title_visible": render_data.colorbar.title_visible,
                "title_font": render_data.colorbar.title_font.model_dump(mode="json"),
                "tick_labels_font": render_data.colorbar.tick_labels_font.model_dump(
                    mode="json"
                ),
                "tick_labels_visible": render_data.colorbar.tick_labels_visible,
            },
            "colors": render_data.line_colors.round(4).tolist(),
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
    figsize = (max(6.0, 2.0 * len(plot.state.presentation.axes)), 4.0)
    original = run_workflow(plot, tmp_path / "plot", figsize)

    restored_plot = pax.ParallelPlot.from_json(original.json_path)
    restored = run_workflow(restored_plot, tmp_path / "restored", figsize)

    assert_workflow_results(original, restored, snapshot)


@pytest.mark.integration
def test_standard_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    numeric = [0.0, 1.0, 4.0]
    categorical = ["medium", "low", "high"]
    shared_font = pax.FontSpec(weight="bold")
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
        numeric,  # 14: hide only the numeric axis spine
        categorical,  # 15: hide only the categorical axis spine
        numeric,  # 16: hide only the axis title
        numeric,  # 17: tick value labels without tick marks
        categorical,  # 18: tick marks without tick value labels
        numeric,  # 19: hide both tick marks and value labels
        categorical,  # 20: hide all decorations; keep the data dimension
        numeric,  # 21: explicitly configure zero numeric ticks
        categorical,  # 22: explicitly configure zero categorical ticks
        numeric,  # 23: title family, size, weight, and style
        numeric,  # 24: custom numeric tick-label fonts
        categorical,  # 25: custom categorical tick-label fonts
        numeric,  # 26: shared weight override; retain role-specific sizes
        numeric,  # 27: Mathtext title and numeric tick labels
        categorical,  # 28: grouped word subscripts and categorical tick labels
        numeric,  # 29: literal underscore for comparison with Mathtext
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
        .set_axis(5, ticks=pax.AxisTicks(count=3))
        .invert_axis(6)
        .set_axis(8, scale=pax.AxisScale(categories=["low", "medium", "high"]))
        .set_axis_ticks(9, values=["medium", "high"])
        .set_axis_ticks(10, values=["medium", "high"], labels=["Medium", "High"])
        .set_axis(
            13,
            title=pax.AxisTitle(text="No numeric spine"),
            spine=pax.AxisSpine(visible=False),
        )
        .set_axis(
            14,
            title=pax.AxisTitle(text="No category spine"),
            spine=pax.AxisSpine(visible=False),
        )
        .set_axis(15, title=pax.AxisTitle(text="Hidden title", visible=False))
        .set_axis(
            16,
            title=pax.AxisTitle(text="Values only"),
            ticks=pax.AxisTicks(marks=pax.AxisTickMarks(visible=False)),
        )
        .set_axis(
            17,
            title=pax.AxisTitle(text="Marks only"),
            ticks=pax.AxisTicks(labels=pax.AxisTickLabels(visible=False)),
        )
        .set_axis(
            18,
            title=pax.AxisTitle(text="No ticks"),
            ticks=pax.AxisTicks(
                marks=pax.AxisTickMarks(visible=False),
                labels=pax.AxisTickLabels(visible=False),
            ),
        )
        .set_axis(
            19,
            title=pax.AxisTitle(visible=False),
            ticks=pax.AxisTicks(
                marks=pax.AxisTickMarks(visible=False),
                labels=pax.AxisTickLabels(visible=False),
            ),
            spine=pax.AxisSpine(visible=False),
        )
        .set_axis(
            20,
            title=pax.AxisTitle(text="Zero numeric ticks"),
            ticks=pax.AxisTicks(values=[]),
        )
        .set_axis(
            21,
            title=pax.AxisTitle(text="Zero category ticks"),
            ticks=pax.AxisTicks(values=[]),
        )
        .set_axis(
            22,
            title=pax.AxisTitle(
                text="Styled title",
                font=pax.FontSpec(
                    family=["DejaVu Serif", "serif"],
                    size=13,
                    weight="bold",
                    style="italic",
                ),
            ),
        )
        .set_axis(
            23,
            title=pax.AxisTitle(text="Numeric font"),
            ticks=pax.AxisTicks(
                labels=pax.AxisTickLabels(
                    font=pax.FontSpec(
                        family="DejaVu Sans Mono", size=9, weight="semibold"
                    ),
                )
            ),
        )
        .set_axis(
            24,
            title=pax.AxisTitle(text="Category font"),
            ticks=pax.AxisTicks(
                labels=pax.AxisTickLabels(
                    font=pax.FontSpec(family="DejaVu Serif", size=10, style="italic"),
                )
            ),
        )
        .set_axis(
            25,
            title=pax.AxisTitle(text="Shared weight", font=shared_font),
            ticks=pax.AxisTicks(labels=pax.AxisTickLabels(font=shared_font)),
        )
        .set_axis_label(26, r"$x_1$")
        .set_axis_ticks(26, values=[0.0, 1.0, 4.0], labels=[r"$0$", r"$1$", r"$2^2$"])
        .set_axis_label(27, r"$y_{\mathrm{test}}$")
        .set_axis_ticks(
            27,
            values=["medium", "low", "high"],
            labels=[
                r"$y_{\mathrm{medium}}$",
                r"$y_{\mathrm{low}}$",
                r"$y_{\mathrm{high}}$",
            ],
        )
        .set_axis_label(28, "x_1")
        .set_colorbar(
            22,
            palette="plasma",
            title=pax.ColorbarTitle(
                text=r"$x_1$",
                font=pax.FontSpec(family="DejaVu Serif", size=13, weight="bold"),
            ),
            ticks=pax.ColorbarTicks(
                labels=pax.ColorbarTickLabels(
                    font=pax.FontSpec(
                        family="DejaVu Sans Mono", size=9, style="italic"
                    ),
                )
            ),
        )
    )

    # Dollar-delimited expressions use built-in Mathtext, without external LaTeX.
    with plt.rc_context({"text.usetex": False}):
        assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)


@pytest.mark.integration
def test_colorbar_workflow_snapshot_and_roundtrip(tmp_path, snapshot) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0], [1.0], [2.0]])
        .set_axis_label(0, "A")
        .set_default_line_style(color="black", width=1.25, linestyle="--")
        .set_colorbar(0, palette="viridis", title=pax.ColorbarTitle(text="A scale"))
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
            scale=pax.AxisScale(limits=(-2.0, 6.0)),
            ticks=pax.AxisTicks(
                values=[-2.0, 1.0, 6.0],
                labels=pax.AxisTickLabels(text=["Minimum", "Target", "Maximum"]),
            ),
        )
        .invert_axis(1)
    )

    assert_snapshot_and_roundtrip(plot, tmp_path, snapshot)


@pytest.mark.integration
def test_large_dataset_workflow_performance(tmp_path, record_property) -> None:
    rows = np.random.default_rng(0).normal(size=(10_000, 10)).tolist()
    png_path = tmp_path / "large.png"
    json_path = tmp_path / "large.json"

    start = time.perf_counter()
    plot = pax.ParallelPlot().set_data(rows)
    fig = plot.render(figsize=(12.0, 5.0))
    try:
        fig.savefig(png_path)
    finally:
        plt.close(fig)
    plot.to_json(json_path)
    restored = pax.ParallelPlot.from_json(json_path)
    elapsed = time.perf_counter() - start

    # Correctness at scale, so this is not a timing-only test.
    assert restored.state == plot.state
    assert len(restored.state.data.rows) == 10_000
    for path in (png_path, json_path):
        assert path.is_file()
        assert path.stat().st_size > 0

    record_property("elapsed_seconds", round(elapsed, 3))
    # ~17x headroom over the ~1.7 s measured on a typical machine, so slower
    # runners pass while algorithmic (e.g. O(n^2)) regressions still fail.
    assert elapsed < 30.0, f"large workflow took {elapsed:.1f}s"
