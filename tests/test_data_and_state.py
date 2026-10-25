from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

import paxplot as pax
from paxplot.rendering import prepare_render_data


def test_set_data_accepts_rows_and_infers_columns() -> None:
    plot = pax.ParallelPlot().set_data([[0.0, "low"], [1.0, "medium"], [None, "low"]])
    assert plot.state.data.rows == [[0.0, "low"], [1.0, "medium"], [None, "low"]]
    assert [column.dtype for column in plot.state.data.columns] == [
        "numeric",
        "categorical",
    ]
    assert plot.state.presentation.axes[1].scale.categories == ["low", "medium"]
    assert "dtype" not in plot.state.presentation.axes[0].model_dump()


def test_numpy_and_missing_values_are_normalized() -> None:
    plot = pax.ParallelPlot().set_data(np.array([[1.0, np.nan], [2.0, np.nan]]))
    assert plot.state.data.rows == [[1.0, None], [2.0, None]]
    assert [column.dtype for column in plot.state.data.columns] == ["numeric"] * 2


def test_canonical_categorical_state_accepts_missing_nan_values() -> None:
    state = pax.PlotState(
        data=pax.PlotData(
            rows=[["low"], [float("nan")]],
            columns=[pax.ColumnSpec(dtype="categorical")],
        ),
        presentation=pax.PlotPresentation(
            axes=[pax.AxisPresentation(scale=pax.AxisScale(categories=["low"]))]
        ),
    )
    prepared = prepare_render_data(state)
    assert prepared.y[0, 0] == 0.5
    assert np.isnan(prepared.y[1, 0])


def test_set_data_rejects_mappings_dataframes_and_bad_rows() -> None:
    for data in ({"A": [0, 1]}, pd.DataFrame({"A": [2, 3]})):
        with pytest.raises(TypeError, match="row-oriented sequences"):
            pax.ParallelPlot().set_data(data)
    for data, message in [
        ([[1, 2], [3]], "same length"),
        ([], "at least one row"),
        ([[]], "at least one value"),
        ([[1], ["bad"]], "mixed numeric"),
        ([[object()]], "unsupported value"),
    ]:
        with pytest.raises(ValueError, match=message):
            pax.ParallelPlot().set_data(data)


def test_position_configuration_and_focused_updates() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0.0, "low"], [1.0, "high"]])
        .set_axis(
            0,
            title=pax.AxisTitle(text="Column A", visible=False),
            scale=pax.AxisScale(limits=(-1.0, 3.0)),
            ticks=pax.AxisTicks(count=3),
        )
        .set_axis_ticks(1, ["low", "high"], ["Low", "High"])
        .invert_axis(0)
        .set_axis_label(0, "Updated A")
        .set_line_style(1, color="crimson", width=2.0)
    )
    axis = plot.state.presentation.axes[0]
    assert axis.title == pax.AxisTitle(text="Updated A", visible=False)
    assert axis.scale == pax.AxisScale(limits=(-1.0, 3.0), inverted=True)
    assert axis.ticks.count == 3
    assert plot.state.presentation.axes[1].ticks.labels.text == ["Low", "High"]
    assert plot.state.presentation.lines.overrides[1].color == "crimson"
    plot.set_axis_limits(0, -2.0, 4.0)
    assert plot.state.presentation.axes[0].scale.inverted


def test_component_replacement_resets_only_supplied_components() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0], [1]])
        .set_axis(
            0,
            scale=pax.AxisScale(limits=(-1, 2), inverted=True),
            title=pax.AxisTitle(text="Retained", visible=False),
            ticks=pax.AxisTicks(count=3),
            spine=pax.AxisSpine(visible=False),
        )
    )
    original = plot.state.model_dump()
    assert plot.set_axis(0) is plot
    assert plot.state.model_dump() == original
    assert plot.set_axis(0, scale=pax.AxisScale(inverted=True)) is plot
    axis = plot.state.presentation.axes[0]
    assert axis.scale.limits == (None, None)
    assert not axis.title.visible and axis.title.text == "Retained"
    assert axis.ticks.count == 3 and not axis.spine.visible
    plot.set_axis(0, title=pax.AxisTitle())
    assert plot.state.presentation.axes[0].title == pax.AxisTitle()
    plot.set_axis(0, ticks=pax.AxisTicks())
    assert plot.state.presentation.axes[0].ticks.count is None


