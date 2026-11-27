"""Canonical data and visual component models for Python and JSON state."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from paxplot._values import is_missing


class StateModel(BaseModel):
    """Reject obsolete fields and revalidate supplied model instances."""

    model_config = ConfigDict(extra="forbid", revalidate_instances="always")


def infer_dtype(values: list[object]) -> Literal["numeric", "categorical"]:
    """Infer a column type, treating None and NaN as missing observations."""

    kinds = set()
    for value in values:
        if is_missing(value):
            continue
        if isinstance(value, (int, float)):
            kinds.add("numeric")
        elif isinstance(value, str):
            kinds.add("categorical")
        else:
            raise ValueError(
                f"unsupported value {value!r}; expected numbers, strings, or missing"
            )
    if len(kinds) > 1:
        raise ValueError("mixed numeric and string axes are not supported")
    return "categorical" if "categorical" in kinds else "numeric"


class ColumnSpec(StateModel):
    """Observation type for a column, matched to an axis by position."""

    dtype: Literal["numeric", "categorical"]


class PlotData(StateModel):
    """Observations and their column metadata."""

    rows: list[list[object]] = Field(default_factory=list)
    columns: list[ColumnSpec] = Field(default_factory=list)


_FontName = Annotated[str, Field(min_length=1)]
_PointSize = Annotated[float, Field(gt=0, allow_inf_nan=False)]
_Alpha = Annotated[float, Field(ge=0, le=1)]
_LineWidth = Annotated[float, Field(gt=0)]
_WeightName = Literal[
    "thin",
    "extra light",
    "light",
    "normal",
    "medium",
    "semibold",
    "bold",
    "extra bold",
    "black",
]


class FontSpec(StateModel):
    """Renderer-neutral font intent; None leaves a property to the renderer.

    State stores font intent, not renderer settings. Each renderer maps
    FontSpec onto its native text styling and may approximate or ignore
    fields it cannot honor. Weight names follow the CSS 100-900 scale
    ("thin" through "black"); sizes are absolute points.
    """

    family: _FontName | Annotated[list[_FontName], Field(min_length=1)] | None = None
    size: _PointSize | None = None
    weight: _WeightName | None = None
    style: Literal["normal", "italic", "oblique"] | None = None


class TextAppearance(StateModel):
    """Shared appearance fields inherited directly by text components."""

    visible: bool = True
    font: FontSpec = Field(default_factory=FontSpec)


class AxisTitle(TextAppearance):
    """Axis heading; None selects the automatic heading."""

    text: str | None = None


class AxisTickLabels(TextAppearance):
    """Optional custom strings displayed at the reference values."""

    text: list[str] | None = None


class AxisTickMarks(StateModel):
    """Reference marks, independently visible from their labels."""

    visible: bool = True


class AxisTicks(StateModel):
    """Tick reference values, automatic count, marks, and labels."""

    values: list[float | str] | None = None
    count: int | None = Field(default=None, ge=2, le=1000)
    marks: AxisTickMarks = Field(default_factory=AxisTickMarks)
    labels: AxisTickLabels = Field(default_factory=AxisTickLabels)

    @model_validator(mode="after")
    def validate_label_count(self) -> AxisTicks:
        if (
            self.values is not None
            and self.labels.text is not None
            and len(self.values) != len(self.labels.text)
        ):
            raise ValueError("tick values and labels must have the same length")
        return self


class AxisScale(StateModel):
    """Mapping from observations to positions."""

    limits: tuple[float | None, float | None] = (None, None)
    inverted: bool = False
    categories: list[str] | None = None

    @model_validator(mode="after")
    def validate_scale(self) -> AxisScale:
        lower, upper = self.limits
        if lower is not None and upper is not None and lower > upper:
            raise ValueError("axis lower limit cannot be greater than upper limit")
        if self.categories is not None and len(set(self.categories)) != len(
            self.categories
        ):
            raise ValueError("axis categories must be unique")
        return self


class AxisSpine(StateModel):
    """Vertical stroke connecting an axis's tick marks."""

    visible: bool = True


class AxisPresentation(StateModel):
    """Visual components for one data column."""

    scale: AxisScale = Field(default_factory=AxisScale)
    title: AxisTitle = Field(default_factory=AxisTitle)
    ticks: AxisTicks = Field(default_factory=AxisTicks)
    spine: AxisSpine = Field(default_factory=AxisSpine)


class LineStyle(StateModel):
    """Default serializable line appearance."""

    color: str | None = None
    alpha: _Alpha = 0.7
    width: _LineWidth = 1.0
    linestyle: str = "-"
    zorder: float | None = None


