Getting Started
===============

PaxPlot centers on :class:`paxplot.ParallelPlot`. Create a plot object, set data,
configure axes, then render a Matplotlib figure.

Installation
------------

.. code-block:: console

   $ pip install paxplot

Basic Usage
-----------

.. code-block:: python

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

   fig = plot.render(figsize=(10, 6))

Saving Plot Definitions
-----------------------

PaxPlot serializes the plot definition, not a Matplotlib figure. Save the
definition to JSON and render it again later.

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render()
