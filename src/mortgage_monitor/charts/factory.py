"""Chart factory for creating and managing all charts."""

import os
import pandas as pd
import plotly.graph_objects as go
from typing import Dict

from ..config.settings import settings
from .registry import ChartRegistry


class ChartFactory:
    """Factory for creating and managing all dashboard charts."""
    
    def __init__(self, df: pd.DataFrame | None = None):
        """Initialize chart factory.
        
        Args:
            df: DataFrame containing all time series data (legacy, kept for compatibility).
        """
        self.df = df  # Keep for backward compatibility
        self.charts = self._discover_charts()
    
    def _discover_charts(self) -> Dict[str, object]:
        """Discover and initialize charts from the registry.
        
        Returns:
            Dictionary mapping chart names to chart instances.
        """
        charts = {}
        
        for chart_meta in ChartRegistry.get_all_charts():
            try:
                # Try to load chart-specific data file
                data_path = f"{settings.DATA_DIR}/{chart_meta.name}_data.csv"
                
                if os.path.exists(data_path):
                    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
                    charts[chart_meta.name] = chart_meta.chart_class(df)
                    print(f"✓ Loaded {chart_meta.name} chart data from {data_path}")
                elif self.df is not None:
                    # Fallback to combined data if available
                    charts[chart_meta.name] = chart_meta.chart_class(self.df)
                    print(f"⚠ Using combined data for {chart_meta.name} chart (individual file not found)")
                else:
                    print(f"✗ No data available for {chart_meta.name} chart")
                    
            except Exception as e:
                print(f"✗ Failed to initialize {chart_meta.name} chart: {e}")
        
        return charts
    
    def create_all_charts(self) -> Dict[str, go.Figure]:
        """Create all charts and return as dictionary.
        
        Returns:
            Dictionary mapping chart names to Plotly figures.
        """
        print("Creating visualizations...")
        figures = {}
        
        for name, chart in self.charts.items():
            try:
                figures[name] = chart.create_chart()
                print(f"✓ Created {name} chart")
            except Exception as e:
                print(f"✗ Failed to create {name} chart: {e}")
                # Create empty figure as fallback
                figures[name] = go.Figure()
                figures[name].add_annotation(
                    text=f"Error creating {name} chart: {str(e)}",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    font=dict(color="red", size=14)
                )
        
        return figures
    
    def save_all_charts(self, figures: Dict[str, go.Figure], output_dir: str = ".") -> None:
        """Save all charts to HTML files.
        
        Args:
            figures: Dictionary of chart figures
            output_dir: Output directory for chart files
        """
        for name, fig in figures.items():
            filename = f"{output_dir}/{name}_chart.html"
            try:
                fig.write_html(filename, include_plotlyjs="cdn")
                print(f"✓ Saved {name} chart to {filename}")
            except Exception as e:
                print(f"✗ Failed to save {name} chart: {e}")
    
    def get_chart_metrics(self) -> Dict[str, float]:
        """Get key metrics for dashboard display.
        
        Returns:
            Dictionary of key metrics.
        """
        return {}  # Simplified - no metrics needed for basic overlay
