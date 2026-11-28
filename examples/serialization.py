"""
Saving Plot Definitions
=======================

Serialize the plot definition to JSON and render the restored plot.
"""

import matplotlib.pyplot as plt

import paxplot as pax

plot = pax.ParallelPlot()
plot.set_data([[0.0, "low", 2.0], [1.0, "medium", 1.0], [3.0, "high", 0.0]])
plot.set_axis_label(0, "A")
plot.set_axis(
    1,
    title=pax.AxisTitle(text="Risk"),
    scale=pax.AxisScale(categories=["low", "medium", "high"]),
)
plot.set_axis_label(2, "C")
plot.set_colorbar(0, title=pax.ColorbarTitle(text="Column A"))

plot.to_json("plot.json")
restored = pax.ParallelPlot.from_json("plot.json")

fig = restored.render(figsize=(10, 6))
plt.show()
