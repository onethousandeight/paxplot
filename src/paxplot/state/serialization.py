"""Version 2 JSON envelopes containing the canonical plot state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import field_validator

from paxplot.state.schema import PlotState, StateModel

PLOT_STATE_SCHEMA_VERSION = 2

_INDENT = "  "


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


def _format_json(value: object, level: int = 0) -> str:
    """Indent structure while keeping scalar lists, such as rows, on one line."""

    if isinstance(value, dict):
        if not value:
            return "{}"
        prefix = _INDENT * (level + 1)
        entries = [
            f"{prefix}{json.dumps(key)}: {_format_json(item, level + 1)}"
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(entries) + "\n" + _INDENT * level + "}"
    if isinstance(value, list):
        if all(not isinstance(item, dict | list) for item in value):
            return json.dumps(value, ensure_ascii=False)
        prefix = _INDENT * (level + 1)
        entries = [f"{prefix}{_format_json(item, level + 1)}" for item in value]
        return "[\n" + ",\n".join(entries) + "\n" + _INDENT * level + "]"
    return json.dumps(value, ensure_ascii=False)


def save_state(state: PlotState, path: str | Path) -> None:
    """Write validated canonical state, including defaults, in a v2 envelope.

    Data rows are written one observation per line; other structures keep one
    entry per line so documents stay readable and diff-friendly.
    """

    document = _StateDocument(schema_version=PLOT_STATE_SCHEMA_VERSION, state=state)
    text = _format_json(document.model_dump(mode="json"))
    Path(path).write_text(text + "\n", encoding="utf-8")


def load_state(path: str | Path) -> PlotState:
    """Read a strict v2 envelope; obsolete formats and fields are rejected."""

    return _StateDocument.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    ).state