class LineStyleOverride(StateModel):
    """Optional per-row line appearance overrides."""

    color: str | None = None
    alpha: _Alpha | None = None
    width: _LineWidth | None = None
    linestyle: str | None = None
    zorder: float | None = None


class ColorbarTitle(TextAppearance):
    """Colorbar heading."""

    text: str | None = None


class ColorbarTickLabels(TextAppearance):
    """Appearance of automatic colorbar tick labels and offset text."""


class ColorbarTicks(StateModel):
    """Colorbar tick presentation; reference values remain automatic."""

    labels: ColorbarTickLabels = Field(default_factory=ColorbarTickLabels)


class ColorbarPresentation(StateModel):
    """Visual components owned by a color encoding's colorbar."""

    title: ColorbarTitle = Field(default_factory=ColorbarTitle)
    ticks: ColorbarTicks = Field(default_factory=ColorbarTicks)


class ColorEncoding(StateModel):
    """Serializable color encoding intent."""

    axis: int
    palette: str | list[str] = "viridis"
    lower: float | None = None
    upper: float | None = None
    colorbar: ColorbarPresentation = Field(default_factory=ColorbarPresentation)

    @model_validator(mode="after")
    def validate_limits(self) -> ColorEncoding:
        if (
            self.lower is not None
            and self.upper is not None
            and self.lower > self.upper
        ):
            msg = "color encoding lower limit cannot be greater than upper limit"
            raise ValueError(msg)
        if isinstance(self.palette, list) and len(self.palette) < 2:
            msg = "explicit color palettes must contain at least two colors"
            raise ValueError(msg)
        return self


class LinePresentation(StateModel):
    """Default line appearance, row overrides, and optional color mapping."""

    default: LineStyle = Field(default_factory=LineStyle)
    overrides: dict[int, LineStyleOverride] = Field(default_factory=dict)
    color_encoding: ColorEncoding | None = None


class PlotPresentation(StateModel):
    """Visual components displaying a dataset."""

    axes: list[AxisPresentation] = Field(default_factory=list)
    lines: LinePresentation = Field(default_factory=LinePresentation)


class PlotState(StateModel):
    """Validated canonical source of truth, shared by Python and JSON."""

    data: PlotData = Field(default_factory=PlotData)
    presentation: PlotPresentation = Field(default_factory=PlotPresentation)

    @model_validator(mode="after")
    def validate_state(self) -> PlotState:
        rows = self.data.rows
        columns = self.data.columns
        axes = self.presentation.axes
        if rows:
            if len({len(row) for row in rows}) != 1:
                raise ValueError("all rows must have the same length")
            if not rows[0]:
                raise ValueError("data rows must contain at least one value")
            if len(columns) != len(rows[0]):
                raise ValueError("column metadata must match row width")
            if len(axes) != len(rows[0]):
                raise ValueError("number of axes must match row width")
        elif columns or axes:
            raise ValueError("columns and axes cannot be defined without data")

        for index, (column, axis) in enumerate(zip(columns, axes, strict=True)):
            values = [row[index] for row in rows]
            if column.dtype != infer_dtype(values):
                raise ValueError(f"column {index} dtype does not match observations")
            self._validate_axis_data(column, axis, values)

        self._validate_lines()
        return self

    def _validate_axis_data(
        self, column: ColumnSpec, axis: AxisPresentation, values: list[object]
    ) -> None:
        """Check one axis's scale and ticks against its column's observations."""

        scale = axis.scale
        if column.dtype == "numeric":
            if scale.categories is not None:
                raise ValueError("numeric axes cannot define categories")
            if axis.ticks.values is not None and any(
                isinstance(value, str) for value in axis.ticks.values
            ):
                raise ValueError("numeric axes require numeric tick values")
        else:
            if scale.limits != (None, None):
                raise ValueError("categorical axes cannot define numeric limits")
            categories = scale.categories
            observed = {value for value in values if isinstance(value, str)}
            if categories is not None and not observed.issubset(categories):
                raise ValueError(
                    "axis categories must include every observed category"
                )
            allowed = set(categories) if categories is not None else observed
            if axis.ticks.values is not None and any(
                value not in allowed for value in axis.ticks.values
            ):
                raise ValueError(
                    "categorical tick values must reference known categories"
                )

    def _validate_lines(self) -> None:
        """Check line overrides and color encoding against this state's data."""

        lines = self.presentation.lines
        rows = self.data.rows
        for row in lines.overrides:
            if row < 0 or row >= len(rows):
                raise ValueError(f"line style references unknown row index {row}")
        if lines.color_encoding is not None:
            index = lines.color_encoding.axis
            if index < 0 or index >= len(self.data.columns):
                raise ValueError(f"unknown axis index {index}")
            if self.data.columns[index].dtype != "numeric":
                raise ValueError("colorbar encoding only supports numeric axes")
