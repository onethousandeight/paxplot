"""Public PaxPlot plotting object."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isnan
from pathlib import Path
from typing import Any

from paxplot.rendering import prepare_render_data, render_matplotlib
from paxplot.state import (
    AxisConfig,
    ColorbarConfig,
    ColorEncoding,
    LineStyle,
    LineStyleOverride,
    PlotState,
    TickConfig,
    load_state,
    save_state,
)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(isnan(value))
    except TypeError:
        return False


def _plain_value(value: Any) -> object:
    if _is_missing(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def _infer_dtype(values: Sequence[object]) -> str:
    has_number = False
    has_string = False
    for value in values:
        if _is_missing(value):
            continue
        if isinstance(value, bool):
            has_number = True
        elif isinstance(value, (int, float)):
            has_number = True
        elif isinstance(value, str):
            has_string = True
        else:
            msg = f"unsupported value {value!r}; expected numbers, strings, or missing"
            raise ValueError(msg)

    if has_number and has_string:
        msg = "mixed numeric and string axes are not supported"
        raise ValueError(msg)
    return "categorical" if has_string else "numeric"


def _categories(values: Sequence[object]) -> list[str] | None:
    if _infer_dtype(values) != "categorical":
        return None
    categories: list[str] = []
    for value in values:
        if _is_missing(value):
            continue
        category = str(value)
        if category not in categories:
            categories.append(category)
    return categories


def _coerce_rows(data: Any) -> list[list[object]]:
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        msg = "set_data accepts row-oriented sequences only"
        raise TypeError(msg)

    if isinstance(data, Mapping):
        msg = "set_data accepts row-oriented sequences only"
        raise TypeError(msg)

    rows = [_coerce_row(row) for row in data]
    if not rows:
        msg = "data must contain at least one row"
        raise ValueError(msg)

    row_width = len(rows[0])
    if any(len(row) != row_width for row in rows):
        msg = "all rows must have the same length"
        raise ValueError(msg)
    if row_width == 0:
        msg = "data rows must contain at least one value"
        raise ValueError(msg)
    return rows


def _coerce_row(row: Any) -> list[object]:
    if isinstance(row, str | bytes):
        msg = "each row must be a sequence of values"
        raise TypeError(msg)
    return [_plain_value(value) for value in row]


def _column_values(rows: Sequence[Sequence[object]], axis: int) -> list[object]:
    return [row[axis] for row in rows]


class ParallelPlot:
    """User-facing object for configuring, rendering, and saving a PaxPlot."""

    def __init__(self, state: PlotState | None = None) -> None:
        self.state = state or PlotState()

    def set_data(self, data) -> ParallelPlot:
        """Set plot data from rectangular row-oriented values."""

        rows = _coerce_rows(data)
        axis_count = len(rows[0])
        axes = [
            AxisConfig(
                dtype=_infer_dtype(values),  # type: ignore[arg-type]
                categories=_categories(values),
            )
            for values in (_column_values(rows, axis) for axis in range(axis_count))
        ]
        self.state = PlotState(
            data=rows,
            axes=axes,
            default_line_style=self.state.default_line_style,
        )
        return self

    def set_axis(
        self,
        axis: int,
        *,
        label: str | None = None,
        limits: tuple[float | None, float | None] | None = None,
        ticks: list[float | str] | None = None,
        tick_labels: list[str] | None = None,
        tick_count: int | None = None,
        categories: list[str] | None = None,
        inverted: bool | None = None,
    ) -> ParallelPlot:
        """Configure an axis in one call."""

        axis_config = self._axis(axis)
        update = axis_config.model_dump()
        if label is not None:
            update["label"] = label
        if limits is not None:
            update["lower"], update["upper"] = limits
        if categories is not None:
            update["categories"] = categories
        if inverted is not None:
            update["inverted"] = inverted
        update["ticks"] = TickConfig(
            values=ticks if ticks is not None else axis_config.ticks.values,
            labels=tick_labels if tick_labels is not None else axis_config.ticks.labels,
            count=tick_count if tick_count is not None else axis_config.ticks.count,
        )
        self._replace_axis(axis, AxisConfig(**update))
        return self

    def set_axis_label(self, axis: int, label: str) -> ParallelPlot:
        axis_config = self._axis(axis)
        self._replace_axis(axis, axis_config.model_copy(update={"label": label}))
        return self

    def set_axis_limits(
        self,
        axis: int,
        lower: float | None = None,
        upper: float | None = None,
    ) -> ParallelPlot:
        axis_config = self._axis(axis)
        self._replace_axis(
            axis,
            axis_config.model_copy(update={"lower": lower, "upper": upper}),
        )
        return self

    def set_axis_ticks(
        self,
        axis: int,
        values: list[float | str],
        labels: list[str] | None = None,
    ) -> ParallelPlot:
        axis_config = self._axis(axis)
        tick_config = TickConfig(values=values, labels=labels)
        self._replace_axis(axis, axis_config.model_copy(update={"ticks": tick_config}))
        return self

    def invert_axis(self, axis: int, inverted: bool = True) -> ParallelPlot:
        axis_config = self._axis(axis)
        self._replace_axis(
            axis,
            axis_config.model_copy(update={"inverted": inverted}),
        )
        return self

    def set_default_line_style(
        self,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
    ) -> ParallelPlot:
        update = self.state.default_line_style.model_dump()
        if color is not None:
            update["color"] = color
        if alpha is not None:
            update["alpha"] = alpha
        if width is not None:
            update["width"] = width
        if linestyle is not None:
            update["linestyle"] = linestyle
        self._replace_state(default_line_style=LineStyle(**update))
        return self

    def set_line_style(
        self,
        row: int,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
        zorder: float | None = None,
    ) -> ParallelPlot:
        if not isinstance(row, int):
            msg = "row must be an integer index"
            raise TypeError(msg)
        if row < 0 or row >= len(self.state.data):
            msg = f"unknown row index {row}"
            raise ValueError(msg)
        styles = dict(self.state.line_styles)
        styles[row] = LineStyleOverride(
            color=color,
            alpha=alpha,
            width=width,
            linestyle=linestyle,
            zorder=zorder,
        )
        self._replace_state(line_styles=styles)
        return self

    def set_colorbar(
        self,
        axis: int,
        *,
        palette: str | list[str] = "viridis",
        label: str | None = None,
        limits: tuple[float | None, float | None] | None = None,
    ) -> ParallelPlot:
        axis_config = self._axis(axis)
        if axis_config.dtype != "numeric":
            msg = "colorbar encoding only supports numeric axes"
            raise ValueError(msg)
        lower, upper = limits or (None, None)
        self._replace_state(
            color_encoding=ColorEncoding(
                axis=axis,
                palette=palette,
                lower=lower,
                upper=upper,
                colorbar=ColorbarConfig(label=label),
            )
        )
        return self

    def render(self, **kwargs):
        """Render the plot with matplotlib and return a Figure."""

        return render_matplotlib(prepare_render_data(self.state), **kwargs)

    def to_json(self, path: str | Path) -> None:
        """Serialize this plot definition to JSON."""

        save_state(self.state, path)

    @classmethod
    def from_json(cls, path: str | Path) -> ParallelPlot:
        """Load a plot definition from JSON."""

        return cls(load_state(path))

    def _axis(self, axis: int) -> AxisConfig:
        if not isinstance(axis, int):
            msg = "axis must be an integer index"
            raise TypeError(msg)
        if axis < 0:
            msg = f"unknown axis index {axis}"
            raise ValueError(msg)
        try:
            return self.state.axes[axis]
        except IndexError as exc:
            msg = f"unknown axis index {axis}"
            raise ValueError(msg) from exc

    def _replace_axis(self, index: int, axis: AxisConfig) -> None:
        axes = list(self.state.axes)
        axes[index] = axis
        self._replace_state(axes=axes)

    def _replace_state(self, **updates) -> None:
        data = self.state.model_dump()
        data.update(updates)
        self.state = PlotState(**data)
