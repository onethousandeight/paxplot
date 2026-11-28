"""Public paxplot plotting object."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence, Set
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from paxplot._values import is_missing, resolve_categories
from paxplot.rendering import prepare_render_data, render_matplotlib
from paxplot.state import (
    AxisPresentation,
    AxisScale,
    AxisSpine,
    AxisTicks,
    AxisTitle,
    ColorbarPresentation,
    ColorbarTicks,
    ColorbarTitle,
    ColorEncoding,
    ColumnSpec,
    LinePresentation,
    LineStyleOverride,
    PlotData,
    PlotPresentation,
    PlotState,
    infer_dtype,
    load_state,
    save_state,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class _Unset:
    """Sentinel distinguishing omitted arguments from explicit ``None``."""


_UNSET = _Unset()


def _plain_value(value: Any) -> object:
    if is_missing(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def _coerce_rows(data: Iterable[Sequence[object]]) -> list[list[object]]:
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        msg = "set_data accepts row-oriented sequences only"
        raise TypeError(msg)

    if isinstance(data, Mapping | Set):
        msg = "set_data accepts row-oriented sequences only"
        raise TypeError(msg)

    try:
        iterator = iter(data)
    except TypeError as exc:
        msg = "data must be a row-oriented sequence"
        raise TypeError(msg) from exc

    rows = [_coerce_row(row) for row in iterator]
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
    if isinstance(row, Mapping | Set):
        msg = "each row must be an ordered sequence of values"
        raise TypeError(msg)
    try:
        values = list(row)
    except TypeError as exc:
        msg = "each row must be a sequence of values"
        raise TypeError(msg) from exc
    return [_plain_value(value) for value in values]


def _column_values(rows: Sequence[Sequence[object]], axis: int) -> list[object]:
    return [row[axis] for row in rows]


class ParallelPlot:
    """User-facing object for configuring, rendering, and saving a paxplot."""

    def __init__(self, state: PlotState | None = None) -> None:
        self.state = state if state is not None else PlotState()

    def set_data(self, data: Iterable[Sequence[object]]) -> Self:
        """Set plot data from rectangular row-oriented values."""

        rows = _coerce_rows(data)
        axis_count = len(rows[0])
        columns = [_column_values(rows, axis) for axis in range(axis_count)]
        dtypes = [infer_dtype(values) for values in columns]
        self._replace_state(
            data=PlotData(
                rows=rows,
                columns=[ColumnSpec(dtype=dtype) for dtype in dtypes],
            ),
            presentation=PlotPresentation(
                axes=[
                    AxisPresentation(
                        scale=AxisScale(
                            categories=(
                                resolve_categories(values)
                                if dtype == "categorical"
                                else None
                            )
                        )
                    )
                    for values, dtype in zip(columns, dtypes, strict=True)
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
    ) -> Self:
        """Replace supplied components, preserving omitted components.

        Each component owns both configuration and appearance. To change only
        part of a component while retaining its settings, use a focused method
        or construct a replacement from its current ``model_dump()``.
        """

        replacement = self._axis(axis).model_copy(deep=True)
        if scale is not None:
            replacement.scale = scale
        if title is not None:
            replacement.title = title
        if ticks is not None:
            replacement.ticks = ticks
        if spine is not None:
            replacement.spine = spine
        self._replace_axis(axis, replacement)
        return self

    def set_axis_label(self, axis: int, label: str) -> Self:
        """Update title text, preserving its appearance."""

        replacement = self._axis(axis).model_copy(deep=True)
        replacement.title.text = label
        self._replace_axis(axis, replacement)
        return self

    def set_axis_limits(
        self,
        axis: int,
        lower: float | None | _Unset = _UNSET,
        upper: float | None | _Unset = _UNSET,
    ) -> Self:
        """Update numeric limits, preserving omitted bounds and other settings."""

        replacement = self._axis(axis).model_copy(deep=True)
        lower_bound, upper_bound = replacement.scale.limits
        if lower is not _UNSET:
            lower_bound = lower
        if upper is not _UNSET:
            upper_bound = upper
        replacement.scale.limits = (lower_bound, upper_bound)
        self._replace_axis(axis, replacement)
        return self

    def reset_axis_limits(
        self,
        axis: int,
        *,
        lower: bool = True,
        upper: bool = True,
    ) -> Self:
        """Reset selected limits to their automatic data-derived values."""

        replacement = self._axis(axis).model_copy(deep=True)
        lower_bound, upper_bound = replacement.scale.limits
        replacement.scale.limits = (
            None if lower else lower_bound,
            None if upper else upper_bound,
        )
        self._replace_axis(axis, replacement)
        return self

    def set_axis_ticks(
        self,
        axis: int,
        values: list[float | str],
        labels: list[str] | None = None,
    ) -> Self:
        """Update reference values and text, preserving appearance and count."""

        replacement = self._axis(axis).model_copy(deep=True)
        replacement.ticks.values = values
        replacement.ticks.labels.text = labels
        self._replace_axis(axis, replacement)
        return self

    def invert_axis(self, axis: int, inverted: bool = True) -> Self:
        """Update inversion, preserving the other scale settings."""

        replacement = self._axis(axis).model_copy(deep=True)
        replacement.scale.inverted = inverted
        self._replace_axis(axis, replacement)
        return self

    def set_default_line_style(
        self,
        *,
        color: str | None | _Unset = _UNSET,
        alpha: float | None | _Unset = _UNSET,
        width: float | None | _Unset = _UNSET,
        linestyle: str | None | _Unset = _UNSET,
        zorder: float | None | _Unset = _UNSET,
    ) -> Self:
        """Update default line appearance, preserving omitted fields.

        Passing ``None`` resets a field, since every ``LineStyle`` field is
        optional.
        """

        replacement = self.state.presentation.lines.default.model_copy()
        for name, value in (
            ("color", color),
            ("alpha", alpha),
            ("width", width),
            ("linestyle", linestyle),
            ("zorder", zorder),
        ):
            if value is not _UNSET:
                setattr(replacement, name, value)
        self._replace_lines(default=replacement)
        return self

    def set_line_style(
        self,
        row: int,
        *,
        color: str | None | _Unset = _UNSET,
        alpha: float | None | _Unset = _UNSET,
        width: float | None | _Unset = _UNSET,
        linestyle: str | None | _Unset = _UNSET,
        zorder: float | None | _Unset = _UNSET,
    ) -> Self:
        """Update one row's line appearance, preserving omitted fields.

        Passing ``None`` resets a field to the default line appearance.
        """

        self._row(row)
        styles = dict(self.state.presentation.lines.overrides)
        replacement = styles[row].model_copy() if row in styles else LineStyleOverride()
        for name, value in (
            ("color", color),
            ("alpha", alpha),
            ("width", width),
            ("linestyle", linestyle),
            ("zorder", zorder),
        ):
            if value is not _UNSET:
                setattr(replacement, name, value)
        styles[row] = replacement
        self._replace_lines(overrides=styles)
        return self

    def clear_line_style(self, row: int) -> Self:
        """Remove all style overrides for one row."""

        self._row(row)
        styles = dict(self.state.presentation.lines.overrides)
        styles.pop(row, None)
        self._replace_lines(overrides=styles)
        return self

    def set_colorbar(
        self,
        axis: int,
        *,
        palette: str | list[str] = "viridis",
        title: ColorbarTitle | None = None,
        ticks: ColorbarTicks | None = None,
        limits: tuple[float | None, float | None] | None = None,
    ) -> Self:
        """Configure color encoding, replacing supplied colorbar components.

        Omitted title and tick components retain their existing settings.
        Palette and limits use the supplied values or their defaults each call.
        """

        self._axis(axis)
        lower, upper = limits or (None, None)
        encoding = self.state.presentation.lines.color_encoding
        colorbar = (
            encoding.colorbar.model_copy(deep=True)
            if encoding is not None
            else ColorbarPresentation()
        )
        if title is not None:
            colorbar.title = title
        if ticks is not None:
            colorbar.ticks = ticks
        self._replace_lines(
            color_encoding=ColorEncoding(
                axis=axis,
                palette=palette,
                lower=lower,
                upper=upper,
                colorbar=colorbar,
            )
        )
        return self

    def render(self, **kwargs: Any) -> Figure:
        """Render the plot with matplotlib and return a Figure."""

        return render_matplotlib(prepare_render_data(self.state), **kwargs)

    def to_json(self, path: str | Path) -> None:
        """Serialize this plot definition to JSON."""

        save_state(self.state, path)

    @classmethod
    def from_json(cls, path: str | Path) -> Self:
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

    def _row(self, row: int) -> int:
        if not isinstance(row, int):
            msg = "row must be an integer index"
            raise TypeError(msg)
        if row < 0 or row >= len(self.state.data.rows):
            msg = f"unknown row index {row}"
            raise ValueError(msg)
        return row

    def _replace_axis(self, index: int, replacement: AxisPresentation) -> None:
        axes = list(self.state.presentation.axes)
        axes[index] = replacement
        self._replace_state(
            presentation=self.state.presentation.model_copy(update={"axes": axes})
        )

    def _replace_lines(self, **updates: Any) -> None:
        lines = self.state.presentation.lines.model_copy(update=updates)
        self._replace_state(
            presentation=self.state.presentation.model_copy(update={"lines": lines})
        )

    def _replace_state(self, **updates: Any) -> None:
        """Validate an entire candidate before committing any edit."""

        self.state = PlotState.model_validate(self.state.model_copy(update=updates))
