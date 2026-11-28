# paxplot

paxplot stores a serializable definition of a parallel coordinate plot and renders it with Matplotlib. Users configure a {class}`paxplot.ParallelPlot`, save its validated state, and render when they need a figure.

% Rendered from examples/pandas_usage.py during the gallery build.
```{image} auto_examples/images/sphx_glr_pandas_usage_001.svg
:alt: Parallel coordinates plot of the trade-off dataset
```

Parallel coordinates are a common way to visualize high-dimensional data. The
figure above shows the built-in `tradeoff` dataset; the
{doc}`/auto_examples/pandas_usage` example reproduces it.

To install:

```console
$ pip install paxplot
```

## Contents

```{toctree}
:maxdepth: 1

getting_started
advanced_usage
auto_examples/index
api
release
```
