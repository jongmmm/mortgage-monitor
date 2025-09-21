"""Chart factory for creating and managing all charts."""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict

from ..config.settings import settings
from .lock_in import LockInChart


class ChartFactory:
    """Factory for creating and managing all dashboard charts."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize chart factory with data.
        
        Args:
            df: DataFrame containing all time series data.
        """
        self.df = df
        self.charts = {
            'lock_in': LockInChart(df),
        }
    
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
            filename = f"{output_dir}/{settings.CHART_FILES[name]}"
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
