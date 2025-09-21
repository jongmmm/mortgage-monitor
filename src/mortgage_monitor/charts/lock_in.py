"""NMDB vs Current Mortgage Rate chart generation."""

import pandas as pd
import plotly.graph_objects as go


class LockInChart:
    """Chart showing NMDB quarterly rate vs current mortgage rate."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with data.
        
        Args:
            df: DataFrame containing time series data.
        """
        self.df = df
    
    def create_chart(self) -> go.Figure:
        """Create lock-in effect chart.
        
        Returns:
            Plotly figure showing lock-in effect.
        """
        fig = go.Figure()
        
        # Add current mortgage rate (FRED MORTGAGE30US)
        mortgage_data = self.df[self.df["Mortgage30"].notna()] if "Mortgage30" in self.df.columns else pd.DataFrame()
        if not mortgage_data.empty:
            fig.add_trace(go.Scatter(
                x=mortgage_data.index,
                y=mortgage_data["Mortgage30"],
                mode="lines",
                name="Current 30Y Mortgage Rate",
                line=dict(color="red", width=2),
                connectgaps=False
            ))
        
        # Overlay FHFA NMDB quarterly average mortgage interest rate
        if "NMDB_QuarterlyRate" in self.df.columns:
            nmdb_quarterly = self.df["NMDB_QuarterlyRate"].dropna()
            if not nmdb_quarterly.empty:
                # Ensure chronologically ordered datetime index
                nmdb_quarterly = nmdb_quarterly.sort_index()
                fig.add_trace(
                    go.Scatter(
                        x=nmdb_quarterly.index,
                        y=nmdb_quarterly.values,
                        mode="lines+markers",
                        name="NMDB Avg Interest Rate (Quarterly)",
                        line=dict(color="blue", width=2),
                        marker=dict(size=4),
                        connectgaps=False,
                    )
                )
        
        fig.update_layout(
            title="NMDB Avg Mortgage Interest Rate (Quarterly) vs Current 30Y Rate",
            xaxis_title="Date",
            yaxis_title="Interest Rate (%)",
            height=420,
            hovermode="x unified",
            # Mobile-friendly legend with proper spacing
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            # Balanced margins - more space for legend
            margin=dict(l=40, r=40, t=60, b=85)
        )
        
        return fig
