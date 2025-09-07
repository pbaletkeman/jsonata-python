"""
JException subpackage initialization for Jsonata Python implementation.
Imports all exception modules for error handling.
"""

import os
import glob

__all__ = []

# Get all .py files in the current directory except __init__.py
module_files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
for path in module_files:
    module = os.path.splitext(os.path.basename(path))[0]
    if module != "__init__":
        __all__.append(module)
        exec(f"from .{module} import *")
