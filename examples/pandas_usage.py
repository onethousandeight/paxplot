import matplotlib.pyplot as plt
import pandas as pd

import paxplot as pax
from paxplot import hydroclimate_model_evaluation

df = pd.read_csv(hydroclimate_model_evaluation()).head(25)
columns = df.select_dtypes(include="number").columns[:5].tolist()

plot = pax.ParallelPlot()
plot.set_data(df[columns].values.tolist())
for index, column in enumerate(columns):
    plot.set_axis_label(index, column)
plot.set_colorbar(0, label=columns[0])

fig = plot.render(figsize=(11, 5))
plt.show()
