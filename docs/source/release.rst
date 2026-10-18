Release Notes
=============

Version 0.2.0
-------------

PaxPlot has been redesigned around a clean, serializable plot model:

* :class:`paxplot.ParallelPlot` is the public plotting object.
* :class:`paxplot.PlotState` stores validated plot intent.
* Render preparation produces internal ``RenderData`` for Matplotlib.
* The package structure now follows the plot, state, and rendering model.
* Legacy compatibility APIs have been removed.

The core workflow is:

.. code-block:: python

   import paxplot as pax

   plot = pax.ParallelPlot()
   plot.set_data([[0.0, "low"], [1.0, "high"]])
   plot.set_axis(0, label="A")
   plot.set_axis(1, label="Risk", categories=["low", "high"])
   plot.set_colorbar(0)
   fig = plot.render()
