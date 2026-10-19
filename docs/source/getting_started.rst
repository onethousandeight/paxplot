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

Axis Visibility
---------------

An axis's **spine** is the vertical stroke connecting its tick marks. The spine,
axis title, tick marks, and tick value labels are independently visible. Hiding
them preserves the data dimension, its position, and its scaling.

.. code-block:: python

   plot.set_axis(0, spine_visible=False)  # Keep the title and ticks.
   plot.set_axis(1, tick_marks_visible=False)  # Keep tick value labels.
   plot.set_axis(2, tick_labels_visible=False)  # Keep tick marks.
   plot.set_axis(3, label_visible=False)  # Keep the spine and ticks.

To hide both tick marks and their value labels:

.. code-block:: python

   plot.set_axis(0, tick_marks_visible=False, tick_labels_visible=False)

Set all four visibility flags to ``False`` to hide every decoration of an axis.
All flags default to ``True``; omitted keywords retain their current settings.
Showing a component again restores its retained configuration, including tick
values and labels changed while hidden. These settings are saved in JSON.

An explicit ``ticks=[]`` configures zero ticks on numeric and categorical axes.
Hiding ticks instead retains their configured values for later display.

Appearance is grouped by component in the state: ``AxisConfig.spine_style`` and
``AxisConfig.label_style`` control the spine and title; ``TickConfig.mark_style``
and ``TickConfig.label_style`` control tick marks and value labels. Each style
currently supports ``visible``. These objects leave room for future font, size,
and color controls.

Saving Plot Definitions
-----------------------

PaxPlot serializes the plot definition, not a Matplotlib figure. Save the
definition to JSON and render it again later.

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render()
