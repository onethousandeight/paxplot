# PaxPlot Schema-First Design

## Overview

PaxPlot should be a Python library for describing, transforming, and rendering
parallel coordinate plots. The core package should not be a matplotlib extension.
Instead, the core should define a backend-neutral plot schema that users can
manipulate in familiar Python ways, serialize to disk, and render through one of
several possible rendering backends.

Matplotlib should be the first renderer, but not the design center. A future
Plotly, SVG, browser, or Rust-backed renderer should be able to consume the same
plot description after it has been compiled into render-ready coordinates.

The main data flow is:

```text
user data + configuration
        |
        v
ParallelPlotSpec  <---->  JSON / dict serialization
        |
        v
compiler
        |
        v
CompiledParallelPlot
        |
        v
MatplotlibRenderer / future renderers
```

## Goals

- Provide a clear, serializable schema for parallel coordinate plots.
- Keep data, plot intent, scaling, and rendering responsibilities separate.
- Support large in-memory datasets without unnecessary row/object duplication.
- Make matplotlib rendering a backend adapter, not part of the core model.
- Preserve a path for future renderers and a possible Rust or Arrow-backed
  compilation layer.

## Non-Goals For The First Redesign

- Streaming or out-of-core data.
- A Rust backend in v1.
- Perfect compatibility with every direct matplotlib mutation allowed by the
  legacy `PaxFigure` API.
- A full grammar for every visual styling option matplotlib supports.

## User-Facing Shape

The user should interact with a normal Python object that feels like a plot
definition. It should accept common Python, NumPy, and pandas-shaped inputs, but
store the result as a validated schema.

### Basic Usage

```python
import paxplot as pax

data = [
    [0.0, "low", 2.0, 0.5],
    [1.0, "medium", 1.0, 1.0],
    [3.0, "high", 0.0, 1.0],
]

plot = pax.ParallelPlot.from_rows(
    data,
    columns=["A", "Risk", "C", "D"],
)

fig = plot.render("matplotlib")
fig.show()
```

### Axis Configuration

```python
plot = (
    pax.ParallelPlot.from_rows(data, columns=["A", "Risk", "C", "D"])
    .axis("A").limits(-1.0, 3.0).done()
    .axis("Risk").categorical_order(["low", "medium", "high"]).done()
    .axis("C").invert().ticks(count=5).done()
)

fig = plot.render("matplotlib", figsize=(10, 6))
```

### Custom Ticks

```python
plot.axis("A").ticks(
    values=[0.0, 1.0, 2.0, 3.0],
    labels=["zero", "one", "two", "three"],
)
```

### Serialization

```python
plot = pax.ParallelPlot.from_dataframe(df)
plot.axis("cost").invert()
plot.axis("quality").limits(0, 100)

json_text = plot.model_dump_json(indent=2)
restored = pax.ParallelPlot.model_validate_json(json_text)

fig = restored.render("matplotlib")
```

The exact method names can evolve, but the important design point is that the
object a user manipulates is the same object they can validate and serialize.

## Core Architecture

### Schema Layer

The schema layer contains only plot intent. It should not import matplotlib.
Pydantic is a good fit because it gives the package validation, defaults,
JSON-schema generation, and reliable round trips through `dict` and JSON.

Core schema objects:

```python
from typing import Literal
from pydantic import BaseModel, Field


class DataSpec(BaseModel):
    orientation: Literal["columns"] = "columns"
    columns: dict[str, list[object]]


class TickSpec(BaseModel):
    mode: Literal["auto", "manual"] = "auto"
    count: int | None = None
    values: list[float | str] | None = None
    labels: list[str] | None = None


class AxisSpec(BaseModel):
    name: str
    dtype: Literal["numeric", "categorical"]
    label: str | None = None
    limits: tuple[float | None, float | None] | None = None
    inverted: bool = False
    category_order: list[str] | None = None
    ticks: TickSpec = Field(default_factory=TickSpec)


class LineStyleSpec(BaseModel):
    color: str | None = None
    alpha: float = 0.7
    width: float = 1.0


class ParallelPlotSpec(BaseModel):
    data: DataSpec
    axes: list[AxisSpec]
    line_style: LineStyleSpec = Field(default_factory=LineStyleSpec)
```

