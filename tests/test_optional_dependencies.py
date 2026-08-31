"""
Tests for running sumy where some of its dependencies are unavailable.

Pyodide/PyEmscripten cannot install every dependency sumy declares -- ``breadability`` pulls
in ``docopt``, which has no wheel on PyPI at all -- and ``requests`` cannot open a socket in a
browser anyway. Summarizing text in the browser must not depend on any of that, so the imports
below have to survive those modules being missing.
"""

import builtins
import sys
from contextlib import contextmanager
from importlib import import_module, reload


@contextmanager
def hidden_modules(*names):
    """Make ``import name`` fail with ``ModuleNotFoundError`` inside the block."""
    real_import = builtins.__import__
    hidden = {name for name in names}
    saved = {key: value for key, value in sys.modules.items() if key.split(".")[0] in hidden}

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in hidden:
            raise ModuleNotFoundError(f"No module named {name.split('.')[0]!r}", name=name)
        return real_import(name, *args, **kwargs)

    for key in saved:
        del sys.modules[key]
    builtins.__import__ = guarded_import
    try:
        yield
    finally:
        builtins.__import__ = real_import
        sys.modules.update(saved)


def reimport(name):
    """Import ``name`` from scratch, ignoring an already imported copy of it."""
    sys.modules.pop(name, None)
    return reload(import_module(name))


def test_utils_import_without_requests():
    with hidden_modules("requests"):
        assert reimport("sumy.utils").normalize_language("en") == "english"
