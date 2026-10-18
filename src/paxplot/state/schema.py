"""Pydantic schemas for serializable PaxPlot state."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TickConfig(BaseModel):
    """Tick intent before render-time scaling."""

    values: list[float | str] | None = None
    labels: list[str] | None = None
    count: int | None = None

    @field_validator("count")
    @classmethod
    def validate_count(cls, value: int | None) -> int | None:
        if value is not None and value < 2:
            msg = "tick count must be at least 2"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_label_count(self) -> TickConfig:
        if (
            self.values is not None
            and self.labels is not None
            and len(self.values) != len(self.labels)
        ):
            msg = "tick values and labels must have the same length"
            raise ValueError(msg)
        return self


class AxisConfig(BaseModel):
    """Serializable axis configuration."""

    dtype: Literal["numeric", "categorical"]
    label: str | None = None
    lower: float | None = None
    upper: float | None = None
    inverted: bool = False
    categories: list[str] | None = None
    ticks: TickConfig = Field(default_factory=TickConfig)

    @model_validator(mode="after")
    def validate_axis(self) -> AxisConfig:
        if (
            self.lower is not None
            and self.upper is not None
            and self.lower > self.upper
        ):
            msg = "axis lower limit cannot be greater than upper limit"
            raise ValueError(msg)
        if self.dtype == "numeric" and self.categories is not None:
            msg = "numeric axes cannot define categories"
            raise ValueError(msg)
        if self.dtype == "categorical":
            if self.lower is not None or self.upper is not None:
                msg = "categorical axes cannot define numeric limits"
                raise ValueError(msg)
            if self.categories is not None and len(set(self.categories)) != len(
                self.categories
            ):
                msg = "axis categories must be unique"
                raise ValueError(msg)
        return self


class LineStyle(BaseModel):
    """Default serializable line appearance."""

    color: str | None = None
    alpha: float = 0.7
    width: float = 1.0
    linestyle: str = "-"
    zorder: float | None = None

    @field_validator("alpha")
    @classmethod
    def validate_alpha(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            msg = "alpha must be between 0 and 1"
            raise ValueError(msg)
        return value

    @field_validator("width")
    @classmethod
    def validate_width(cls, value: float) -> float:
        if value <= 0:
            msg = "line width must be positive"
            raise ValueError(msg)
        return value


class LineStyleOverride(BaseModel):
    """Optional per-row line appearance overrides."""

    color: str | None = None
    alpha: float | None = None
    width: float | None = None
    linestyle: str | None = None
    zorder: float | None = None

    @field_validator("alpha")
    @classmethod
    def validate_alpha(cls, value: float | None) -> float | None:
        if value is not None and not 0.0 <= value <= 1.0:
            msg = "alpha must be between 0 and 1"
            raise ValueError(msg)
        return value

    @field_validator("width")
    @classmethod
    def validate_width(cls, value: float | None) -> float | None:
        if value is not None and value <= 0:
            msg = "line width must be positive"
            raise ValueError(msg)
        return value


class ColorbarConfig(BaseModel):
    """Display configuration for a rendered colorbar."""

    label: str | None = None


class ColorEncoding(BaseModel):
    """Serializable color encoding intent."""

    axis: int
    palette: str | list[str] = "viridis"
    lower: float | None = None
    upper: float | None = None
    colorbar: ColorbarConfig = Field(default_factory=ColorbarConfig)

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


class PlotState(BaseModel):
    """The validated, serializable source of truth for a PaxPlot."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: list[list[object]] = Field(default_factory=list)
    axes: list[AxisConfig] = Field(default_factory=list)
    default_line_style: LineStyle = Field(default_factory=LineStyle)
    line_styles: dict[int, LineStyleOverride] = Field(default_factory=dict)
    color_encoding: ColorEncoding | None = None

    @model_validator(mode="after")
    def validate_state(self) -> PlotState:
        row_count = len(self.data)
        axis_count = len(self.axes)
        if row_count:
            row_widths = {len(row) for row in self.data}
            if len(row_widths) != 1:
                msg = "all rows must have the same length"
                raise ValueError(msg)
            row_width = next(iter(row_widths))
            if row_width != axis_count:
                msg = "number of axes must match row width"
                raise ValueError(msg)
        elif axis_count:
            msg = "axes cannot be defined without data"
            raise ValueError(msg)

        invalid_rows = [row for row in self.line_styles if row < 0 or row >= row_count]
        if invalid_rows:
            row = sorted(invalid_rows)[0]
            msg = f"line style references unknown row index {row}"
            raise ValueError(msg)

        if self.color_encoding is not None:
            axis_index = self.color_encoding.axis
            if axis_index < 0 or axis_index >= axis_count:
                msg = f"unknown axis index {axis_index}"
                raise ValueError(msg)
            axis = self.axes[axis_index]
            if axis.dtype != "numeric":
                msg = "colorbar encoding only supports numeric axes"
                raise ValueError(msg)
        return self
