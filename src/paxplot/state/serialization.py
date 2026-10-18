"""JSON serialization helpers for PaxPlot state."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paxplot.state.schema import PlotState

PLOT_STATE_SCHEMA_VERSION = 1
SUPPORTED_PLOT_STATE_SCHEMA_VERSIONS = (PLOT_STATE_SCHEMA_VERSION,)


def save_state(state: PlotState, path: str | Path) -> None:
    """Write a plot state to JSON."""

    output = Path(path)
    document = {
        "schema_version": PLOT_STATE_SCHEMA_VERSION,
        "state": state.model_dump(mode="json"),
    }
    output.write_text(json.dumps(document, indent=2), encoding="utf-8")


def load_state(path: str | Path) -> PlotState:
    """Read a plot state from JSON."""

    source = Path(path)
    return _state_from_json(source.read_text(encoding="utf-8"))


def _state_from_json(source: str) -> PlotState:
    """Parse a plot-state JSON document into the current state model."""

    return _state_from_document(json.loads(source))


def _state_from_document(document: Any) -> PlotState:
    """Normalize supported plot-state JSON documents before validation."""

    if not isinstance(document, Mapping):
        return PlotState.model_validate(document)

    if "schema_version" not in document:
        return PlotState.model_validate(document)

    schema_version = document["schema_version"]
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version not in SUPPORTED_PLOT_STATE_SCHEMA_VERSIONS
    ):
        supported = ", ".join(
            str(version) for version in SUPPORTED_PLOT_STATE_SCHEMA_VERSIONS
        )
        msg = (
            f"plot state requires schema version {schema_version!r}; "
            f"supported versions: {supported}"
        )
        raise ValueError(msg)

    state = document.get("state")
    if state is None:
        msg = "plot state schema version 1 requires a 'state' payload"
        raise ValueError(msg)
    return PlotState.model_validate(state)
