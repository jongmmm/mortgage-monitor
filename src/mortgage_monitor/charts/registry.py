"""Chart registry system for composable chart architecture."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Type


@dataclass
class DataSource:
    """Represents a data source with name and URL."""
    name: str
    url: str


@dataclass
class ChartMetadata:
    """Metadata for a chart including all information needed for registration."""
    name: str
    title: str
    data_dependencies: List[str]
    explanation: str | None = None
    data_sources: List[DataSource] = field(default_factory=list)
    chart_class: Type | None = None
    order: int = 100
    enabled: bool = True


class ChartRegistry:
    """Central registry for all charts in the system."""
    
    _charts: Dict[str, ChartMetadata] = {}
    
    @classmethod
    def register(cls, metadata: ChartMetadata) -> None:
        """Register a chart with the registry.
        
        Args:
            metadata: Chart metadata to register.
        """
        if metadata.name in cls._charts:
            raise ValueError(f"Chart '{metadata.name}' is already registered")
        
        cls._charts[metadata.name] = metadata
        print(f"✓ Registered chart: {metadata.name}")
    
    @classmethod
    def get_chart(cls, name: str) -> ChartMetadata | None:
        """Get chart metadata by name.
        
        Args:
            name: Chart name.
            
        Returns:
            Chart metadata or None if not found.
        """
        return cls._charts.get(name)
    
    @classmethod
    def get_all_charts(cls) -> List[ChartMetadata]:
        """Get all registered charts sorted by order.
        
        Returns:
            List of chart metadata sorted by order.
        """
        return sorted(
            [chart for chart in cls._charts.values() if chart.enabled],
            key=lambda x: x.order
        )
    
    @classmethod
    def get_required_data_dependencies(cls) -> Set[str]:
        """Get all data dependencies required by enabled charts.
        
        Returns:
            Set of required data series names.
        """
        dependencies = set()
        for chart in cls.get_all_charts():
            dependencies.update(chart.data_dependencies)
        return dependencies
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered charts (mainly for testing)."""
        cls._charts.clear()


def register_chart(
    name: str,
    title: str,
    data_dependencies: List[str],
    explanation: str | None = None,
    data_sources: List[Dict[str, str]] | None = None,
    order: int = 100,
    enabled: bool = True
):
    """Decorator to register a chart class with the registry.
    
    Args:
        name: Unique chart identifier.
        title: Human-readable chart title.
        data_dependencies: List of data series names this chart needs.
        explanation: Optional detailed explanation text.
        data_sources: Optional list of data sources with name and url keys.
        order: Display order (lower numbers appear first).
        enabled: Whether the chart is enabled.
    
    Returns:
        Decorator function.
    """
    def decorator(chart_class: Type) -> Type:
        # Convert data_sources dict list to DataSource objects
        sources = []
        if data_sources:
            sources = [DataSource(name=ds["name"], url=ds["url"]) for ds in data_sources]
        
        metadata = ChartMetadata(
            name=name,
            title=title,
            data_dependencies=data_dependencies,
            explanation=explanation,
            data_sources=sources,
            chart_class=chart_class,
            order=order,
            enabled=enabled
        )
        
        ChartRegistry.register(metadata)
        return chart_class
    
    return decorator
