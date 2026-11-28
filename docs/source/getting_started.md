# Getting Started

paxplot centers on {class}`paxplot.ParallelPlot`. Create a plot object, set data,
configure axes, then render a Matplotlib figure.

## Installation

```console
$ pip install paxplot
```

## Basic Usage

```{literalinclude} ../../examples/basic_usage.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/basic_usage` gallery example for the rendered
figure and downloadable script.

## Data and Visual Components

`plot.state.data` owns observations in `rows` and inferred column types in
`columns`. Columns and axes match by position. `plot.state.presentation`
owns the axes and line presentation. Each axis has four components:

- `scale` maps values to positions through limits, inversion, and category order.
- `title` owns its text and visibility.
- `ticks` owns reference values and count, plus marks and labels.
- `spine` owns the visibility of the vertical stroke.

For example, `plot.state.data.columns[0].dtype` describes the observations,
while `plot.state.presentation.axes[0].scale.inverted` describes their mapping.

`set_axis()` replaces supplied components; omitted components stay unchanged.
Focused methods such as `set_axis_label()` and `set_axis_limits()` update part
of a component and preserve its other settings. The
{doc}`/auto_examples/advanced_usage` example shows both styles.

## Axis Visibility

The spine, title, tick marks, and tick labels are independently visible. Hiding
a component preserves the data dimension, its position, and its scaling.
Appearance belongs directly to the component, alongside its configuration.

```{literalinclude} ../../examples/axis_visibility.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/axis_visibility` gallery example for the rendered
figure and downloadable script.

## Tick Visibility and Configuration

Supplying a component replaces its configuration. To change visibility while
retaining configured tick values, count, and custom labels, build a validated
replacement from the existing component:

```{literalinclude} ../../examples/axis_ticks.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/axis_ticks` gallery example for the rendered
figure and downloadable script.

`set_axis_ticks()` preserves the count and appearance of the marks and labels.
An explicit `AxisTicks(values=[])` configures zero ticks; `values=None`
selects automatic ticks. Visibility suppresses drawing while retaining values.
Invalid method calls leave the entire plot unchanged.

Calling `set_data()` again rebuilds axes, clears row overrides and color
encoding, and retains the default line style.

## Saving Plot Definitions

paxplot serializes the plot definition, not a Matplotlib figure. Save the
definition to JSON and render it again later.

```{literalinclude} ../../examples/serialization.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/serialization` gallery example for the rendered
figure and downloadable script.

The JSON document has the shape `{"schema_version": 2, "state": ...}`.
The state is serialized directly, including defaults. Loading requires this
envelope and rejects other versions, unversioned documents, and unknown fields
at every level.
