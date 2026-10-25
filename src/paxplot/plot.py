"""Public PaxPlot plotting object."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isnan
from pathlib import Path
from typing import Any

from paxplot.rendering import prepare_render_data, render_matplotlib
from paxplot.state import (
    AxisPresentation,
    AxisScale,
    AxisSpine,
    AxisTicks,
    AxisTitle,
    ColorbarPresentation,
    ColorbarTitle,
    ColorEncoding,
    ColumnSpec,
    LinePresentation,
    LineStyle,
    LineStyleOverride,
    PlotData,
    PlotPresentation,
    PlotState,
    load_state,
    save_state,
)
from paxplot.state.schema import infer_dtype


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


def _categories(values: Sequence[object]) -> list[str] | None:
    if infer_dtype(list(values)) != "categorical":
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
        self.state = PlotState.model_validate(state or PlotState())

    def set_data(self, data) -> ParallelPlot:
        """Set plot data from rectangular row-oriented values."""

        rows = _coerce_rows(data)
        axis_count = len(rows[0])
        columns = [_column_values(rows, axis) for axis in range(axis_count)]
        self._replace_state(
            data=PlotData(
                rows=rows,
                columns=[ColumnSpec(dtype=infer_dtype(values)) for values in columns],
            ),
            presentation=PlotPresentation(
                axes=[
                    AxisPresentation(scale=AxisScale(categories=_categories(values)))
                    for values in columns
                ],
                lines=LinePresentation(default=self.state.presentation.lines.default),
            ),
        )
        return self

    def set_axis(
        self,
        axis: int,
        *,
        scale: AxisScale | None = None,
        title: AxisTitle | None = None,
        ticks: AxisTicks | None = None,
        spine: AxisSpine | None = None,
    ) -> ParallelPlot:
        """Replace supplied components, preserving omitted components.

        Each component owns both configuration and appearance. To change only
        part of a component while retaining its settings, use a focused method
        or construct a replacement from its current ``model_dump()``.
        """

        update = self._axis(axis).model_dump()
        for name, component in (
            ("scale", scale),
            ("title", title),
            ("ticks", ticks),
            ("spine", spine),
        ):
            if component is not None:
                update[name] = component
        self._replace_axis(axis, update)
        return self

    def set_axis_label(self, axis: int, label: str) -> ParallelPlot:
        """Update title text, preserving its appearance."""

        update = self._axis(axis).model_dump()
        update["title"]["text"] = label
        self._replace_axis(axis, update)
        return self

    def set_axis_limits(
        self,
        axis: int,
        lower: float | None = None,
        upper: float | None = None,
    ) -> ParallelPlot:
        """Update numeric limits, preserving inversion and category order."""

        update = self._axis(axis).model_dump()
        update["scale"]["limits"] = (lower, upper)
        self._replace_axis(axis, update)
        return self

    def set_axis_ticks(
        self,
        axis: int,
        values: list[float | str],
        labels: list[str] | None = None,
    ) -> ParallelPlot:
        """Update reference values and text, preserving appearance and count."""

        update = self._axis(axis).model_dump()
        update["ticks"]["values"] = values
        update["ticks"]["labels"]["text"] = labels
        self._replace_axis(axis, update)
        return self

    def invert_axis(self, axis: int, inverted: bool = True) -> ParallelPlot:
        """Update inversion, preserving the other scale settings."""

        update = self._axis(axis).model_dump()
        update["scale"]["inverted"] = inverted
        self._replace_axis(axis, update)
        return self

    def set_default_line_style(
        self,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
    ) -> ParallelPlot:
        update = self.state.presentation.lines.default.model_dump()
        if color is not None:
            update["color"] = color
        if alpha is not None:
            update["alpha"] = alpha
        if width is not None:
            update["width"] = width
        if linestyle is not None:
            update["linestyle"] = linestyle
        self._replace_lines(default=LineStyle(**update))
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
        if row < 0 or row >= len(self.state.data.rows):
            msg = f"unknown row index {row}"
            raise ValueError(msg)
        styles = dict(self.state.presentation.lines.overrides)
        styles[row] = LineStyleOverride(
            color=color,
            alpha=alpha,
            width=width,
            linestyle=linestyle,
            zorder=zorder,
        )
        self._replace_lines(overrides=styles)
        return self

    def set_colorbar(
        self,
        axis: int,
        *,
        palette: str | list[str] = "viridis",
        label: str | None = None,
        limits: tuple[float | None, float | None] | None = None,
    ) -> ParallelPlot:
        self._axis(axis)
        lower, upper = limits or (None, None)
        self._replace_lines(
            color_encoding=ColorEncoding(
                axis=axis,
                palette=palette,
                lower=lower,
                upper=upper,
                colorbar=ColorbarPresentation(title=ColorbarTitle(text=label)),
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

    def _axis(self, axis: int) -> AxisPresentation:
        if not isinstance(axis, int):
            msg = "axis must be an integer index"
            raise TypeError(msg)
        if axis < 0:
            msg = f"unknown axis index {axis}"
            raise ValueError(msg)
        try:
            return self.state.presentation.axes[axis]
        except IndexError as exc:
            msg = f"unknown axis index {axis}"
            raise ValueError(msg) from exc

    def _replace_axis(self, index: int, axis: dict) -> None:
        presentation = self.state.presentation.model_dump()
        presentation["axes"][index] = axis
        self._replace_state(presentation=presentation)

    def _replace_lines(self, **updates) -> None:
        presentation = self.state.presentation.model_dump()
        presentation["lines"].update(updates)
        self._replace_state(presentation=presentation)

    def _replace_state(self, **updates) -> None:
        """Validate an entire candidate before committing any edit."""

        candidate = self.state.model_dump()
        candidate.update(updates)
        self.state = PlotState.model_validate(candidate)
