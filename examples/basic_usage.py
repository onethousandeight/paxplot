import matplotlib.pyplot as plt

import paxplot as pax

data = [
    [0.0, 2.0, 0.5],
    [1.0, 1.0, 1.0],
    [3.0, 0.0, 1.0],
]

plot = pax.ParallelPlot()
plot.set_data(data)
plot.set_axis_label(0, "A")
plot.set_axis_label(1, "C")
plot.set_axis_label(2, "D")
fig = plot.render(figsize=(8, 4))

plt.show()
