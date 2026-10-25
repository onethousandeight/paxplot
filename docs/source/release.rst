Release Notes
=============

Version 0.2.0
-------------

PaxPlot has been redesigned around a clean, serializable plot model:

* :class:`paxplot.ParallelPlot` is the public plotting object.
* :class:`paxplot.PlotState` stores validated plot intent.
* Render preparation produces internal ``RenderData`` for Matplotlib.
* The package structure now follows the plot, state, and rendering model.
* Data owns inferred column types; presentation owns axes and lines.
* Axis scale, title, ticks, and spine each own configuration and appearance.
* ``set_axis()`` accepts component replacements; focused setters preserve other settings.
* State JSON requires a version 2 envelope and rejects obsolete or unknown fields.
* Legacy compatibility APIs have been removed.

The core workflow is:

.. code-block:: python

   import paxplot as pax

   plot = pax.ParallelPlot()
   plot.set_data([[0.0, "low"], [1.0, "high"]])
   plot.set_axis_label(0, "A")
   plot.set_axis(
       1,
       title=pax.AxisTitle(text="Risk"),
       scale=pax.AxisScale(categories=["low", "high"]),
   )
   plot.set_colorbar(0)
   fig = plot.render()