@pytest.mark.parametrize("values", [[0.0, 1.0], ["low", "high"]])
def test_tick_edits_preserve_appearance_and_visibility_preserves_content(
    values, tmp_path
) -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[value] for value in values])
        .set_axis(
            0,
            title=pax.AxisTitle(text="Retained title", visible=False),
            spine=pax.AxisSpine(visible=False),
            ticks=pax.AxisTicks(
                count=3,
                marks=pax.AxisTickMarks(visible=False),
                labels=pax.AxisTickLabels(visible=False),
            ),
        )
    )
    plot.set_axis_ticks(0, values, ["Bottom", "Top"])
    axis = plot.state.presentation.axes[0]
    assert not axis.ticks.marks.visible and not axis.ticks.labels.visible
    assert axis.ticks.count == 3
    path = tmp_path / "hidden.json"
    plot.to_json(path)
    restored = pax.ParallelPlot.from_json(path)
    assert restored.state == plot.state
    ticks = axis.ticks.model_dump()
    ticks["marks"]["visible"] = True
    ticks["labels"]["visible"] = True
    restored.set_axis(
        0,
        title=pax.AxisTitle(text=axis.title.text),
        spine=pax.AxisSpine(),
        ticks=pax.AxisTicks(**ticks),
    )
    shown = restored.state.presentation.axes[0]
    assert shown.title.text == "Retained title" and shown.title.visible
    assert (
        shown.spine.visible and shown.ticks.marks.visible and shown.ticks.labels.visible
    )
    assert shown.ticks.values == values
    assert shown.ticks.labels.text == ["Bottom", "Top"]
    assert prepare_render_data(restored.state).axes[0].tick_labels == ["Bottom", "Top"]


@pytest.mark.parametrize(
    "method,args",
    [
        ("set_axis", ("A",)),
        ("set_line_style", ("row-1",)),
        ("set_axis", (2,)),
        ("set_axis", (-1,)),
        ("set_line_style", (2,)),
    ],
)
def test_invalid_indices(method, args) -> None:
    plot = pax.ParallelPlot().set_data([[0], [1]])
    with pytest.raises((TypeError, ValueError), match="index"):
        getattr(plot, method)(*args)


@pytest.mark.parametrize(
    "edit",
    [
        lambda p: p.set_axis_limits(0, 3, -1),
        lambda p: p.set_axis_limits(1, 0, 1),
        lambda p: p.set_axis(0, scale=pax.AxisScale(categories=["bad"])),
        lambda p: p.set_axis(1, scale=pax.AxisScale(categories=["missing"])),
        lambda p: p.set_axis_ticks(0, [0, 1], ["one"]),
        lambda p: p.set_axis_ticks(0, ["bad"]),
        lambda p: p.set_axis_ticks(1, ["unknown"]),
        lambda p: p.set_axis_label(0, ["invalid"]),
        lambda p: p.set_default_line_style(alpha=2),
        lambda p: p.set_line_style(0, width=-1),
        lambda p: p.set_colorbar(1),
        lambda p: p.set_colorbar(0, limits=(3, -1)),
        lambda p: p.set_data([[1], ["mixed"]]),
        lambda p: p.set_axis(
            0,
            title=pax.AxisTitle(text="uncommitted"),
            scale=pax.AxisScale(categories=["bad"]),
        ),
    ],
)
def test_failed_edits_are_atomic(edit) -> None:
    plot = pax.ParallelPlot().set_data([[0, "low"], [1, "high"]])
    state = plot.state
    before = state.model_dump()
    with pytest.raises((ValueError, TypeError)):
        edit(plot)
    assert plot.state is state
    assert plot.state.model_dump() == before


@pytest.mark.parametrize(
    "change,message",
    [
        (lambda s: s["data"]["rows"].append([1]), "same length"),
        (lambda s: s["data"]["columns"].pop(), "column metadata"),
        (lambda s: s["presentation"]["axes"].pop(), "number of axes"),
        (lambda s: s["data"]["columns"][0].update(dtype="categorical"), "dtype"),
        (
            lambda s: s["presentation"]["lines"]["overrides"].update({9: {}}),
            "unknown row",
        ),
        (
            lambda s: s["presentation"]["lines"].update(color_encoding={"axis": 9}),
            "unknown axis",
        ),
        (
            lambda s: s["presentation"]["lines"].update(color_encoding={"axis": 1}),
            "numeric axes",
        ),
        (
            lambda s: s["presentation"]["axes"][0]["scale"].update(categories=["bad"]),
            "numeric axes",
        ),
        (
            lambda s: s["presentation"]["axes"][1]["scale"].update(limits=[0, 1]),
            "categorical axes",
        ),
    ],
)
def test_aggregate_validation(change, message) -> None:
    state = pax.ParallelPlot().set_data([[0, "low"], [1, "high"]]).state.model_dump()
    change(state)
    with pytest.raises(ValidationError, match=message):
        pax.PlotState.model_validate(state)


