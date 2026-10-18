import matplotlib.pyplot as plt

import paxplot as pax

data = [[0, 2, 1], [1, 1, 3], [2, 0, 2]]

plot = pax.ParallelPlot()
plot.set_data(data)
plot.set_axis_label(0, "A")
plot.set_axis_label(1, "B")
plot.set_axis_label(2, "C")
plot.set_default_line_style(color="black", alpha=0.4, width=1.25, linestyle="--")
plot.set_line_style(2, color="crimson", alpha=0.9, width=2.5, linestyle="-")

fig = plot.render(figsize=(8, 4))
plt.show()
