# Contributing

paxplot uses `uv`, `ruff`, `pytest`, and Sphinx.

## Setup

```console
uv sync --extra dev
```

## Tests and lint

```console
uv run pytest
uv run ruff format .
uv run ruff check .
```

## Documentation

Install the docs toolchain alongside the test and lint tools:

```console
uv sync --extra dev --group docs
```

For a docs-only environment, `uv sync --group docs` is enough (that is what CI
uses).

Build the docs exactly as CI does:

```console
uv run sphinx-build -W --keep-going -b html docs/source docs/build/html
```

Open `docs/build/html/index.html` to read the result. For live reload while
writing:

```console
uv run sphinx-autobuild docs/source docs/build/html --open-browser
```

### Where things live

- **Pages** are in `docs/source/` and written in Markdown, with
  reStructuredText retained for the API reference and release notes. Add every
  new page to the toctree in `docs/source/index.md`.
- **Examples** are in `examples/`. Sphinx Gallery executes each script and
  generates `docs/source/auto_examples/` at build time, so edit the scripts and
  never the generated pages. The directory is gitignored. Reference an example
  from a page with `literalinclude`; do not paste its code into the page.
- **API reference** in `docs/source/api.rst` pulls signatures and descriptions
  from the docstrings in `src/paxplot/`. Document new public classes there and
  in the source docstring; a test fails if a name in `paxplot.__all__` is
  missing from `api.rst`.

### Before opening a pull request

The docs build fails on warnings, which catches broken references, missing
images, and examples that no longer run. Run the `-W` command above, and
optionally check external links with:

```console
uv run sphinx-build -b linkcheck docs/source docs/build/linkcheck
```
