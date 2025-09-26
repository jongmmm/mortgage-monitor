"""Macro Dashboard engine package.

This module provides a composable dashboard engine that:
- Downloads data from predefined sources (FRED, NMDB)
- Stores raw observations and metadata in a SQLite database
- Prepares plotting payloads carrying frequency/period semantics
- Renders reusable components like tables and spread charts

Note: This package does not modify the existing mortgage_monitor module.
"""

__all__ = [
    "__version__",
]

__version__ = "0.1.0"

