"""
Pandas DataFrames
=================

Load the trade-off dataset, plot its columns, and add a colorbar.
"""

import matplotlib.pyplot as plt
import pandas as pd

import paxplot as pax
from paxplot import tradeoff

df = pd.read_csv(tradeoff())
columns = df.columns.tolist()

plot = pax.ParallelPlot()
plot.set_data(df[columns].values.tolist())
for index, column in enumerate(columns):
    plot.set_axis_label(index, column)
plot.set_colorbar(0, palette="viridis", title=pax.ColorbarTitle(text=columns[0]))

fig = plot.render(figsize=(6.4, 4.8))
plt.show()
