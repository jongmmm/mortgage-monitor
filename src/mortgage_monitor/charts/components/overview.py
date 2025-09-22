"""Overview summary chart showing latest values from all time series."""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

from ..registry import register_chart, ChartRegistry


@register_chart(
    name="overview",
    title="Market Overview - Latest Values",
    data_dependencies=["Mortgage30", "Treasury10Y", "NMDB_QuarterlyRate"],
    explanation="Summary of the latest values from all key mortgage market indicators.",
    order=0,
    page="Overview",
    page_order=1,  # Make Overview page first
)
class OverviewChart:
    """Chart showing latest values summary."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with data.

        Args:
            df: DataFrame containing time series data.
        """
        self.df = df

    def create_chart(self) -> go.Figure:
        """Create overview summary chart.

        Returns:
            Plotly figure showing latest values summary.
        """
        # Get latest values from each series
        latest_values = self._get_latest_values()

        # Create a simple table-style visualization
        fig = go.Figure()

        # Create a table showing the latest values
        headers = ["Metric", "Latest Value", "As of Date"]
        cell_values = [
            list(latest_values.keys()),
            [f"{v['value']:.2f}%" for v in latest_values.values()],
            [v["date"] for v in latest_values.values()],
        ]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=headers,
                    fill_color="#3498db",
                    font=dict(color="white", size=14),
                    align="center",
                    height=40,
                ),
                cells=dict(
                    values=cell_values,
                    fill_color=[["#f8f9fa", "#ecf0f1"] * len(latest_values)],
                    font=dict(color="#2c3e50", size=12),
                    align=["left", "center", "center"],
                    height=35,
                ),
            )
        )

        # Get title from registry metadata
        chart_meta = ChartRegistry.get_chart("overview")
        chart_title = chart_meta.title if chart_meta else "Market Overview"

        fig.update_layout(
            title=dict(
                text=chart_title,
                x=0.5,
                xanchor="center",
                font=dict(size=18),
                pad=dict(t=20),
            ),
            height=300,
            margin=dict(l=40, r=40, t=80, b=40),
            showlegend=False,
        )

        return fig

    def _get_latest_values(self) -> Dict[str, Dict[str, Any]]:
        """Extract latest values from time series data.

        Returns:
            Dictionary with latest values and dates for each series.
        """
        latest_values = {}

        # 30Y Mortgage Rate
        if "Mortgage30" in self.df.columns:
            mortgage_data = self.df["Mortgage30"].dropna()
            if not mortgage_data.empty:
                latest_values["30Y Mortgage Rate"] = {
                    "value": mortgage_data.iloc[-1],
                    "date": mortgage_data.index[-1].strftime("%Y-%m-%d"),
                }

        # 10Y Treasury Rate
        if "Treasury10Y" in self.df.columns:
            treasury_data = self.df["Treasury10Y"].dropna()
            if not treasury_data.empty:
                latest_values["10Y Treasury Rate"] = {
                    "value": treasury_data.iloc[-1],
                    "date": treasury_data.index[-1].strftime("%Y-%m-%d"),
                }

        # NMDB Quarterly Rate
        if "NMDB_QuarterlyRate" in self.df.columns:
            nmdb_data = self.df["NMDB_QuarterlyRate"].dropna()
            if not nmdb_data.empty:
                latest_values["Avg Outstanding Mortgage Rate"] = {
                    "value": nmdb_data.iloc[-1],
                    "date": nmdb_data.index[-1].strftime("%Y-%m-%d"),
                }

        # Calculate spreads if both rates are available
        if (
            "30Y Mortgage Rate" in latest_values
            and "10Y Treasury Rate" in latest_values
        ):
            spread = (
                latest_values["30Y Mortgage Rate"]["value"]
                - latest_values["10Y Treasury Rate"]["value"]
            )
            latest_values["Mortgage-Treasury Spread"] = {
                "value": spread,
                "date": latest_values["30Y Mortgage Rate"]["date"],
            }

        return latest_values
