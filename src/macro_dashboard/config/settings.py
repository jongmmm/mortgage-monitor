"""Configuration for macro_dashboard.

This config is intentionally minimal and opinionated to allow
imperative, low-code composition of dashboards.
"""

from __future__ import annotations

import datetime as _dt
import os
from dataclasses import dataclass
from typing import Dict


# Optionally load .env if python-dotenv is available
try:  # pragma: no cover - optional convenience
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


@dataclass(frozen=True)
class Settings:
    # Database
    DB_PATH: str = os.getenv("MACRO_DB_PATH", "data/macro_dashboard.db")

    # Storage
    DATA_DIR: str = os.getenv("MACRO_DATA_DIR", "data")
    OUTPUT_DIR: str = os.getenv("MACRO_OUTPUT_DIR", "output")
    TEMPLATES_DIR: str = "src/macro_dashboard/templates"

    # API keys
    FRED_API_KEY: str | None = os.getenv("FRED_API_KEY")

    # Fetch horizon
    START_DATE: str = os.getenv("MACRO_START_DATE", "1999-01-01")
    END_DATE: str = os.getenv("MACRO_END_DATE", str(_dt.date.today()))

    # Predefined series registry keys (aliases → provider identifiers)
    # Notes:
    # - frequency: D, W, M, Q, A (ISO-like tokens)
    # - is_periodic: True if value covers a period (e.g., quarterly average)
    #   rather than an instant/end-of-day observation.
    FRED_SERIES: Dict[str, Dict[str, str | bool]] = {
        "Mortgage30": {
            "id": "MORTGAGE30US",
            "frequency": "W",
            "is_periodic": False,
            "title": "30Y Fixed Mortgage Rate",
            "unit": "%",
        },
        "Treasury10Y": {
            "id": "DGS10",
            "frequency": "D",
            "is_periodic": False,
            "title": "10Y Treasury Constant Maturity",
            "unit": "%",
        },
    }

    # NMDB registry keys (logical aliases)
    NMDB_SERIES: Dict[str, Dict[str, str | bool]] = {
        "NMDB_QuarterlyRate": {
            "id": "FHFA_NMDB_AVE_INTRATE",
            "frequency": "Q",
            "is_periodic": True,  # each value represents a quarter
            "title": "Avg Outstanding Mortgage Interest Rate (NMDB)",
            "unit": "%",
        }
    }

    DASHBOARD_FILE: str = "macro_index.html"


settings = Settings()

