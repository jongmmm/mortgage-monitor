"""Data fetching utilities for FRED and FHFA NMDB."""

import io
import os
import zipfile
from typing import Dict

import pandas as pd
import requests
from fredapi import Fred

from ..config.settings import settings
from ..charts.registry import ChartRegistry


class DataFetcher:
    """Handles data fetching from FRED and FHFA NMDB."""

    def __init__(self):
        """Initialize the data fetcher."""
        settings.validate()
        self.fred = Fred(settings.FRED_API_KEY)

        # Create data subdirectories
        os.makedirs(f"{settings.DATA_DIR}/fred", exist_ok=True)
        os.makedirs(f"{settings.DATA_DIR}/nmdb", exist_ok=True)

    def fetch_fred_series(self, series_id: str) -> pd.Series:
        """Fetch a FRED series.

        Args:
            series_id: FRED series identifier

        Returns:
            Pandas Series indexed by date.
        """
        series = self.fred.get_series(series_id, settings.START_DATE, settings.END_DATE)
        # Save to file
        series.to_csv(f"{settings.DATA_DIR}/fred/{series_id}.csv")
        return series

    def fetch_all_fred_data(self) -> Dict[str, pd.Series]:
        """Fetch required FRED data series based on chart registry.

        Returns:
            Dictionary mapping series names to pandas Series.
        """
        print("Fetching FRED data...")
        data_dict = {}

        # Get required data dependencies from registry
        required_series = ChartRegistry.get_required_data_dependencies()

        # Filter to only FRED series (exclude special ones like NMDB_QuarterlyRate)
        fred_series_needed = {
            name: series_id
            for name, series_id in settings.FRED_SERIES.items()
            if name in required_series
        }

        print(f"Required FRED series: {list(fred_series_needed.keys())}")

        # Fetch all required FRED series
        for series_name, series_id in fred_series_needed.items():
            try:
                data_dict[series_name] = self.fetch_fred_series(series_id)
                print(
                    f"✓ Fetched {series_name} - {len(data_dict[series_name])} observations"
                )
            except Exception as e:
                print(f"✗ Failed to fetch {series_name}: {e}")
                data_dict[series_name] = pd.Series(dtype=float, name=series_name)

        return data_dict

    def fetch_fhfa_nmdb_quarterly_rate(self) -> pd.Series:
        """Fetch FHFA NMDB quarterly average interest rate.

        Returns:
            Quarterly Series indexed by quarter-end dates.
        """
        url = "https://www.fhfa.gov/document/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip"
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
            df = pd.read_csv(zf.open(csv_name))

        # Save raw data
        df.to_csv(f"{settings.DATA_DIR}/nmdb/raw_nmdb.csv", index=False)

        # Filter for National and All Mortgages
        filtered = df.query(
            "GEOLEVEL=='National' and MARKET=='All Mortgages' and SERIESID=='AVE_INTRATE'"
        ).copy()
        val_col = "VALUE2" if "VALUE2" in filtered.columns else "VALUE1"

        # Save filtered data
        filtered.to_csv(f"{settings.DATA_DIR}/nmdb/filtered_nmdb.csv", index=False)

        # Convert to quarterly time series
        period_raw = filtered["PERIOD"].astype(str).str.upper()
        print(f"Sample PERIOD values: {period_raw.head(10).tolist()}")

        year = period_raw.str.extract(r"(\d{4})")[0].astype(int)
        quarter = period_raw.str.extract(r"Q([1-4])")[0].astype(int)

        # Create proper quarterly start dates (date only, no time)
        quarter_start_dates = (
            pd.PeriodIndex(year.astype(str) + "Q" + quarter.astype(str), freq="Q-DEC")
            .to_timestamp(how="start")
            .normalize()
        )  # Remove time component

        # Create quarterly series with both start and end dates for step visualization
        quarterly_rates = pd.to_numeric(filtered[val_col], errors="coerce")

        # Create both start and end dates for each quarter
        quarter_end_dates = (
            pd.PeriodIndex(year.astype(str) + "Q" + quarter.astype(str), freq="Q-DEC")
            .to_timestamp(how="end")
            .normalize()
        )

        # Create expanded series with both start and end points for each quarter
        expanded_dates = []
        expanded_values = []

        for start_date, end_date, rate in zip(
            quarter_start_dates, quarter_end_dates, quarterly_rates
        ):
            if not pd.isna(rate):
                expanded_dates.extend([start_date, end_date])
                expanded_values.extend([rate, rate])

        quarterly_series = pd.Series(
            expanded_values,
            index=pd.DatetimeIndex(expanded_dates),
            name="NMDB_QuarterlyRate",
        ).sort_index()

        # Save quarterly data
        quarterly_series.to_csv(f"{settings.DATA_DIR}/nmdb/quarterly_rate.csv")
        print(f"Quarterly data saved: {len(quarterly_series)} quarters")
        print(
            f"Date range: {quarterly_series.index.min()} to {quarterly_series.index.max()}"
        )

        return quarterly_series

    def combine_data(
        self, data_dict: Dict[str, pd.Series], nmdb_data: pd.Series
    ) -> pd.DataFrame:
        """Combine FRED and NMDB data.

        Args:
            data_dict: Dictionary of FRED data series
            nmdb_data: FHFA NMDB average interest rate series

        Returns:
            Combined DataFrame.
        """
        if not nmdb_data.empty:
            data_dict["NMDB_QuarterlyRate"] = nmdb_data
            print("✓ NMDB quarterly data available")
        else:
            print("✗ No NMDB quarterly data available")

        df = pd.concat(data_dict.values(), axis=1, keys=data_dict.keys())
        df = df.dropna(how="all")

        # Save individual chart data files
        self._save_chart_data_files(data_dict, nmdb_data)

        return df

    def _save_chart_data_files(
        self, data_dict: Dict[str, pd.Series], nmdb_data: pd.Series
    ) -> None:
        """Save individual data files for each chart based on registry.

        Args:
            data_dict: Dictionary of FRED data series
            nmdb_data: FHFA NMDB average interest rate series
        """
        print("Saving individual chart data files...")

        # Add NMDB data to the available data
        all_data = data_dict.copy()
        if not nmdb_data.empty:
            all_data["NMDB_QuarterlyRate"] = nmdb_data

        # Save data file for each registered chart
        for chart_meta in ChartRegistry.get_all_charts():
            chart_data = {}

            # Collect required data for this chart
            for dependency in chart_meta.data_dependencies:
                if dependency in all_data:
                    chart_data[dependency] = all_data[dependency]

            # Save chart data file if we have any data
            if chart_data:
                df = pd.concat(chart_data.values(), axis=1, keys=chart_data.keys())
                df = df.dropna(how="all")
                file_path = f"{settings.DATA_DIR}/{chart_meta.name}_data.csv"
                df.to_csv(file_path)
                print(f"✓ Saved {chart_meta.name} chart data: {file_path}")
            else:
                print(
                    f"⚠ No data available for {chart_meta.name} chart dependencies: {chart_meta.data_dependencies}"
                )
