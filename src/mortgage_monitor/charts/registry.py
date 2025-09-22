"""Chart registry system for composable chart architecture."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Type

from ..data.sources import get_data_sources_for_dependencies


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
    page: str = "Overview"
    page_order: int = 100  # For ordering pages


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

        # Validate page_order consistency
        cls._validate_page_order_consistency(metadata)

        cls._charts[metadata.name] = metadata
        print(f"✓ Registered chart: {metadata.name}")

    @classmethod
    def _validate_page_order_consistency(cls, new_metadata: ChartMetadata) -> None:
        """Validate that all charts on the same page have consistent page_order.

        Args:
            new_metadata: New chart metadata being registered.

        Raises:
            ValueError: If page_order is inconsistent with existing charts on same page.
        """
        existing_page_order = None
        conflicting_charts = []

        for chart in cls._charts.values():
            if chart.page == new_metadata.page:
                if existing_page_order is None:
                    existing_page_order = chart.page_order
                elif chart.page_order != existing_page_order:
                    conflicting_charts.append(
                        f"{chart.name} (page_order={chart.page_order})"
                    )

        # Check if new chart conflicts with existing page_order
        if (
            existing_page_order is not None
            and new_metadata.page_order != existing_page_order
        ):
            conflicting_charts.append(
                f"{new_metadata.name} (page_order={new_metadata.page_order})"
            )

            if conflicting_charts:
                raise ValueError(
                    f"Page order conflict detected for page '{new_metadata.page}'. "
                    f"All charts on the same page must have the same page_order value. "
                    f"Conflicting charts: {', '.join(conflicting_charts)}. "
                    f"Expected page_order: {existing_page_order}"
                )

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
            key=lambda x: x.order,
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
    def get_charts_by_page(cls) -> Dict[str, List[ChartMetadata]]:
        """Get all charts grouped by page.

        Returns:
            Dictionary mapping page names to lists of chart metadata.
        """
        pages = {}
        for chart in cls.get_all_charts():
            page = chart.page
            if page not in pages:
                pages[page] = []
            pages[page].append(chart)

        # Sort charts within each page by order
        for page_charts in pages.values():
            page_charts.sort(key=lambda x: x.order)

        return pages

    @classmethod
    def get_page_names(cls) -> List[str]:
        """Get all unique page names from registered charts ordered by page_order.

        Returns:
            List of page names sorted by page_order, then alphabetically.
        """
        page_info = {}
        for chart in cls.get_all_charts():
            page = chart.page
            if page not in page_info:
                page_info[page] = chart.page_order
            else:
                # Use the minimum page_order if multiple charts on same page
                page_info[page] = min(page_info[page], chart.page_order)

        # Sort by page_order, then by name
        return sorted(page_info.keys(), key=lambda x: (page_info[x], x))

    @classmethod
    def validate_all_page_orders(cls) -> Dict[str, List[str]]:
        """Validate page order consistency across all registered charts.

        Returns:
            Dictionary mapping page names to lists of conflicting chart info.
            Empty dict means no conflicts.
        """
        page_orders = {}
        conflicts = {}

        for chart in cls._charts.values():
            page = chart.page
            if page not in page_orders:
                page_orders[page] = {}

            order = chart.page_order
            if order not in page_orders[page]:
                page_orders[page][order] = []
            page_orders[page][order].append(f"{chart.name} (order={order})")

        # Find pages with multiple different page_order values
        for page, orders in page_orders.items():
            if len(orders) > 1:
                all_charts = []
                for chart_list in orders.values():
                    all_charts.extend(chart_list)
                conflicts[page] = all_charts

        return conflicts

    @classmethod
    def get_page_order_summary(cls) -> Dict[str, int]:
        """Get a summary of page orders for all pages.

        Returns:
            Dictionary mapping page names to their page_order values.
        """
        page_orders = {}
        for chart in cls._charts.values():
            page = chart.page
            if page not in page_orders:
                page_orders[page] = chart.page_order
        return page_orders

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
    enabled: bool = True,
    page: str = "Overview",
    page_order: int = 100,
):
    """Decorator to register a chart class with the registry.

    Args:
        name: Unique chart identifier.
        title: Human-readable chart title.
        data_dependencies: List of data series names this chart needs.
        explanation: Optional detailed explanation text.
        data_sources: Optional list of data sources with name and url keys.
                     If None, will be auto-populated from data_dependencies.
        order: Display order within page (lower numbers appear first).
        enabled: Whether the chart is enabled.
        page: Page name for organizing charts into tabs.
        page_order: Page display order (lower numbers appear first).

    Returns:
        Decorator function.
    """

    def decorator(chart_class: Type) -> Type:
        # Auto-populate data sources from dependencies if not provided
        if data_sources is None:
            auto_sources = get_data_sources_for_dependencies(data_dependencies)
            sources = [
                DataSource(name=ds["name"], url=ds["url"]) for ds in auto_sources
            ]
        else:
            # Convert provided data_sources dict list to DataSource objects
            sources = [
                DataSource(name=ds["name"], url=ds["url"]) for ds in data_sources
            ]

        metadata = ChartMetadata(
            name=name,
            title=title,
            data_dependencies=data_dependencies,
            explanation=explanation,
            data_sources=sources,
            chart_class=chart_class,
            order=order,
            enabled=enabled,
            page=page,
            page_order=page_order,
        )

        ChartRegistry.register(metadata)
        return chart_class

    return decorator
