"""Factory to create components using prepared data from DB."""

from __future__ import annotations

import os
from typing import Dict

import plotly.graph_objects as go

from ..config.settings import settings
from ..services.query import latest_values, prepare_spread_chart
from ..db.session import session_scope
from .registry import ComponentRegistry
from . import components  # noqa: F401 - ensure registrations


class ComponentFactory:
    def __init__(self) -> None:
        pass

    def create_all(self) -> Dict[str, go.Figure]:
        figures: Dict[str, go.Figure] = {}
        with session_scope() as s:
            # Table component (overview_table)
            lv = latest_values(s, [
                "Mortgage30",
                "Treasury10Y",
                "NMDB_QuarterlyRate",
            ])
            table_cls = ComponentRegistry.get("overview_table").component_class  # type: ignore
            table_fig = table_cls(lv).render()
            figures["overview_table"] = table_fig

            # Spread: (Mortgage30 vs Treasury10Y)
            prep = prepare_spread_chart(s, "Mortgage30", "Treasury10Y")
            spread_cls = ComponentRegistry.get("spread_chart").component_class  # type: ignore
            spread_fig = spread_cls(prep, title="30Y Mortgage vs 10Y Treasury with Spread").render()
            figures["mortgage_treasury_spread"] = spread_fig

            # Spread: (Mortgage30 vs NMDB_QuarterlyRate)
            prep2 = prepare_spread_chart(s, "Mortgage30", "NMDB_QuarterlyRate")
            spread_fig2 = spread_cls(prep2, title="Current vs Outstanding Mortgage Rates (Spread)").render()
            figures["lock_in_spread"] = spread_fig2

        return figures

    def save_all(self, figures: Dict[str, go.Figure], output_dir: str | None = None) -> None:
        out = output_dir or settings.OUTPUT_DIR
        os.makedirs(out, exist_ok=True)
        for name, fig in figures.items():
            fig.write_html(os.path.join(out, f"{name}.html"), include_plotlyjs="cdn")

