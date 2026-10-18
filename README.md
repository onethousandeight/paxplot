[![PyPI](https://img.shields.io/pypi/v/paxplot)](https://pypi.org/project/paxplot/)
[![GitHub license](https://img.shields.io/github/license/kravitsjacob/paxplot)](https://github.com/kravitsjacob/paxplot/blob/main/LICENSE)

# PaxPlot

PaxPlot stores a serializable definition of a parallel coordinate plot and renders it with matplotlib.

```python
import paxplot as pax

plot = pax.ParallelPlot()
plot.set_data([[0.0, "low", 2.0], [1.0, "medium", 1.0], [3.0, "high", 0.0]])
plot.set_axis(0, label="A")
plot.set_axis(1, label="Risk", categories=["low", "medium", "high"])
plot.set_axis(2, label="C")
plot.set_colorbar(0, label="Column A")

fig = plot.render()
```

## Installation

```console
pip install paxplot
```

## Reporting Bugs

Please report all bugs using [issues](https://github.com/kravitsjacob/paxplot/issues).

## Contributing

PaxPlot uses `uv`, `ruff`, `pytest`, and Sphinx.

```console
uv sync --extra dev --extra docs
uv run ruff format .
uv run ruff check .
uv run pytest
```
