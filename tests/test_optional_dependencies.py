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
import types
from importlib import import_module

import pytest


def reimport_without(monkeypatch, module, missing):
    """Import ``module`` from scratch, with ``missing`` unimportable."""
    # Its submodules too: `from breadability.readable import ...` is satisfied straight from
    # sys.modules when another test already imported it, without consulting the parent.
    for name in [missing, *(name for name in sys.modules if name.startswith(missing + "."))]:
        monkeypatch.setitem(sys.modules, name, None)

    # Importing a submodule also rebinds it as an attribute of its package, which sys.modules
    # alone does not undo -- `sumy.parsers.html` would keep pointing at this second copy of
    # the module, with its own classes, for the rest of the session.
    parent, _, attribute = module.rpartition(".")
    package = sys.modules.get(parent)
    if package is not None and hasattr(package, attribute):
        monkeypatch.setattr(package, attribute, getattr(package, attribute))

    monkeypatch.delitem(sys.modules, module, raising=False)

    return import_module(module)


def test_utils_import_without_requests(monkeypatch):
    utils = reimport_without(monkeypatch, "sumy.utils", missing="requests")

    assert utils.normalize_language("en") == "english"


def test_fetch_url_without_requests_explains_what_to_install(monkeypatch):
    utils = reimport_without(monkeypatch, "sumy.utils", missing="requests")

    with pytest.raises(ValueError, match="pip install requests"):
        utils.fetch_url("https://example.com/")


def test_html_parser_import_without_breadability(monkeypatch):
    html = reimport_without(monkeypatch, "sumy.parsers.html", missing="breadability")

    with pytest.raises(ValueError, match="pip install breadability"):
        html.HtmlParser("<p>Hello.</p>", url=None, tokenizer=None)


def test_html_parser_names_the_dependency_that_actually_failed(monkeypatch):
    """breadability itself needs lxml, and "install breadability" is no help then."""
    # breadability has to be imported again for the missing lxml to bite; an earlier test in
    # the session may have left it in sys.modules, already holding its lxml import.
    for name in [name for name in sys.modules if name.startswith("breadability")]:
        monkeypatch.delitem(sys.modules, name)

    html = reimport_without(monkeypatch, "sumy.parsers.html", missing="lxml")

    with pytest.raises(ValueError, match="lxml"):
        html.HtmlParser("<p>Hello.</p>", url=None, tokenizer=None)


class FakeXhrResponse:
    """The part of ``pyodide.http.pyxhr``'s response that fetch_url uses."""

    def __init__(self, content):
        self.content = content
        self.raised_for_status = False

    def raise_for_status(self):
        self.raised_for_status = True


def test_fetch_url_uses_the_browsers_own_http_client(monkeypatch):
    """A browser has no sockets, but Pyodide offers a synchronous XMLHttpRequest client."""
    response = FakeXhrResponse(b"<html>Downloaded in a tab.</html>")
    requested = []

    pyxhr = types.SimpleNamespace(get=lambda url: requested.append(url) or response)
    monkeypatch.setitem(sys.modules, "pyodide", types.ModuleType("pyodide"))
    monkeypatch.setitem(sys.modules, "pyodide.http", types.SimpleNamespace(pyxhr=pyxhr))
    monkeypatch.setattr(sys, "platform", "emscripten")

    utils = reimport_without(monkeypatch, "sumy.utils", missing="requests")

    assert utils.fetch_url("https://example.com/") == b"<html>Downloaded in a tab.</html>"
    assert requested == ["https://example.com/"]
    assert response.raised_for_status
