[![PyPI](https://img.shields.io/pypi/v/paxplot)](https://pypi.org/project/paxplot/)
[![CI](https://img.shields.io/github/actions/workflow/status/onethousandeight/paxplot/ci.yml?branch=main)](https://github.com/onethousandeight/paxplot/actions/workflows/ci.yml)
[![GitHub license](https://img.shields.io/github/license/onethousandeight/paxplot)](https://github.com/onethousandeight/paxplot/blob/main/LICENSE)

# paxplot

paxplot stores a serializable definition of a parallel coordinate plot and renders it with matplotlib.

Check out our [homepage](https://docs.paxplot.org) for more information.

```python
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

fig = plot.render()
```

## Installation

```console
pip install paxplot
```

For additional installation instructions, see the [Getting Started](https://docs.paxplot.org/getting_started.html) documentation.

## Reporting Bugs

Please report all bugs using [issues](https://github.com/onethousandeight/paxplot/issues).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, and instructions for
building the documentation locally.
