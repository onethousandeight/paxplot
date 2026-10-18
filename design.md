# PaxPlot Design

## Purpose

The project name is **PaxPlot**, with a capital `P` at the start and a second
capital `P` in `Plot`. Use **PaxPlot** in prose, documentation headings,
release notes, and user-facing text. Reserve lowercase `paxplot` for the Python
package name, import paths, module paths, and filesystem paths.

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
plot.set_data(data)
plot.set_axis_label(0, "Column A")
plot.set_axis_limits(0, lower=-1.0, upper=3.0)
plot.set_axis_ticks(1, values=["low", "medium", "high"])
plot.invert_axis(2)
plot.set_colorbar(0, palette="viridis", label="Column A")

fig = plot.render()
fig.show()
```

The same plot can be configured more compactly with `set_axis`:

```python
plot = pax.ParallelPlot()
plot.set_data(data)

plot.set_axis(
    0,
    label="Column A",
    limits=(-1.0, 3.0),
    ticks=[0.0, 1.0, 2.0, 3.0],
)
plot.set_axis(
    1,
    label="Risk",
    categories=["low", "medium", "high"],
)
plot.set_axis(2, label="C", inverted=True, tick_count=5)
plot.set_line_style(2, color="crimson", width=2.0)

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
    def set_data(self, data) -> "ParallelPlot": ...

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
    ) -> "ParallelPlot": ...

    def set_axis_label(self, axis: int, label: str) -> "ParallelPlot": ...
    def set_axis_limits(
        self,
        axis: int,
        lower: float | None = None,
        upper: float | None = None,
    ) -> "ParallelPlot": ...
    def set_axis_ticks(
        self,
        axis: int,
        values: list[float | str],
        labels: list[str] | None = None,
    ) -> "ParallelPlot": ...
    def invert_axis(self, axis: int, inverted: bool = True) -> "ParallelPlot": ...
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
        row: int,
        *,
        color: str | None = None,
        alpha: float | None = None,
        width: float | None = None,
        linestyle: str | None = None,
        zorder: float | None = None,
    ) -> "ParallelPlot": ...
    def set_colorbar(
        self,
        axis: int,
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
plot = pax.ParallelPlot().set_data(data).set_axis_label(0, "Column A").invert_axis(2)
```

## Core Objects

### PlotState

`PlotState` is the serializable source of truth. It stores row-oriented data,
axis configuration, and plot-level style settings. It should be a Pydantic model
so validation and JSON round trips are built into the package.

```python
class PlotState(BaseModel):
    data: list[list[object]]
    axes: list[AxisConfig]
    default_line_style: LineStyle = Field(default_factory=LineStyle)
    line_styles: dict[int, LineStyleOverride] = Field(default_factory=dict)
    color_encoding: ColorEncoding | None = None
```

### AxisConfig

`AxisConfig` stores what an axis means and how it should be displayed.

```python
class AxisConfig(BaseModel):
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
    axis: int
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
    label: str
    x: float
    tick_positions: list[float]
    tick_labels: list[str]


@dataclass
class RenderColorbar:
    axis: int
    palette: str | list[str]
    label: str | None
    lower: float
    upper: float


@dataclass
class RenderData:
    x: np.ndarray
    y: np.ndarray
    axes: list[RenderAxis]
    default_line_style: LineStyle
    line_colors: np.ndarray | None = None
    line_widths: np.ndarray | None = None
    colorbar: RenderColorbar | None = None
```

## Data And Axis Handling

Data is stored by row:

```python
[
    [0.0, "low", 2.0, 0.5],
    [1.0, "medium", 1.0, 1.0],
    [3.0, "high", 0.0, 1.0],
]
```

`set_data` accepts only non-empty rectangular row-oriented data. Users address
axes and rows by integer position. Axis labels are display metadata, not lookup
keys.

Axis type inference is simple:

- numeric axes contain only `int`, `float`, `None`, or `NaN`;
- categorical axes contain strings, `None`, or repeated labels;
- mixed numeric and string axes raise a validation error.

Numeric axes use `lower` and `upper` when supplied. Missing bounds come from the
axis data. Values are scaled with min-max normalization:

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

Users can set a default line style, override individual lines by row index, or call
`set_colorbar(axis)` to color lines from a numeric axis. `palette` can be a
named matplotlib colormap or an explicit list of colors.

Style precedence is:

1. default line style;
2. colorbar axis encoding;
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

## File Organization

The redesigned package should use an idiomatic structure that follows the plot,
state, and rendering mental model:

```text
src/paxplot/
  __init__.py
  plot.py

  state/
    __init__.py
    schema.py
    serialization.py

  rendering/
    __init__.py
    data.py
    prepare.py
    matplotlib.py
    _scaling.py
    _ticks.py
    _styles.py

  datasets.py
  data/
    tradeoff.csv
    hydroclimate_model_evaluation.csv
```

`plot.py` owns `ParallelPlot`, the public user-facing object. `state/` owns
validated, serializable plot intent: `PlotState`, axis configuration, ticks,
styles, and color encoding. `rendering/` owns derived backend-ready data, render
preparation, and matplotlib drawing.

Private rendering helpers use leading underscores because they support the
rendering pipeline rather than define the public architecture. Avoid broad
buckets like `model`, `core`, `structures`, `views`, or `utils`.


## Tooling

PaxPlot uses a small, standard Python toolchain:

- `uv` manages environments, dependency groups, lockfiles, and command
  execution.
- `ruff` handles linting, import sorting, and formatting.
- `pytest` runs the test suite, with `syrupy` for structured snapshot tests.
- Sphinx builds package documentation using the current docs theme.
- GitHub Actions runs CI, package builds, docs, and releases.

### Documentation

Sphinx remains the documentation tool because PaxPlot is a Python library with
API reference pages, examples, and plotting tutorials. Keep the existing Sphinx
structure and current documentation theme.

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

Prefer Ubuntu-only CI at first. For this implementation just make the pipeline yamls, you don't need to actually connect to github to run the actions

Delay coverage upload, benchmark workflows, OpenSSF Scorecard, pre-commit CI,
and nox/tox until they solve a real maintenance problem.

## Tests

Use many focused unit tests for core behavior and a few trusted integration
tests for typical user workflows. New tests should live in `tests/`; legacy
compatibility tests do not constrain this redesign.

Unit tests should cover validation, data loading, axis configuration, dtype inference,
normalization, categorical mapping, missing values, limits, inversion, tick
resolution, line style precedence, colorbar resolution, JSON round trips, and
thin matplotlib renderer behavior.

Integration tests should use `syrupy` snapshots of structured `PlotState` and
`RenderData` summaries. Do not snapshot rendered images by default; assert
targeted matplotlib objects instead, such as returned `Figure` instances, axis
labels, tick labels, line collections, line styles, and colorbars.

Keep the initial integration suite to three workflows:

- mixed numeric and categorical axes with labels, limits, ticks, inversion, and
  missing values;
- default line styling, numeric colorbar encoding, and one explicit row style
  override;
- configured plot serialized to JSON, loaded back, summarized, and rendered.
