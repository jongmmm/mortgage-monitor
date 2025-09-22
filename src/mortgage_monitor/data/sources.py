"""Centralized data source definitions and metadata."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class DataSource:
    """Data source metadata."""

    name: str
    description: str
    url: str
    provider: str
    frequency: str


# Centralized data source registry
DATA_SOURCES: Dict[str, DataSource] = {
    "Mortgage30": DataSource(
        name="FRED: 30Y Mortgage Rate (MORTGAGE30US)",
        description="30-Year Fixed Rate Mortgage Average in the United States",
        url="https://fred.stlouisfed.org/series/MORTGAGE30US",
        provider="Federal Reserve Economic Data (FRED)",
        frequency="Weekly",
    ),
    "Treasury10Y": DataSource(
        name="FRED: 10Y Treasury Rate (DGS10)",
        description="10-Year Treasury Constant Maturity Rate",
        url="https://fred.stlouisfed.org/series/DGS10",
        provider="Federal Reserve Economic Data (FRED)",
        frequency="Daily",
    ),
    "NMDB_QuarterlyRate": DataSource(
        name="FHFA NMDB: Outstanding Mortgage Statistics",
        description="National Mortgage Database Quarterly Outstanding Mortgage Interest Rate Statistics",
        url="https://www.fhfa.gov/document/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip",
        provider="Federal Housing Finance Agency (FHFA)",
        frequency="Quarterly",
    ),
}


def get_data_sources_for_dependencies(dependencies: list[str]) -> list[dict]:
    """Get data source information for given dependencies.

    Args:
        dependencies: List of data dependency keys.

    Returns:
        List of data source dictionaries for chart registration.
    """
    sources = []
    for dep in dependencies:
        if dep in DATA_SOURCES:
            source = DATA_SOURCES[dep]
            sources.append({"name": source.name, "url": source.url})
    return sources


def get_data_source_info(dependency: str) -> DataSource | None:
    """Get detailed data source information.

    Args:
        dependency: Data dependency key.

    Returns:
        DataSource object or None if not found.
    """
    return DATA_SOURCES.get(dependency)