This is an illustrative shape, not final implementation code. The important
contract is that raw data, axis definitions, tick policy, and style intent are
plain schema data.

### Builder Layer

A small user-facing wrapper can make the schema pleasant to work with. It should
mutate or replace the underlying `ParallelPlotSpec`, but should not become the
authoritative model itself.

Examples:

```python
plot = pax.ParallelPlot.from_dataframe(df)
plot.axis("temperature").label("Temperature").limits(-20, 45)
plot.axis("score").invert()
plot.to_json("plot.json")
```

The wrapper should stay thin:

- Build schemas from rows, columns, NumPy arrays, and pandas DataFrames.
- Provide ergonomic methods for common edits.
- Delegate validation and serialization to Pydantic models.
- Delegate render preparation to the compiler.

### Compiler Layer

The compiler converts plot intent into immutable render-ready data. This is
where scaling, category encoding, limit resolution, tick generation, and color
mapping happen.

The compiler should produce a backend-neutral snapshot:

```python
class CompiledAxis(BaseModel):
    name: str
    label: str
    dtype: str
    coordinate: float
    normalized_ticks: list[float]
    tick_labels: list[str]
    raw_limits: tuple[float | str | None, float | str | None]


class CompiledParallelPlot(BaseModel):
    x: list[float]
    y: list[list[float]]
    axes: list[CompiledAxis]
    line_colors: list[str] | None = None
    line_alpha: float
    line_width: float
```

Responsibilities:

- Infer or confirm column types.
- Store data column-wise and avoid per-row object wrappers.
- Normalize numeric values into `[0.0, 1.0]`.
- Encode categorical values into stable numeric positions.
- Apply custom limits before normalization.
- Apply axis inversion after normalization.
- Resolve tick policies into normalized tick positions and string labels.
- Produce deterministic output independent of matplotlib.

The compiler is the natural future boundary for acceleration. A later Rust
backend could implement this layer while preserving the Python schema and
renderer APIs.

### Renderer Layer

Renderers consume `CompiledParallelPlot`. They should not decide semantic plot
behavior such as category ordering, numeric limits, or whether an axis is
inverted. They are responsible for drawing.

The first renderer should be matplotlib:

```python
compiled = pax.compile(plot.spec)
fig = pax.renderers.MatplotlibRenderer().render(compiled)
```

Renderer responsibilities:

- Create figure and axes.
- Draw vertical axes at compiled x positions.
- Draw lines using compiled normalized y values.
- Apply compiled tick positions and labels.
- Apply labels, line styles, legends, and colorbars.
- Return a normal matplotlib `Figure`.

This keeps matplotlib-specific mechanics in one place while the plot definition
remains portable.

## Data Model

PaxPlot should store data column-wise because parallel coordinate plots are
axis-oriented. Most operations need column min/max, categorical levels, column
ticks, and column normalization.

Input adapters should accept:

- Rows: `Sequence[Sequence[object]]`
- Columns: `Mapping[str, Sequence[object]]`
- pandas `DataFrame`
- NumPy arrays with supplied or generated column names

The schema may serialize data as JSON-compatible column lists. Internally, the
builder or compiler can use NumPy arrays for efficient computation, but the
schema itself should remain portable.

### Missing Values

Missing values should be represented consistently before compilation.

Initial policy:

- Numeric `None` and `NaN` are missing.
- Categorical `None` is missing.
- Missing values compile to `None` or `NaN` in normalized coordinates.
- The matplotlib renderer should break or skip line segments with missing
  coordinates rather than inventing a category or numeric value.

## Axis And Tick Design

Ticks should be declarative in the schema and concrete in compiled output.

Schema examples:

```python
TickSpec(mode="auto", count=6)
TickSpec(mode="manual", values=[0, 50, 100])
TickSpec(mode="manual", values=[0, 1, 2], labels=["low", "mid", "high"])
```

The schema should not depend on `matplotlib.ticker.MaxNLocator`. A backend-neutral
tick resolver can start simple:

