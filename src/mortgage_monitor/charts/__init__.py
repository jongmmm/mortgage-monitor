"""Chart generation and visualization modules."""

# Import all chart components to ensure they register with the registry
from . import components
from .registry import ChartRegistry

# Make registry available at package level
__all__ = ["ChartRegistry", "components"]
