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
   plot.set_colorbar(0, palette="viridis", title=pax.ColorbarTitle(text="Column A"))

   fig = plot.render(figsize=(10, 6))

Data and Visual Components
--------------------------

``plot.state.data`` owns observations in ``rows`` and inferred column types in
``columns``. Columns and axes match by position. ``plot.state.presentation``
owns the axes and line presentation. Each axis has four components:

* ``scale`` maps values to positions through limits, inversion, and category order.
* ``title`` owns its text and visibility.
* ``ticks`` owns reference values and count, plus marks and labels.
* ``spine`` owns the visibility of the vertical stroke.

For example, ``plot.state.data.columns[0].dtype`` describes the observations,
while ``plot.state.presentation.axes[0].scale.inverted`` describes their mapping.

``set_axis()`` replaces supplied components; omitted components stay unchanged.
Focused methods update part of a component and preserve its other settings:

.. code-block:: python

   plot.set_axis(
       0,
       title=pax.AxisTitle(text="Score", visible=False),
       scale=pax.AxisScale(limits=(-1.0, 3.0), inverted=True),
   )
   plot.set_axis_label(0, "Updated score")  # The title remains hidden.
   plot.set_axis_limits(0, lower=-2.0, upper=4.0)  # Inversion remains enabled.

Axis Visibility
---------------

The spine, title, tick marks, and tick labels are independently visible. Hiding
a component preserves the data dimension, its position, and its scaling.
Appearance belongs directly to the component, alongside its configuration.

.. code-block:: python

   plot.set_axis(0, spine=pax.AxisSpine(visible=False))
   plot.set_axis(1, ticks=pax.AxisTicks(marks=pax.AxisTickMarks(visible=False)))
   plot.set_axis(2, ticks=pax.AxisTicks(labels=pax.AxisTickLabels(visible=False)))
   plot.set_axis(3, title=pax.AxisTitle(text="Hidden title", visible=False))

These calls replace the supplied components, including their configuration. To
change visibility while retaining configured tick values, count, and custom
labels, build a validated replacement from the existing component:

.. code-block:: python

   ticks = plot.state.presentation.axes[0].ticks.model_dump()
   ticks["marks"]["visible"] = False
   ticks["labels"]["visible"] = False
   plot.set_axis(0, ticks=pax.AxisTicks(**ticks))
   plot.set_axis_ticks(0, values=[0.0, 1.0], labels=["Low", "High"])

``set_axis_ticks()`` preserves the count and appearance of the marks and labels.
An explicit ``AxisTicks(values=[])`` configures zero ticks; ``values=None``
selects automatic ticks. Visibility suppresses drawing while retaining values.
Invalid method calls leave the entire plot unchanged.

Calling ``set_data()`` again rebuilds axes, clears row overrides and color
encoding, and retains the default line style.

Saving Plot Definitions
-----------------------

PaxPlot serializes the plot definition, not a Matplotlib figure. Save the
definition to JSON and render it again later.

.. code-block:: python

   plot.to_json("plot.json")
   restored = pax.ParallelPlot.from_json("plot.json")
   fig = restored.render()

The JSON document has the shape ``{"schema_version": 2, "state": ...}``.
The state is serialized directly, including defaults. Loading requires this
envelope and rejects other versions, unversioned documents, and unknown fields
at every level.