- Numeric auto ticks use a small "nice number" algorithm.
- Numeric manual ticks preserve supplied values and labels.
- Categorical auto ticks use category order.
- Categorical manual ticks validate that supplied categories exist.

Matplotlib renderers may later expose an optional renderer-specific locator
mode, but that should be an extension rather than the default schema behavior.

## Matplotlib Rendering Strategy

Matplotlib rendering is nontrivial because a parallel coordinate plot is not a
standard single-axis chart. The renderer should treat the compiled plot as a
normalized coordinate system:

- x positions are axis indices or evenly spaced normalized positions.
- y positions are normalized values in `[0.0, 1.0]`.
- every vertical axis receives its own tick labels from compiled output.
- lines are plotted across the shared normalized coordinate space.

The renderer can use one main axis for the line geometry and secondary/twin axes
or custom artists for per-axis ticks. This decision belongs entirely inside the
matplotlib renderer and should not leak into the schema.

## Public API Sketch

```python
import paxplot as pax

plot = pax.ParallelPlot.from_dataframe(df)

plot.axis("cost").label("Cost").invert()
plot.axis("region").categorical_order(["west", "central", "east"])
plot.axis("score").ticks(count=7)

plot.line_style(color="#3366cc", alpha=0.3, width=0.8)

plot.to_json("plot.json")
fig = plot.render("matplotlib")
```

Lower-level users can bypass the builder:

```python
spec = pax.ParallelPlotSpec.model_validate(payload)
compiled = pax.compile(spec)
fig = pax.renderers.MatplotlibRenderer().render(compiled)
```

## Package Layout

```text
src/paxplot/
    __init__.py
    schema/
        __init__.py
        plot.py
        axis.py
        ticks.py
        style.py
    builders/
        __init__.py
        parallel_plot.py
    compile/
        __init__.py
        compiler.py
        normalize.py
        ticks.py
        categorical.py
    renderers/
        __init__.py
        base.py
        matplotlib.py
    legacy/
        ...
```

The existing `legacy` package can remain available during migration. New code
should not import from legacy modules.

## Migration Plan

1. Add schema models and serialization tests.
2. Add builders for rows, columns, NumPy arrays, and pandas DataFrames.
3. Implement the compiler for numeric and categorical columns.
4. Implement backend-neutral tick resolution.
5. Build `MatplotlibRenderer` against compiled fixtures.
6. Add compatibility examples that recreate current docs: basic plots, labels,
   custom ticks, limits, inversion, legend, colorbar, and categorical data.
7. Keep `pax_parallel` and `PaxFigure` as legacy exports while introducing the
   new schema-first API as the preferred path.
8. Deprecate direct matplotlib-coupled APIs only after the new renderer covers
   the important existing workflows.

## Testing Strategy

Schema tests:

- Validate minimal numeric plot specs.
- Validate mixed numeric and categorical plot specs.
- Round-trip specs through JSON.
- Reject mismatched column lengths.
- Reject invalid axis references and duplicate axis names.

Compiler tests:

- Numeric min/max normalization.
- Custom limits.
- Inverted axes.
- Single-value numeric columns.
- Categorical ordering.
- Missing values.
- Auto and manual tick resolution.

Renderer tests:

- Render from compiled fixtures.
- Verify matplotlib output has expected number of axes, lines, ticks, and labels.
- Verify custom limits, inversion, and categorical ticks appear correctly.
- Verify large in-memory data renders without per-row schema objects.

Migration tests:

- Recreate current examples from `docs/source/getting_started.rst`.
- Recreate advanced examples for labels, limits, custom ticks, inversion,
  legends, colorbars, and categorical axes.

## Future Extensions

- Plotly renderer.
- SVG/static vector renderer.
- Interactive browser renderer.
- Arrow-backed column storage.
- Rust compiler for normalization and tick preparation.
- Streaming/downsampled rendering for very large datasets.
- Rich selection/highlighting schema.
- Faceting or grouped parallel coordinate plots.

## Design Principle To Preserve

PaxPlot should make the hard part explicit: a parallel coordinate plot is a
schema plus a coordinate compilation problem. Matplotlib is one way to draw the
result. Keeping that boundary clean is what will let the package grow without
tying every design decision to a single rendering library.
