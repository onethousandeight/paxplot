"""
Axis Visibility
===============

Hide the spine, tick marks, tick labels, and title independently.
"""

import matplotlib.pyplot as plt

import paxplot as pax

data = [
    [0.0, 2.0, 1.0, 3.0],
    [1.0, 1.0, 2.0, 2.0],
    [3.0, 0.0, 3.0, 0.0],
]

plot = pax.ParallelPlot()
plot.set_data(data)
plot.set_axis(0, spine=pax.AxisSpine(visible=False))
plot.set_axis(1, ticks=pax.AxisTicks(marks=pax.AxisTickMarks(visible=False)))
plot.set_axis(2, ticks=pax.AxisTicks(labels=pax.AxisTickLabels(visible=False)))
plot.set_axis(3, title=pax.AxisTitle(text="Hidden title", visible=False))

fig = plot.render(figsize=(8, 4))
plt.show()
