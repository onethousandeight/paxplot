"""
Categorical Axes
================

Map string columns onto ordered categories instead of numeric scales.
"""

import matplotlib.pyplot as plt

import paxplot as pax

data = [
    [0.0, "low", "north"],
    [0.5, "medium", "west"],
    [1.0, "high", "north"],
]

plot = pax.ParallelPlot()
plot.set_data(data)
plot.set_axis_label(0, "Score")
plot.set_axis(
    1,
    scale=pax.AxisScale(categories=["low", "medium", "high"]),
    title=pax.AxisTitle(text="Risk"),
)
plot.set_axis(
    2,
    scale=pax.AxisScale(categories=["north", "west"]),
    title=pax.AxisTitle(text="Region"),
)

fig = plot.render(figsize=(8, 4))
plt.show()
