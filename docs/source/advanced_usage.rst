Advanced Usage
==============

PaxPlot keeps plot intent in serializable state, so advanced edits are still ordinary method calls on :class:`paxplot.ParallelPlot`.

Axis Configuration
------------------

.. code-block:: python

   import paxplot as pax

   data = [
       [0.0, "low", 2.0, 0.5],
       [1.0, "medium", 1.0, 1.0],
       [3.0, "high", 0.0, 1.0],
   ]

   plot = pax.ParallelPlot()
   plot.set_data(data)
   plot.set_axis(
       0,
       title=pax.AxisTitle(text="Column A"),
       scale=pax.AxisScale(limits=(-1.0, 3.0)),
       ticks=pax.AxisTicks(values=[-1.0, 1.0, 3.0]),
   )
   plot.set_axis(
       1,
       title=pax.AxisTitle(text="Risk"),
       scale=pax.AxisScale(categories=["low", "medium", "high"]),
   )
   plot.set_axis(
       2,
       title=pax.AxisTitle(text="C"),
       scale=pax.AxisScale(inverted=True),
       ticks=pax.AxisTicks(count=5),
   )

Omitted components remain unchanged, while supplied components replace their
previous configuration. For example, supplying ``AxisScale(inverted=True)``
also restores automatic limits. To retain limits, call ``invert_axis()`` instead.

Color Encoding
--------------

.. code-block:: python

   plot.set_default_line_style(alpha=0.45, width=1.0)
   plot.set_colorbar(0, palette="viridis", title=pax.ColorbarTitle(text="Column A"))
   plot.set_line_style(2, color="crimson", width=2.5, zorder=10)

Line configuration lives in ``state.presentation.lines``: ``default`` stores
the default appearance, ``overrides`` maps row indices to overrides, and
``color_encoding`` owns its palette and normalization bounds. A colorbar owns
its title as ``color_encoding.colorbar.title`` and tick-label appearance as
``color_encoding.colorbar.ticks.labels``.
Row overrides take precedence over color encoding and the default style.

Font Customization
------------------

Every text component has a ``font`` using the same :class:`paxplot.FontSpec`.
Each property defaults to ``None``, leaving that property to the renderer.
There is no plot-wide font inheritance. A partial specification such as
``FontSpec(weight="bold")`` keeps the renderer's different default sizes for
titles and tick labels.

Font specifications store renderer-neutral intent. Each renderer maps
:class:`paxplot.FontSpec` onto its native text styling and may approximate or
ignore fields it cannot honor, so plot definitions stay portable across
renderers.

.. code-block:: python

   heading = pax.FontSpec(
       family=["DejaVu Serif", "serif"], size=14, weight="bold",
   )
   labels = pax.FontSpec(size=10, style="italic")
   plot.set_axis(
       0,
       title=pax.AxisTitle(text="Column A", font=heading),
       ticks=pax.AxisTicks(labels=pax.AxisTickLabels(font=labels)),
   )
   plot.set_colorbar(
       0,
       title=pax.ColorbarTitle(text="Column A", font=heading),
       ticks=pax.ColorbarTicks(labels=pax.ColorbarTickLabels(font=labels)),
   )

``family`` accepts a name or an ordered fallback list. ``size`` accepts a
positive point size. ``weight`` accepts a common name on the CSS weight scale:
``thin``, ``extra light``, ``light``, ``normal``, ``medium``, ``semibold``,
``bold``, ``extra bold``, or ``black``. ``style`` accepts ``normal``,
``italic``, or ``oblique``. Each renderer resolves available fonts and
fallback families on the machine rendering the plot.

Reusing a ``FontSpec`` supplies independent values to each component; editing
one component does not update the others. ``set_axis_label()`` and
``set_axis_ticks()`` preserve fonts. Supplying a replacement component resets
its unspecified properties; use ``font=FontSpec()`` to clear font overrides.

``set_colorbar()`` replaces supplied title and tick components and preserves
omitted components. Each call uses the supplied palette and limits or their
defaults. Colorbar tick positions and formatting remain automatic. Label fonts
also apply to scientific-notation offset text. To hide labels and offset text
while retaining tick marks, use
``ColorbarTicks(labels=ColorbarTickLabels(visible=False))``.

Fonts use the existing JSON serialization. For example, the title above is
stored at ``state.presentation.axes[0].title`` as:

.. code-block:: json

   {
     "visible": true,
     "font": {
       "family": ["DejaVu Serif", "serif"],
       "size": 14.0,
       "weight": "bold",
       "style": null
     },
     "text": "Column A"
   }

Serialization
-------------

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render(figsize=(10, 6))
