"""Predefined series registry and helpers.

These definitions centralize which time series we download and how we
interpret their metadata (frequency and whether values represent periods).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from ..config.settings import settings


@dataclass(frozen=True)
class SeriesDef:
    alias: str
    source: str  # "FRED" | "NMDB"
    code: str    # provider-specific code
    title: str
    unit: str | None
    frequency: str  # D,W,M,Q,A
    is_periodic: bool


def iter_all_series() -> Iterable[SeriesDef]:
    # FRED
    for alias, meta in settings.FRED_SERIES.items():
        yield SeriesDef(
            alias=alias,
            source="FRED",
            code=str(meta["id"]),
            title=str(meta.get("title", alias)),
            unit=str(meta.get("unit", "")) or None,
            frequency=str(meta.get("frequency", "D")),
            is_periodic=bool(meta.get("is_periodic", False)),
        )

    # NMDB
    for alias, meta in settings.NMDB_SERIES.items():
        yield SeriesDef(
            alias=alias,
            source="NMDB",
            code=str(meta["id"]),
            title=str(meta.get("title", alias)),
            unit=str(meta.get("unit", "")) or None,
            frequency=str(meta.get("frequency", "Q")),
            is_periodic=bool(meta.get("is_periodic", True)),
        )


def alias_map() -> Dict[str, SeriesDef]:
    return {s.alias: s for s in iter_all_series()}

