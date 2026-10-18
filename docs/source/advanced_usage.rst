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
       label="Column A",
       limits=(-1.0, 3.0),
       ticks=[-1.0, 1.0, 3.0],
   )
   plot.set_axis(1, label="Risk", categories=["low", "medium", "high"])
   plot.set_axis(2, label="C", inverted=True, tick_count=5)

Color Encoding
--------------

.. code-block:: python

   plot.set_default_line_style(alpha=0.45, width=1.0)
   plot.set_colorbar(0, palette="viridis", label="Column A")
   plot.set_line_style(2, color="crimson", width=2.5, zorder=10)

Serialization
-------------

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render(figsize=(10, 6))
