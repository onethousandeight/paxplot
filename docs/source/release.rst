Release Notes
=============

Version 1.0.0
-------------

paxplot 1.0.0 is the first stable release. The public API described in
:doc:`api`, the serializable plot definition, the rendering workflow, and the
JSON schema envelope are now covered by semantic versioning.

Documentation
^^^^^^^^^^^^^

* Sources are written in Markdown, with reStructuredText retained where
  directives require it.
* Examples are executed during the documentation build and published as a
  gallery with rendered figures.
* API pages cross-reference NumPy, Matplotlib, pandas, and pydantic.
* The documentation build fails on warnings, including broken references and
  examples that no longer run.

Version 0.2.0
-------------

paxplot has been redesigned around a clean, serializable plot model:

* :class:`paxplot.ParallelPlot` is the public plotting object.
* :class:`paxplot.PlotState` stores validated plot intent.
* Render preparation produces internal ``RenderData`` for Matplotlib.
* The package structure now follows the plot, state, and rendering model.
* Data owns inferred column types; presentation owns axes and lines.
* Axis scale, title, ticks, and spine each own configuration and appearance.
* ``set_axis()`` accepts component replacements; focused setters preserve other
  settings.
* State JSON requires a version 2 envelope and rejects obsolete or unknown
  fields.
* Legacy compatibility APIs have been removed.

The core workflow is shown in :doc:`getting_started` and the
:doc:`/auto_examples/index` gallery.
