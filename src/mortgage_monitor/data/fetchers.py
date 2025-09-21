"""Data fetching utilities for FRED and FHFA NMDB."""

import io
import os
import zipfile
from typing import Dict

import pandas as pd
import requests
from fredapi import Fred

from ..config.settings import settings


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
        """Fetch required FRED data series.
        
        Returns:
            Dictionary mapping series names to pandas Series.
        """
        print("Fetching FRED data...")
        data_dict = {}
        
        # Only fetch Mortgage30 for this simple overlay
        try:
            data_dict["Mortgage30"] = self.fetch_fred_series("MORTGAGE30US")
            print(f"✓ Fetched Mortgage30 - {len(data_dict['Mortgage30'])} observations")
        except Exception as e:
            print(f"✗ Failed to fetch Mortgage30: {e}")
            data_dict["Mortgage30"] = pd.Series(dtype=float, name="Mortgage30")
        
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
        filtered = df.query("GEOLEVEL=='National' and MARKET=='All Mortgages' and SERIESID=='AVE_INTRATE'").copy()
        val_col = "VALUE2" if "VALUE2" in filtered.columns else "VALUE1"
        
        # Save filtered data
        filtered.to_csv(f"{settings.DATA_DIR}/nmdb/filtered_nmdb.csv", index=False)
        
        # Convert to quarterly time series
        period_raw = filtered["PERIOD"].astype(str).str.upper()
        print(f"Sample PERIOD values: {period_raw.head(10).tolist()}")
        
        year = period_raw.str.extract(r"(\d{4})")[0].astype(int)
        quarter = period_raw.str.extract(r"Q([1-4])")[0].astype(int)
        
        # Create proper quarterly end dates (date only, no time)
        quarter_end_dates = pd.PeriodIndex(
            year.astype(str) + "Q" + quarter.astype(str), freq="Q-DEC"
        ).to_timestamp(how="end").normalize()  # Remove time component
        
        # Create quarterly series
        quarterly_rates = pd.to_numeric(filtered[val_col], errors="coerce")
        quarterly_series = pd.Series(
            quarterly_rates.values, 
            index=quarter_end_dates, 
            name="NMDB_QuarterlyRate"
        ).sort_index()
        
        # Remove any NaN values
        quarterly_series = quarterly_series.dropna()
        
        # Save quarterly data
        quarterly_series.to_csv(f"{settings.DATA_DIR}/nmdb/quarterly_rate.csv")
        print(f"Quarterly data saved: {len(quarterly_series)} quarters")
        print(f"Date range: {quarterly_series.index.min()} to {quarterly_series.index.max()}")
        
        return quarterly_series
    
    
    def combine_data(self, data_dict: Dict[str, pd.Series], nmdb_data: pd.Series) -> pd.DataFrame:
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
        df = df.dropna(how='all')
        
        
        return df
