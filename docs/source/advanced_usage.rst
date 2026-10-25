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
   plot.set_colorbar(0, palette="viridis", label="Column A")
   plot.set_line_style(2, color="crimson", width=2.5, zorder=10)

Line configuration lives in ``state.presentation.lines``: ``default`` stores
the default appearance, ``overrides`` maps row indices to overrides, and
``color_encoding`` owns its palette and normalization bounds. A colorbar owns
its title as ``color_encoding.colorbar.title`` with ``text`` and ``visible``.
Row overrides take precedence over color encoding and the default style.

Serialization
-------------

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render(figsize=(10, 6))
