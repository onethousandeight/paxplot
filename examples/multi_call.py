import matplotlib.pyplot as plt

import paxplot as pax

plot = pax.ParallelPlot()
plot.set_data([[0, 2], [1, 1], [2, 0]])
plot.set_axis_label(0, "First Axis")
plot.set_axis_limits(1, lower=-1.0, upper=3.0)
plot.invert_axis(1)

fig = plot.render(figsize=(7, 4))
plt.show()
