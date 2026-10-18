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
plot.set_axis(1, label="Risk", categories=["low", "medium", "high"])
plot.set_axis(2, label="Region", categories=["north", "west"])

fig = plot.render(figsize=(8, 4))
plt.show()
