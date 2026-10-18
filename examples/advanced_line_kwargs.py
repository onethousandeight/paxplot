import matplotlib.pyplot as plt
import pandas as pd

import paxplot as pax
from paxplot import hydroclimate_model_evaluation

df = pd.read_csv(hydroclimate_model_evaluation()).head(20)
columns = df.select_dtypes(include="number").columns[:4].tolist()

plot = pax.ParallelPlot()
plot.set_data(df[columns].values.tolist())
for index, column in enumerate(columns):
    plot.set_axis_label(index, column)
plot.set_default_line_style(alpha=0.35, width=1.0)
plot.set_line_style(0, color="crimson", width=2.5, zorder=10)
plot.set_colorbar(0, label=columns[0])

fig = plot.render(figsize=(10, 5))
plt.show()
