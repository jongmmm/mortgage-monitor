"""Table component rendering latest values.

This is not a chart; it renders a Plotly Table from prepared values.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from ..registry import register_component


@register_component(
    name="overview_table",
    title="Market Overview",
    order=0,
    page="Overview",
    page_order=1,
)
class TableComponent:
    def __init__(self, df: pd.DataFrame):
        self.df = df  # columns: alias, title, value, date, unit

    def render(self) -> go.Figure:
        if self.df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data", x=0.5, y=0.5, xref="paper", yref="paper")
            return fig

        headers = ["Metric", "Latest Value", "As of Date"]
        value_fmt = [
            f"{v:.2f}{' ' + u if u else ''}" for v, u in zip(self.df["value"], self.df["unit"])
        ]
        cells = [
            list(self.df["title"]),
            value_fmt,
            [pd.to_datetime(d).strftime("%Y-%m-%d") for d in self.df["date"]],
        ]

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=headers,
                        fill_color="#34495e",
                        font=dict(color="white", size=14),
                        align="center",
                        height=36,
                    ),
                    cells=dict(
                        values=cells,
                        align=["left", "center", "center"],
                        height=32,
                    ),
                )
            ]
        )
        fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40))
        return fig