def test_models_are_revalidated_on_replacement() -> None:
    plot = pax.ParallelPlot().set_data([[0], [1]])
    bad_scale = pax.AxisScale.model_construct(limits=(3, -1))
    with pytest.raises(ValidationError, match="lower limit"):
        plot.set_axis(0, scale=bad_scale)
    assert plot.state.presentation.axes[0].scale.limits == (None, None)


def test_set_data_rebuilds_components_but_retains_default_lines() -> None:
    plot = (
        pax.ParallelPlot()
        .set_data([[0], [1]])
        .set_default_line_style(color="black", alpha=0.4, width=2)
        .set_line_style(1, color="red")
        .set_colorbar(0)
        .set_axis(
            0,
            title=pax.AxisTitle(text="Old", visible=False),
            scale=pax.AxisScale(inverted=True),
        )
    )
    default = plot.state.presentation.lines.default.model_dump()
    assert plot.set_data([["low", 3], ["high", 4]]) is plot
    assert plot.state.presentation.lines.default.model_dump() == default
    assert plot.state.presentation.lines.overrides == {}
    assert plot.state.presentation.lines.color_encoding is None
    assert plot.state.presentation.axes[0].title == pax.AxisTitle()
    assert not plot.state.presentation.axes[0].scale.inverted
    assert plot.state.presentation.axes[0].scale.categories == ["low", "high"]


def test_json_round_trip_includes_defaults_and_integer_override_keys(tmp_path) -> None:
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
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document == {
        "schema_version": 2,
        "state": plot.state.model_dump(mode="json"),
    }
    assert document["state"]["presentation"]["axes"][0]["title"] == {
        "text": "Column A",
        "visible": True,
    }
    restored = pax.ParallelPlot.from_json(path)
    assert restored.state == plot.state
    assert list(restored.state.presentation.lines.overrides) == [1]
    assert prepare_render_data(restored.state).colorbar.label == "A scale"


@pytest.mark.parametrize("version", [1, 3, True, 2.0, "2", None])
def test_obsolete_and_invalid_json_versions_rejected(version, tmp_path) -> None:
    path = tmp_path / "plot.json"
    path.write_text(
        json.dumps({"schema_version": version, "state": {}}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="supported versions: 2"):
        pax.ParallelPlot.from_json(path)


@pytest.mark.parametrize(
    "document",
    [
        {},
        {"schema_version": 2},
        {"schema_version": 2, "state": {"data": [], "axes": []}},
        [],
        {"data": {"rows": [], "columns": []}, "presentation": {}},
    ],
)
def test_missing_envelopes_payloads_and_obsolete_state_rejected(
    document, tmp_path
) -> None:
    path = tmp_path / "plot.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValidationError):
        pax.ParallelPlot.from_json(path)


@pytest.mark.parametrize(
    "location",
    [
        (),
        ("state",),
        ("state", "data"),
        ("state", "data", "columns", 0),
        ("state", "presentation"),
        ("state", "presentation", "axes", 0),
        ("state", "presentation", "axes", 0, "scale"),
        ("state", "presentation", "axes", 0, "title"),
        ("state", "presentation", "axes", 0, "ticks"),
        ("state", "presentation", "axes", 0, "ticks", "labels"),
        ("state", "presentation", "axes", 0, "ticks", "marks"),
        ("state", "presentation", "axes", 0, "spine"),
        ("state", "presentation", "lines"),
        ("state", "presentation", "lines", "default"),
        ("state", "presentation", "lines", "overrides", "0"),
        ("state", "presentation", "lines", "color_encoding"),
        ("state", "presentation", "lines", "color_encoding", "colorbar"),
        ("state", "presentation", "lines", "color_encoding", "colorbar", "title"),
    ],
)
def test_unknown_fields_rejected_at_every_level(location, tmp_path) -> None:
    plot = pax.ParallelPlot().set_data([[0], [1]]).set_colorbar(0).set_line_style(0)
    document = {"schema_version": 2, "state": plot.state.model_dump(mode="json")}
    target = document
    for key in location:
        target = target[key]
    target["obsolete"] = True
    path = tmp_path / "plot.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValidationError, match="Extra inputs"):
        pax.ParallelPlot.from_json(path)
