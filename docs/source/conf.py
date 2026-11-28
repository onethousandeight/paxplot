# Configuration file for the Sphinx documentation builder.
#
# For the full list of options see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import date
from functools import partial
from importlib import metadata

from sphinx_gallery.scrapers import matplotlib_scraper

sys.path.insert(0, os.path.abspath("../../src"))


# -- Project information -----------------------------------------------------

project = "paxplot"
author = "Jacob Kravits"
copyright = f"2022-{date.today().year}, onethousandeight"

# Keep the docs version in sync with the installed package.
try:
    release = metadata.version("paxplot")
except metadata.PackageNotFoundError:
    release = "1.0.0"
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinx_sitemap",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Numpy-style docstrings.
napoleon_numpy_docstring = True

# Move type hints out of signatures, which keeps pydantic models readable.
autodoc_typehints = "description"
autodoc_member_order = "bysource"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pydantic": ("https://pydantic.dev/docs/validation/latest/", None),
}
intersphinx_timeout = 15

# Markdown support (MyST).
myst_enable_extensions = ["colon_fence", "deflist", "tasklist", "linkify"]
myst_heading_anchors = 3

# Execute the scripts in examples/ and build the gallery.
sphinx_gallery_conf = {
    "examples_dirs": "../../examples",
    "gallery_dirs": "auto_examples",
    "filename_pattern": r"\.py",
    # Save vector graphics so figures stay sharp at any size.
    "image_scrapers": (partial(matplotlib_scraper, format="svg"),),
    "within_subsection_order": "FileNameSortKey",
    "remove_config_comments": True,
    "download_all_examples": False,
}


# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_title = "paxplot"

# Used by the sitemap extension and canonical links.
html_baseurl = "https://docs.paxplot.org/"

html_theme_options = {
    "github_url": "https://github.com/onethousandeight/paxplot",
    "use_edit_page_button": True,
    "navigation_depth": 2,
    "show_prev_next": False,
}

html_context = {
    "github_user": "onethousandeight",
    "github_repo": "paxplot",
    "github_version": "main",
    "doc_path": "docs/source",
}

# Strip prompts from copied code blocks.
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
