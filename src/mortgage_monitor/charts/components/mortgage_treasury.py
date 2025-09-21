"""30Y Mortgage vs 10Y Treasury comparison chart generation."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..registry import register_chart, ChartRegistry


@register_chart(
    name="mortgage_treasury",
    title="30Y Mortgage Rate vs 10Y Treasury Rate with Spread",
    data_dependencies=["Mortgage30", "Treasury10Y"],
    explanation="This chart shows the relationship between mortgage rates and 10Y Treasury rates.",
    data_sources=[
        {"name": "FRED: 30Y Mortgage Rate (MORTGAGE30US)", "url": "https://fred.stlouisfed.org/series/MORTGAGE30US"},
        {"name": "FRED: 10Y Treasury Rate (DGS10)", "url": "https://fred.stlouisfed.org/series/DGS10"}
    ],
    order=2
)
class MortgageTreasuryChart:
    """Chart showing 30Y mortgage rate vs 10Y Treasury rate with spread visualization."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with data.
        
        Args:
            df: DataFrame containing time series data.
        """
        self.df = df
    
    def create_chart(self) -> go.Figure:
        """Create mortgage vs treasury comparison chart with separate spread subplot.
        
        Returns:
            Plotly figure showing mortgage vs treasury rates with spread in separate subplots.
        """
        # Create subplots: top for rates comparison, bottom for spread
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Mortgage vs Treasury Rates", "Mortgage-Treasury Spread"),
            vertical_spacing=0.15,  # More space between subplots
            row_heights=[0.65, 0.35]  # Adjust proportions
        )
        
        # Get data with forward fill to align series
        mortgage_data = self.df["Mortgage30"].dropna() if "Mortgage30" in self.df.columns else pd.Series(dtype=float)
        treasury_data = self.df["Treasury10Y"].dropna() if "Treasury10Y" in self.df.columns else pd.Series(dtype=float)
        
        if not mortgage_data.empty and not treasury_data.empty:
            # Align data by reindexing to common dates and forward filling
            common_index = mortgage_data.index.union(treasury_data.index)
            mortgage_aligned = mortgage_data.reindex(common_index).ffill()
            treasury_aligned = treasury_data.reindex(common_index).ffill()
            
            # Calculate spread (mortgage - treasury)
            spread = mortgage_aligned - treasury_aligned
            spread = spread.dropna()
            
            # Add 30Y Mortgage Rate to top subplot
            fig.add_trace(
                go.Scatter(
                    x=mortgage_aligned.index,
                    y=mortgage_aligned.values,
                    mode="lines",
                    name="30Y Mortgage Rate",
                    line=dict(color="#e74c3c", width=2.5),
                    connectgaps=False
                ),
                row=1, col=1
            )
            
            # Add 10Y Treasury Rate to top subplot
            fig.add_trace(
                go.Scatter(
                    x=treasury_aligned.index,
                    y=treasury_aligned.values,
                    mode="lines",
                    name="10Y Treasury Rate",
                    line=dict(color="#3498db", width=2.5),
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
                        name="Mortgage-Treasury Spread",
                        line=dict(color="rgba(95, 39, 205, 0.6)", width=1),
                        fill="tozeroy",
                        fillcolor="rgba(95, 39, 205, 0.3)",
                        connectgaps=False,
                        showlegend=False  # Don't show in legend since it's in separate subplot
                    ),
                    row=2, col=1
                )
        
        # Get title from registry metadata
        chart_meta = ChartRegistry.get_chart("mortgage_treasury")
        chart_title = chart_meta.title if chart_meta else "30Y Mortgage vs 10Y Treasury Rate with Spread"
        # Add line break for better wrapping on narrow screens
        wrapped_title = chart_title.replace(" with ", "<br>with ")
        
        # Update layout
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
