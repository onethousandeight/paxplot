"""
Font Customization
==================

Reuse a font specification across axis titles, tick labels, and the
colorbar while leaving other text at renderer defaults.
"""

from matplotlib import pyplot as plt

import paxplot as pax

heading = pax.FontSpec(family=["DejaVu Serif", "serif"], size=14, weight="bold")
labels = pax.FontSpec(family="DejaVu Sans Mono", size=9, style="italic")

plot = pax.ParallelPlot().set_data([[0, 10], [1, 20], [4, 15]])
plot.set_axis(
    0,
    title=pax.AxisTitle(text="Revenue", font=heading),
    ticks=pax.AxisTicks(labels=pax.AxisTickLabels(font=labels)),
)
plot.set_axis_label(1, "Cost")  # Uses renderer font defaults.
plot.set_colorbar(
    1,
    title=pax.ColorbarTitle(text="Cost", font=heading),
    ticks=pax.ColorbarTicks(labels=pax.ColorbarTickLabels(font=labels)),
)

fig = plot.render(figsize=(8, 4))
plt.show()
