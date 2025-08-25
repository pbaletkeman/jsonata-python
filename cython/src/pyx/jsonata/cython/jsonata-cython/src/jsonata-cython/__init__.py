"""
jsonata_cython
--------------

A Cython-accelerated implementation of JSONata utilities.
"""

from importlib import import_module, metadata

try:
    __version__ = metadata.version("jsonata-cython")
except metadata.PackageNotFoundError:
    # Fallback if package is not installed (e.g. in dev mode)
    __version__ = "0.0.0"

__all__ = [
    "utils",
    "tokenizer",
    "signature",
    "jexception",
    "datetimeutils",
    "parser",
    "functions",
    "Constants",
]

# Import each known submodule so they're available under jsonata_cython.<module>
for module in __all__:
    globals()[module] = import_module(f"jsonata_cython.{module}")


def __getattr__(name: str):
    """
    Fallback attribute access.
    Ensures that missing attributes raise a clean AttributeError,
    instead of an obscure ImportError or KeyError.
    """
    if name in __all__:
        return import_module(f"jsonata_cython.{name}")
    raise AttributeError(f"module 'jsonata_cython' has no attribute '{name}'")
