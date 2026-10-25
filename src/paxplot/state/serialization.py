"""Version 2 JSON envelopes containing the canonical plot state."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import field_validator

from paxplot.state.schema import PlotState, StateModel

PLOT_STATE_SCHEMA_VERSION = 2


class _StateDocument(StateModel):
    schema_version: Literal[2]
    state: PlotState

    @field_validator("schema_version", mode="before")
    @classmethod
    def validate_version(cls, value: object) -> object:
        if type(value) is not int or value != PLOT_STATE_SCHEMA_VERSION:
            raise ValueError(
                f"plot state requires schema version {value!r}; supported versions: 2"
            )
        return value


def save_state(state: PlotState, path: str | Path) -> None:
    """Write validated canonical state, including defaults, in a v2 envelope."""

    document = _StateDocument(schema_version=PLOT_STATE_SCHEMA_VERSION, state=state)
    Path(path).write_text(document.model_dump_json(indent=2), encoding="utf-8")


def load_state(path: str | Path) -> PlotState:
    """Read a strict v2 envelope; obsolete formats and fields are rejected."""

    return _StateDocument.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    ).state
