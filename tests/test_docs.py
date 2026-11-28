import re
from pathlib import Path

import paxplot

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs" / "source"
API_DOC = DOCS / "api.rst"
PAGES = [
    path
    for path in DOCS.rglob("*")
    if path.suffix in {".md", ".rst"} and "auto_examples" not in path.parts
]
LITERALINCLUDE = re.compile(r"```\{literalinclude\}\s+(\S+)")
GALLERY_IMAGE = re.compile(
    r"```\{image\}\s+auto_examples/images/sphx_glr_(\w+)_\d+\.(?:png|svg)"
)


def test_public_api_is_documented():
    text = API_DOC.read_text(encoding="utf-8")
    missing = [name for name in paxplot.__all__ if f"paxplot.{name}" not in text]
    assert not missing, f"Public names missing from api.rst: {missing}"


def test_pages_include_python_instead_of_embedding_it():
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        assert "```python" not in text, f"{page} embeds Python; use literalinclude"
        assert ".. code-block:: python" not in text, (
            f"{page} embeds Python; use literalinclude"
        )


def test_literalinclude_paths_exist():
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        for relative in LITERALINCLUDE.findall(text):
            path = (page.parent / relative).resolve()
            assert path.exists(), f"{page} includes missing file: {relative}"


def test_gallery_images_come_from_an_example():
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        for stem in GALLERY_IMAGE.findall(text):
            assert (ROOT / "examples" / f"{stem}.py").exists(), (
                f"{page} shows a gallery image with no matching example: {stem}.py"
            )
