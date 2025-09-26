"""Spread chart component: top = two series, bottom = spread.

Rendering-only: expects pre-aligned payloads prepared by services.query.
"""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ...services.query import PreparedSpreadChart
from ..registry import register_component


@register_component(
    name="spread_chart",
    title="Spread Chart",
    order=1,
    page="Market Analysis",
    page_order=2,
)
class SpreadChartComponent:
    def __init__(self, prepared: PreparedSpreadChart, title: str | None = None):
        self.prepared = prepared
        self.custom_title = title

    def render(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Top Series", "Spread"),
            vertical_spacing=0.12,
            row_heights=[0.65, 0.35],
        )

        # Top two series
        for p in self.prepared.top_series:
            fig.add_trace(
                go.Scatter(
                    x=p.x,
                    y=p.y,
                    name=p.title,
                    mode="lines",
                    line=dict(width=2, shape=p.line_shape),
                ),
                row=1,
                col=1,
            )

        # Bottom spread
        s = self.prepared.spread_series
        fig.add_trace(
            go.Scatter(
                x=s.x,
                y=s.y,
                mode="lines",
                name="Spread",
                line=dict(width=1.2, color="rgba(95,39,205,0.7)"),
                fill="tozeroy",
                fillcolor="rgba(95,39,205,0.25)",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        title = self.custom_title or "Spread"
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor="center", font=dict(size=16)),
            height=520,
            hovermode="x unified",
            legend=dict(orientation="h", x=0.5, xanchor="center", y=1.02),
            margin=dict(l=40, r=40, t=80, b=60),
        )
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Level", row=1, col=1)
        fig.update_yaxes(title_text="Spread", row=2, col=1)
        return fig

