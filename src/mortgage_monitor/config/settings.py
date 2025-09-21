"""Configuration settings for the mortgage monitor."""

import datetime
import os
from typing import Dict

# Optionally load .env if python-dotenv is available
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # It's okay if python-dotenv isn't installed; CI uses GitHub Secrets.
    pass


class Settings:
    """Application settings and configuration."""
    
    # API Keys
    FRED_API_KEY: str | None = os.getenv("FRED_API_KEY")
    
    # Data settings
    START_DATE: str | datetime.date = "2000-01-01"
    END_DATE: datetime.date = datetime.date.today()
    
    # FRED Series Configuration (simplified)
    FRED_SERIES: Dict[str, str] = {
        "Mortgage30": "MORTGAGE30US",
        "Treasury10Y": "DGS10",
    }
    
    # Output paths
    DATA_DIR = "data"
    OUTPUT_DIR = "output"
    TEMPLATES_DIR = "src/mortgage_monitor/templates"
    
    # File names
    DATA_FILE = "mortgage_dashboard_data.csv"  # Legacy combined file
    DASHBOARD_FILE = "index.html"
    
    # Note: Individual chart data files and chart HTML files are now 
    # dynamically generated based on chart registry. No hard-coding needed.
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if cls.FRED_API_KEY is None or not cls.FRED_API_KEY.strip():
            raise RuntimeError(
                "FRED_API_KEY is not set. Set it in your environment or in a local .env file (FRED_API_KEY=your_key)."
            )


# Global settings instance
settings = Settings()
