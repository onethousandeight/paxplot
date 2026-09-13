# PaxPlot Design

## Purpose

PaxPlot stores a serializable definition of a parallel coordinate plot and
renders it with matplotlib. Users work with a `ParallelPlot` object that feels
like a normal Python plotting object: set data, configure axes, adjust ticks and
limits, then render or save the plot definition.

The package has three concrete parts:

1. `ParallelPlot`: the public API users interact with.
2. `PlotState`: the validated, serializable plot state.
3. `RenderData`: normalized coordinates and resolved axis information passed to
   matplotlib.

## Example Usage

```python
import paxplot as pax

data = [
    [0.0, "low", 2.0, 0.5],
    [1.0, "medium", 1.0, 1.0],
    [3.0, "high", 0.0, 1.0],
]

plot = pax.ParallelPlot()
plot.set_data(data, columns=["A", "Risk", "C", "D"])
plot.set_axis_label("A", "Column A")
plot.set_axis_limits("A", lower=-1.0, upper=3.0)
plot.set_axis_ticks("Risk", values=["low", "medium", "high"])
plot.invert_axis("C")
plot.set_colorbar("A", palette="viridis", label="Column A")

fig = plot.render()
fig.show()
```

The same plot can be configured more compactly with `set_axis`:

```python
plot = pax.ParallelPlot()
plot.set_data(data, columns=["A", "Risk", "C", "D"])

plot.set_axis(
    "A",
    label="Column A",
    limits=(-1.0, 3.0),
    ticks=[0.0, 1.0, 2.0, 3.0],
)
plot.set_axis(
    "Risk",
    label="Risk",
    categories=["low", "medium", "high"],
)
plot.set_axis("C", inverted=True, tick_count=5)
plot.set_line_style("row-2", color="crimson", width=2.0)

fig = plot.render(figsize=(10, 6))
```

Serialization uses the same plot object:

```python
plot.to_json("plot.json")

restored = pax.ParallelPlot.from_json("plot.json")
fig = restored.render()
```

## Public API

`ParallelPlot` owns a `PlotState` and provides matplotlib-inspired methods for
common edits.

```python
class ParallelPlot:
    def set_data(
        self,
        data,
        columns: list[str] | None = None,
        row_ids: list[str] | None = None,
    ) -> "ParallelPlot": ...

    def set_axis(
        self,
        axis: int | str,
        *,
        label: str | None = None,
        limits: tuple[float | None, float | None] | None = None,
        ticks: list[float | str] | None = None,
        tick_labels: list[str] | None = None,
        tick_count: int | None = None,
        categories: list[str] | None = None,
        inverted: bool | None = None,
    ) -> "ParallelPlot": ...

    def set_axis_label(self, axis: int | str, label: str) -> "ParallelPlot": ...
    def set_axis_limits(
        self,
        axis: int | str,
        lower: float | None = None,
        upper: float | None = None,
    ) -> "ParallelPlot": ...
    def set_axis_ticks(
        self,
        axis: int | str,
        values: list[float | str],
        labels: list[str] | None = None,
    ) -> "ParallelPlot": ...
    def invert_axis(self, axis: int | str, inverted: bool = True) -> "ParallelPlot": ...
    def set_default_line_style(
        self,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
    ) -> "ParallelPlot": ...
    def set_line_style(
        self,
        row_id: str,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
        zorder: float | None = None,
    ) -> "ParallelPlot": ...
    def set_colorbar(
        self,
        axis: int | str,
        *,
        palette: str | list[str] = "viridis",
        label: str | None = None,
        limits: tuple[float | None, float | None] | None = None,
    ) -> "ParallelPlot": ...

    def render(self, **kwargs): ...
    def to_json(self, path: str) -> None: ...

    @classmethod
    def from_json(cls, path: str) -> "ParallelPlot": ...
```

Methods return `self` so users can chain calls when useful:

```python
plot = (
    pax.ParallelPlot()
    .set_data(data, columns=["A", "Risk", "C", "D"])
    .set_axis_label("A", "Column A")
    .invert_axis("C")
)
```

## Core Objects

### PlotState

`PlotState` is the serializable source of truth. It stores column-oriented data,
axis configuration, and plot-level style settings. It should be a Pydantic model
so validation and JSON round trips are built into the package.

```python
class PlotState(BaseModel):
    data: dict[str, list[object]]
    row_ids: list[str]
    axes: list[AxisConfig]
    default_line_style: LineStyle = Field(default_factory=LineStyle)
    line_styles: dict[str, LineStyleOverride] = Field(default_factory=dict)
    color_encoding: ColorEncoding | None = None
```

