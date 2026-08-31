"""
Tests for running sumy where some of its dependencies are unavailable.

Pyodide/PyEmscripten cannot install every dependency sumy declares -- ``breadability`` pulls
in ``docopt``, which has no wheel on PyPI at all -- and ``requests`` cannot open a socket in a
browser anyway. Summarizing text in the browser must not depend on any of that, so the imports
below have to survive those modules being missing.

Setting a module to ``None`` in ``sys.modules`` is what makes ``import`` of it fail; dropping
sumy's own module forces it to be imported again under that condition. ``monkeypatch`` puts
both back afterwards.
"""

import sys
from importlib import import_module

import pytest


def reimport_without(monkeypatch, module, missing):
    """Import ``module`` from scratch, with ``missing`` unimportable."""
    # Its submodules too: `from breadability.readable import ...` is satisfied straight from
    # sys.modules when another test already imported it, without consulting the parent.
    for name in [missing, *(name for name in sys.modules if name.startswith(missing + "."))]:
        monkeypatch.setitem(sys.modules, name, None)
    monkeypatch.delitem(sys.modules, module, raising=False)
    return import_module(module)


def test_utils_import_without_requests(monkeypatch):
    utils = reimport_without(monkeypatch, "sumy.utils", missing="requests")

    assert utils.normalize_language("en") == "english"


def test_fetch_url_without_requests_explains_what_to_install(monkeypatch):
    utils = reimport_without(monkeypatch, "sumy.utils", missing="requests")

    with pytest.raises(ImportError, match="pip install requests"):
        utils.fetch_url("https://example.com/")


def test_html_parser_import_without_breadability(monkeypatch):
    html = reimport_without(monkeypatch, "sumy.parsers.html", missing="breadability")

    with pytest.raises(ImportError, match="pip install breadability"):
        html.HtmlParser("<p>Hello.</p>", url=None, tokenizer=None)
