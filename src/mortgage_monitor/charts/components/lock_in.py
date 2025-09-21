"""NMDB vs Current Mortgage Rate chart generation."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..registry import register_chart, ChartRegistry


@register_chart(
    name="lock_in",
    title="Avg Outstanding Mortgage Interest Rate (Quarterly) vs Current 30Y Rate",
    data_dependencies=["Mortgage30", "NMDB_QuarterlyRate"],
    explanation="Compares the average mortgage interest rate from outstanding mortgages (NMDB quarterly data) with the current 30-year mortgage rate to show the lock-in effect.",
    data_sources=[
        {"name": "FRED: 30Y Mortgage Rate (MORTGAGE30US)", "url": "https://fred.stlouisfed.org/series/MORTGAGE30US"},
        {"name": "FHFA NMDB: Outstanding Mortgage Statistics", "url": "https://www.fhfa.gov/document/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip"}
    ],
    order=1
)
class LockInChart:
    """Chart showing NMDB quarterly rate vs current mortgage rate."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with data.
        
        Args:
            df: DataFrame containing time series data.
        """
        self.df = df
    
    def create_chart(self) -> go.Figure:
        """Create lock-in effect chart with separate spread subplot.
        
        Returns:
            Plotly figure showing NMDB vs current mortgage rates with spread in separate subplots.
        """
        # Create subplots: top for rates comparison, bottom for spread
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Current vs Outstanding Mortgage Rates", "Current-Outstanding Rate Spread"),
            vertical_spacing=0.15,  # More space between subplots
            row_heights=[0.65, 0.35]  # Adjust proportions
        )
        
        # Get data with forward fill to align series
        mortgage_data = self.df["Mortgage30"].dropna() if "Mortgage30" in self.df.columns else pd.Series(dtype=float)
        nmdb_data = self.df["NMDB_QuarterlyRate"].dropna() if "NMDB_QuarterlyRate" in self.df.columns else pd.Series(dtype=float)
        
        if not mortgage_data.empty and not nmdb_data.empty:
            # Align data by reindexing to common dates and forward filling
            common_index = mortgage_data.index.union(nmdb_data.index)
            mortgage_aligned = mortgage_data.reindex(common_index).ffill()
            nmdb_aligned = nmdb_data.reindex(common_index).ffill()
            
            # Calculate spread (current mortgage - outstanding mortgage)
            spread = mortgage_aligned - nmdb_aligned
            spread = spread.dropna()
            
            # Add current mortgage rate to top subplot
            fig.add_trace(
                go.Scatter(
                    x=mortgage_aligned.index,
                    y=mortgage_aligned.values,
                    mode="lines",
                    name="Current 30Y Mortgage Rate",
                    line=dict(color="red", width=2),
                    connectgaps=False
                ),
                row=1, col=1
            )
            
            # Add NMDB quarterly rate to top subplot
            fig.add_trace(
                go.Scatter(
                    x=nmdb_aligned.index,
                    y=nmdb_aligned.values,
                    mode="lines+markers",
                    name="NMDB Avg Interest Rate (Quarterly)",
                    line=dict(color="blue", width=2),
                    marker=dict(size=4),
                    connectgaps=False
                ),
                row=1, col=1
            )
            
            # Add spread as shaded area to bottom subplot
            if not spread.empty:
                fig.add_trace(
                    go.Scatter(
                        x=spread.index,
                        y=spread.values,
                        mode="lines",
                        name="Current-Outstanding Rate Spread",
                        line=dict(color="rgba(255, 99, 71, 0.6)", width=1),
                        fill="tozeroy",
                        fillcolor="rgba(255, 99, 71, 0.3)",
                        connectgaps=False,
                        showlegend=False  # Don't show in legend since it's in separate subplot
                    ),
                    row=2, col=1
                )
        
        # Get title from registry metadata
        chart_meta = ChartRegistry.get_chart("lock_in")
        chart_title = chart_meta.title if chart_meta else "NMDB vs Current 30Y Rate"
        # Add line break for better wrapping on narrow screens
        wrapped_title = chart_title.replace(" vs ", "<br>vs ")
        
        fig.update_layout(
            title=dict(
                text=wrapped_title,
                x=0.5,  # Center the title
                xanchor='center',
                font=dict(size=16),  # Larger font to match subplot titles
                pad=dict(t=15)  # More padding to prevent overlap
            ),
            height=520,  # Taller chart to use available space better
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.52,  # Position legend between subplots (after top chart)
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.5)"  # More transparent background
            ),
            # Adjust margins for better spacing
            margin=dict(l=40, r=40, t=80, b=60)
        )
        
        # Update subplot title font sizes to match main title
        fig.update_annotations(font_size=14)
        
        # Update x-axis titles for both subplots
        fig.update_xaxes(title_text="Date", row=2, col=1)  # Only bottom subplot gets x-axis title
        
        # Update y-axis titles for both subplots
        fig.update_yaxes(title_text="Interest Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Spread (%)", row=2, col=1)
        
        return fig