### AxisConfig

`AxisConfig` stores what an axis means and how it should be displayed.

```python
class AxisConfig(BaseModel):
    name: str
    dtype: Literal["numeric", "categorical"]
    label: str | None = None
    lower: float | None = None
    upper: float | None = None
    inverted: bool = False
    categories: list[str] | None = None
    ticks: TickConfig = Field(default_factory=TickConfig)
```

### TickConfig

`TickConfig` describes tick intent before scaling. It can request automatic ticks
or store explicit tick values and labels.

```python
class TickConfig(BaseModel):
    values: list[float | str] | None = None
    labels: list[str] | None = None
    count: int | None = None
```

### LineStyle

`LineStyle` stores serializable line appearance. `LineStyleOverride` uses the
same fields, but all fields are optional.

```python
class LineStyle(BaseModel):
    color: str | None = None
    alpha: float = 0.7
    width: float = 1.0
    linestyle: str = "-"
    zorder: float | None = None


class LineStyleOverride(BaseModel):
    color: str | None = None
    alpha: float | None = None
    width: float | None = None
    linestyle: str | None = None
    zorder: float | None = None
```

### ColorEncoding

`ColorEncoding` describes line colors generated from one axis. It is plot
intent, not a matplotlib colorbar object.

```python
class ColorEncoding(BaseModel):
    axis: str
    palette: str | list[str] = "viridis"
    lower: float | None = None
    upper: float | None = None
    colorbar: ColorbarConfig = Field(default_factory=ColorbarConfig)


class ColorbarConfig(BaseModel):
    label: str | None = None
```

### RenderData

`RenderData` is produced from `PlotState` immediately before rendering. It stores
normalized line coordinates, resolved tick positions, and labels that matplotlib
can draw directly. Unlike `PlotState`, it is internal render data: it is not
serialized and does not need Pydantic validation. Dense NumPy arrays are used
for line coordinates so rendering thousands of rows does not require building
one Python model per line.

```python
from dataclasses import dataclass

import numpy as np


@dataclass
class RenderAxis:
    name: str
    label: str
    x: float
    tick_positions: list[float]
    tick_labels: list[str]


@dataclass
class RenderColorbar:
    axis: str
    palette: str | list[str]
    label: str | None
    lower: float
    upper: float


@dataclass
class RenderData:
    x: np.ndarray
    y: np.ndarray
    row_ids: list[str]
    axes: list[RenderAxis]
    default_line_style: LineStyle
    line_colors: np.ndarray | None = None
    line_widths: np.ndarray | None = None
    colorbar: RenderColorbar | None = None
```

## Data And Axis Handling

Data is stored by column:

```python
{
    "A": [0.0, 1.0, 3.0],
    "Risk": ["low", "medium", "high"],
    "C": [2.0, 1.0, 0.0],
    "D": [0.5, 1.0, 1.0],
}
```

`set_data` accepts row-oriented data because that is convenient for users, then
converts it to column-oriented state. It should also accept mappings of columns
and pandas DataFrames. If `row_ids` are not supplied, PaxPlot assigns ids like
`row-0`, `row-1`, and `row-2` for the current dataset.

Axis type inference is simple:

- numeric columns contain only `int`, `float`, `None`, or `NaN`;
- categorical columns contain strings, `None`, or repeated labels;
- mixed numeric and string columns raise a validation error.

Numeric axes use `lower` and `upper` when supplied. Missing bounds come from the
column data. Values are scaled with min-max normalization:

```text
scaled = (value - lower) / (upper - lower)
```

Categorical axes use `categories` when supplied. Otherwise categories are ordered
by first appearance in the data. Category positions are evenly spaced between
`0.0` and `1.0`.

Axis inversion is applied after scaling:

```text
scaled = 1.0 - scaled
```

Ticks are resolved during render preparation:

- explicit tick values are scaled onto the axis;
- explicit labels are used when provided;
- categorical ticks default to category labels;
- numeric ticks default to a small set of readable values between the resolved
  lower and upper bounds;
- `tick_count` controls the number of automatic numeric ticks.

Missing values remain missing in `RenderData`, represented as `NaN` values in
the coordinate matrix. The matplotlib renderer should skip or break line
segments where a row has missing coordinates.

## Line Styling And Colorbars

Line style is part of serializable plot state when it changes the meaning of the
plot. Backend-only artist details stay in the renderer.

Users can set a default line style, override individual lines by row id, or call
`set_colorbar(axis)` to color lines from a numeric column. `palette` can be a
named matplotlib colormap or an explicit list of colors.

Style precedence is:

1. default line style;
2. colorbar column encoding;
3. explicit per-line style overrides.

