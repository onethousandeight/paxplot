Examples
========

Usage with Pandas
-----------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd

   import paxplot as pax
   from paxplot import tradeoff

   df = pd.read_csv(tradeoff()).head(25)
   columns = df.select_dtypes(include="number").columns[:5].tolist()

   plot = pax.ParallelPlot()
   plot.set_data(df[columns].values.tolist())
   for index, column in enumerate(columns):
       plot.set_axis_label(index, column)
   plot.set_colorbar(0, label=columns[0])

   fig = plot.render(figsize=(11, 5))
   plt.show()

Highlight One Row
-----------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd

   import paxplot as pax
   from paxplot import tradeoff

   df = pd.read_csv(tradeoff()).head(12)
   columns = df.select_dtypes(include="number").columns[:4].tolist()

   plot = pax.ParallelPlot()
   plot.set_data(df[columns].values.tolist())
   for index, column in enumerate(columns):
       plot.set_axis_label(index, column)
   plot.set_default_line_style(color="0.35", alpha=0.25, width=1.0)
   plot.set_line_style(3, color="crimson", alpha=1.0, width=2.5, zorder=10)

   fig = plot.render(figsize=(10, 5))
   plt.show()
