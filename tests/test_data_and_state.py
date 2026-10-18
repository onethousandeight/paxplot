from __future__ import annotations

import json

import pandas as pd
import pytest
from pydantic import ValidationError

import paxplot as pax
from paxplot.rendering import prepare_render_data
from paxplot.state import AxisConfig, PlotState, TickConfig


def test_set_data_accepts_rows_and_infers_axes() -> None:
    plot = pax.ParallelPlot().set_data([[0.0, "low"], [1.0, "medium"], [None, "low"]])

    assert plot.state.data == [[0.0, "low"], [1.0, "medium"], [None, "low"]]
    assert [axis.dtype for axis in plot.state.axes] == ["numeric", "categorical"]
    assert plot.state.axes[1].categories == ["low", "medium"]


def test_set_data_rejects_mappings_dataframes_and_bad_rows() -> None:
    with pytest.raises(TypeError, match="row-oriented sequences"):
        pax.ParallelPlot().set_data({"A": [0, 1], "B": ["x", "y"]})

    with pytest.raises(TypeError, match="row-oriented sequences"):
        pax.ParallelPlot().set_data(pd.DataFrame({"A": [2, 3], "B": ["z", "w"]}))

    with pytest.raises(ValueError, match="same length"):
        pax.ParallelPlot().set_data([[1, 2], [3]])

    with pytest.raises(ValueError, match="at least one row"):
        pax.ParallelPlot().set_data([])


def test_mixed_numeric_and_string_columns_raise() -> None:
    with pytest.raises(ValueError, match="mixed numeric and string"):
        pax.ParallelPlot().set_data([[1], ["bad"]])


def test_position_axis_and_row_configuration_methods() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, "low"], [1.0, "high"]])
        .set_axis(0, label="Column A", limits=(-1.0, 3.0), tick_count=3)
        .set_axis(1, ticks=["low", "high"], tick_labels=["Low", "High"])
        .invert_axis(0)
        .set_line_style(1, color="crimson", width=2.0)
    )

    axis = plot.state.axes[0]
    assert axis.label == "Column A"
    assert axis.lower == -1.0
    assert axis.upper == 3.0
    assert axis.ticks.count == 3
    assert axis.inverted is True
    assert plot.state.axes[1].ticks.values == ["low", "high"]
    assert plot.state.axes[1].ticks.labels == ["Low", "High"]
    assert plot.state.line_styles[1].color == "crimson"


def test_string_axis_and_out_of_range_row_raise() -> None:
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]])

    with pytest.raises(TypeError, match="integer index"):
        plot.set_axis("A")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unknown axis index"):
        plot.set_axis(2)

    with pytest.raises(TypeError, match="integer index"):
        plot.set_line_style("row-1", color="crimson")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unknown row index"):
        plot.set_line_style(2, color="crimson")


def test_state_validation_rejects_bad_lengths_and_tick_labels() -> None:
    with pytest.raises(ValidationError, match="same length"):
        TickConfig(values=[0, 1], labels=["only one"])

    with pytest.raises(ValidationError, match="number of axes must match row width"):
        PlotState(data=[[1]], axes=[])

    with pytest.raises(ValidationError, match="unknown row index"):
        PlotState(
            data=[[1.0]],
            axes=[AxisConfig(dtype="numeric")],
            line_styles={1: {}},
        )


def test_json_round_trip(tmp_path) -> None:
    path = tmp_path / "plot.json"
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, "low"], [1.0, "high"]])
        .set_axis_label(0, "Column A")
        .set_default_line_style(color="black", alpha=0.5)
        .set_line_style(1, color="crimson", width=2.0)
        .set_colorbar(0, label="A scale")
    )

    plot.to_json(path)
    restored = pax.ParallelPlot.from_json(path)

    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert document["state"]["axes"][0]["label"] == "Column A"
    assert restored.state == plot.state
    assert prepare_render_data(restored.state).colorbar is not None


def test_versioned_json_ignores_unknown_optional_fields(tmp_path) -> None:
    path = tmp_path / "plot.json"
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]]).set_axis_label(0, "A")

    plot.to_json(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["extra_top_level"] = {"ignored": True}
    document["state"]["extra_state_field"] = "ignored"
    document["state"]["axes"][0]["extra_axis_field"] = "ignored"
    path.write_text(json.dumps(document), encoding="utf-8")

    restored = pax.ParallelPlot.from_json(path)

    assert restored.state == plot.state


def test_unsupported_future_json_version_raises(tmp_path) -> None:
    path = tmp_path / "plot.json"
    path.write_text(
        json.dumps({"schema_version": 2, "state": {"data": [], "axes": []}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="schema version 2.*supported versions: 1"):
        pax.ParallelPlot.from_json(path)


def test_legacy_unversioned_json_still_loads(tmp_path) -> None:
    path = tmp_path / "plot.json"
    plot = pax.ParallelPlot().set_data([[0.0], [1.0]]).set_axis_label(0, "A")
    path.write_text(plot.state.model_dump_json(), encoding="utf-8")

    restored = pax.ParallelPlot.from_json(path)

    assert restored.state == plot.state