A user-set line color overrides generated colorbar colors for that line.
Categorical palettes can use the same model later, but the first colorbar
implementation is numeric.

## Matplotlib Rendering

`ParallelPlot.render()` prepares `RenderData` and passes it to the matplotlib
renderer. At that point, scaling decisions are complete and the renderer
receives ready-to-draw coordinates.

The matplotlib renderer:

- creates one figure;
- draws vertical axes at the `RenderAxis.x` positions;
- draws normalized line coordinates from the `RenderData.y` matrix;
- prefers a matplotlib `LineCollection` for bulk line drawing instead of
  creating one line artist per row;
- applies each axis's resolved tick positions and labels;
- applies resolved line styles;
- draws a colorbar when `RenderData.colorbar` is present;
- returns a matplotlib `Figure`.

The renderer can use a main axis for line geometry and secondary axes or custom
artists for vertical axes and ticks. That detail stays inside the renderer.

## Implementation Steps

1. Define Pydantic models for `PlotState`, `AxisConfig`, `TickConfig`,
   line styling, and color encoding. Define lightweight render dataclasses for
   `RenderAxis` and `RenderData`.
2. Implement `ParallelPlot` with data loading, axis lookup, setters,
   serialization, and `render()`.
3. Implement render preparation from `PlotState` to `RenderData`.
4. Implement numeric scaling, categorical mapping, inversion, and tick
   resolution.
5. Implement the matplotlib renderer against `RenderData`.
6. Export `ParallelPlot` from `paxplot.__init__`.
7. Add examples that cover basic data, labels, limits, ticks, categorical axes,
   inversion, line styling, colorbars, JSON round trips, and rendering.

## Tooling

PaxPlot uses a small, standard Python toolchain:

- `uv` manages environments, dependency groups, lockfiles, and command
  execution.
- `ruff` handles linting, import sorting, and formatting.
- `pytest` runs the test suite.
- Sphinx builds package documentation with the PyData Sphinx Theme.
- GitHub Actions runs CI, package builds, docs, and releases.
- Dependabot keeps Python dependencies and GitHub Actions updated.

### Documentation

Sphinx remains the documentation tool because PaxPlot is a Python library with
API reference pages, examples, and plotting tutorials. Keep the existing Sphinx
structure, use the PyData Sphinx Theme.

### GitHub Actions

The default workflows should stay lean:

- CI runs on every push and pull request, checking Ruff formatting, Ruff
  linting, and pytest.
- Build creates wheel and source distributions separately from release
  publishing.
- Docs builds Sphinx docs on pull requests and publishes docs to GitHub Pages
  from `main`.
- Release publishes tagged releases to PyPI using Trusted Publishing.
- CodeQL can run as an optional scheduled security analysis for Python and
  workflow files.

Prefer Ubuntu-only CI at first. Add Windows or macOS only if rendering, fonts,
paths, or packaging behavior require it.

### Dependabot

Dependabot should run weekly for `uv` dependencies and `github-actions`, with a
low open PR limit to avoid automation noise.

Delay coverage upload, benchmark workflows, OpenSSF Scorecard, pre-commit CI,
and nox/tox until they solve a real maintenance problem.

## Tests

Schema and state:

- `PlotState` validates equal column lengths.
- `PlotState` validates row ids match data length.
- `ParallelPlot.set_data` accepts row data and produces column data.
- JSON round trips preserve data, row ids, axis config, ticks, style, and
  colorbar config.
- axis lookup works by index and name.

Axis handling:

- numeric columns infer as numeric.
- categorical columns infer as categorical.
- mixed numeric/string columns raise a validation error.
- custom limits affect normalized values.
- inverted axes flip normalized values.
- missing values stay missing.

Ticks:

- explicit numeric ticks scale to normalized positions.
- explicit categorical ticks map to category positions.
- labels must match tick values when provided.
- automatic numeric ticks respect `tick_count`.
- categorical ticks default to category labels.

Line styling and colorbars:

- default line style applies to every line.
- per-line style overrides are resolved by row id.
- `set_colorbar("A", palette="viridis")` resolves one color per row from
  column `A`.
- colorbar limits follow the selected axis unless explicitly provided.
- per-line color overrides generated colorbar color.

Matplotlib rendering:

- `plot.render()` returns a matplotlib `Figure`.
- rendered figures contain one rendered path per complete row.
- axis labels and tick labels match `RenderData`.
- resolved line colors and widths are reflected in the rendered figure.
- colorbar configuration creates a matplotlib colorbar.
- limits, ticks, categorical axes, and inversion are reflected in the rendered
  figure.
