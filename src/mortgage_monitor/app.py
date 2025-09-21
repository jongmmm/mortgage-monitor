"""Main application orchestrator for the mortgage monitor dashboard."""

import os
import pandas as pd
from typing import Dict

from .config.settings import settings
from .data.fetchers import DataFetcher
from .charts.factory import ChartFactory
from .templates.dashboard import DashboardTemplate


class MortgageMonitorApp:
    """Main application class for the mortgage monitor dashboard."""
    
    def __init__(self):
        """Initialize the application."""
        self.data_fetcher = DataFetcher()
        self.df: pd.DataFrame | None = None
        self.chart_factory: ChartFactory | None = None
        
        # Ensure output directories exist
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    def fetch_data(self) -> pd.DataFrame:
        """Fetch all required data.
        
        Returns:
            Combined DataFrame with all data series.
        """
        print("Starting data collection...")
        
        # Fetch FRED data
        fred_data = self.data_fetcher.fetch_all_fred_data()

        # Fetch FHFA NMDB quarterly interest rate
        nmdb_data = self.data_fetcher.fetch_fhfa_nmdb_quarterly_rate()

        # Combine all data
        self.df = self.data_fetcher.combine_data(fred_data, nmdb_data)
        
        return self.df
    
    def save_data(self, df: pd.DataFrame) -> None:
        """Save data to CSV file.
        
        Args:
            df: DataFrame to save.
        """
        output_path = f"{settings.DATA_DIR}/{settings.DATA_FILE}"
        df.to_csv(output_path)
        print(f"Data saved to {output_path}")
    
    def create_charts(self, df: pd.DataFrame) -> Dict:
        """Create all dashboard charts.
        
        Args:
            df: DataFrame with data.
            
        Returns:
            Dictionary of chart figures and metrics.
        """
        self.chart_factory = ChartFactory(df)
        
        # Create all charts
        figures = self.chart_factory.create_all_charts()
        
        # Save charts to HTML files
        self.chart_factory.save_all_charts(figures, settings.OUTPUT_DIR)
        
        # Get key metrics
        metrics = self.chart_factory.get_chart_metrics()
        
        return {
            'figures': figures,
            'metrics': metrics
        }
    
    def create_dashboard(self, metrics: Dict[str, float]) -> str:
        """Create the main dashboard HTML.
        
        Args:
            metrics: Dictionary of key metrics.
            
        Returns:
            HTML content for dashboard.
        """
        template = DashboardTemplate(metrics)
        html_content = template.generate_html()
        
        # Save dashboard HTML
        dashboard_path = f"{settings.OUTPUT_DIR}/{settings.DASHBOARD_FILE}"
        with open(dashboard_path, "w") as f:
            f.write(html_content)
        
        print(f"✅ Comprehensive mortgage dashboard created: {dashboard_path}")
        return html_content
    
    def run(self) -> None:
        """Run the complete mortgage monitor application."""
        try:
            # Step 1: Fetch data
            df = self.fetch_data()
            
            # Step 2: Save data
            self.save_data(df)
            
            # Step 3: Create charts
            chart_results = self.create_charts(df)
            
            # Step 4: Create dashboard
            self.create_dashboard(chart_results['metrics'])
            
            # Step 5: Print summary
            self._print_summary()
            
        except Exception as e:
            print(f"❌ Application failed: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print application summary."""
        print("📊 Data saved: mortgage_dashboard_data.csv")
        print("🚀 Dashboard includes:")
        print("   - NMDB quarterly average mortgage interest rate overlaid with current 30Y mortgage rate")


def main() -> None:
    """Main entry point for the application."""
    app = MortgageMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
