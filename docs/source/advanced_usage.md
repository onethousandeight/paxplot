# Advanced Usage

paxplot keeps plot intent in serializable state, so advanced edits are still
ordinary method calls on {class}`paxplot.ParallelPlot`.

## Axis Configuration

```{literalinclude} ../../examples/advanced_usage.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/advanced_usage` gallery example for the rendered
figure and downloadable script.

Omitted components remain unchanged, while supplied components replace their
previous configuration. For example, supplying `AxisScale(inverted=True)`
also restores automatic limits. To retain limits, call `invert_axis()` instead.

## Color Encoding

```{literalinclude} ../../examples/advanced_line_kwargs.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/advanced_line_kwargs` gallery example for the
rendered figure and downloadable script.

Line configuration lives in `state.presentation.lines`: `default` stores the
default appearance, `overrides` maps row indices to overrides, and
`color_encoding` owns its palette and normalization bounds. A colorbar owns its
title as `color_encoding.colorbar.title` and tick-label appearance as
`color_encoding.colorbar.ticks.labels`. Row overrides take precedence over
color encoding and the default style.

## Font Customization

Every text component has a `font` using the same {class}`paxplot.FontSpec`.
Each property defaults to `None`, leaving that property to the renderer. There
is no plot-wide font inheritance. A partial specification such as
`FontSpec(weight="bold")` keeps the renderer's different default sizes for
titles and tick labels.

Font specifications store renderer-neutral intent. Each renderer maps
{class}`paxplot.FontSpec` onto its native text styling and may approximate or
ignore fields it cannot honor, so plot definitions stay portable across
renderers.

```{literalinclude} ../../examples/fonts.py
:language: python
:start-at: import
```

See the {doc}`/auto_examples/fonts` gallery example for the rendered figure and
downloadable script.

`family` accepts a name or an ordered fallback list. `size` accepts a positive
point size. `weight` accepts a common name on the CSS weight scale: `thin`,
`extra light`, `light`, `normal`, `medium`, `semibold`, `bold`, `extra bold`,
or `black`. `style` accepts `normal`, `italic`, or `oblique`. Each renderer
resolves available fonts and fallback families on the machine rendering the
plot.

Reusing a `FontSpec` supplies independent values to each component; editing one
component does not update the others. `set_axis_label()` and
`set_axis_ticks()` preserve fonts. Supplying a replacement component resets its
unspecified properties; use `font=FontSpec()` to clear font overrides.

`set_colorbar()` replaces supplied title and tick components and preserves
omitted components. Each call uses the supplied palette and limits or their
defaults. Colorbar tick positions and formatting remain automatic. Label fonts
also apply to scientific-notation offset text. To hide labels and offset text
while retaining tick marks, use
`ColorbarTicks(labels=ColorbarTickLabels(visible=False))`.

Fonts use the existing JSON serialization. For example, the title above is
stored at `state.presentation.axes[0].title` with `family`, `size`, `weight`,
and `style` fields.

## Serialization

See {doc}`/getting_started` for saving and loading a plot definition.

Saved documents indent nested structure, but each data row is written on a
single line, so observations stay readable and diffs stay small.
