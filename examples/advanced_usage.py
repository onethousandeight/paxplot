import matplotlib.pyplot as plt

import paxplot as pax

data = [
    [0.0, "low", 2.0, 0.5],
    [1.0, "medium", 1.0, 1.0],
    [3.0, "high", 0.0, 1.0],
]

plot = (
    pax.ParallelPlot()
    .set_data(data)
    .set_axis(
        0,
        scale=pax.AxisScale(limits=(-1.0, 3.0)),
        title=pax.AxisTitle(text="Column A"),
        ticks=pax.AxisTicks(values=[-1.0, 1.0, 3.0]),
    )
    .set_axis(
        1,
        scale=pax.AxisScale(categories=["low", "medium", "high"]),
        title=pax.AxisTitle(text="Risk"),
    )
    .set_axis_label(2, "C")
    .invert_axis(2)
    .set_colorbar(0, palette="viridis", title=pax.ColorbarTitle(text="Column A"))
)

fig = plot.render(figsize=(10, 6))
plt.show()
