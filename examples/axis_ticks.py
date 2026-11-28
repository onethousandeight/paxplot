"""
Tick Visibility and Configuration
=================================

Retain configured ticks while hiding marks and labels, then update the
reference values and text.
"""

import matplotlib.pyplot as plt

import paxplot as pax

plot = pax.ParallelPlot()
plot.set_data([[0.0, 2.0], [1.0, 1.0], [3.0, 0.0]])
plot.set_axis_ticks(0, values=[0.0, 1.0, 3.0], labels=["Low", "Mid", "High"])

ticks = plot.state.presentation.axes[0].ticks.model_dump()
ticks["marks"]["visible"] = False
ticks["labels"]["visible"] = False
plot.set_axis(0, ticks=pax.AxisTicks(**ticks))
plot.set_axis_ticks(0, values=[0.0, 1.0], labels=["Low", "High"])

fig = plot.render(figsize=(7, 4))
plt.show()
