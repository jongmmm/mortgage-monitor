"""Macro Dashboard application orchestrator.

Workflow:
1) Ensure DB schema exists
2) Sync predefined data from FRED/NMDB
3) Prepare and render components
4) Assemble dashboard HTML
"""

from __future__ import annotations

from typing import Dict

from .config.settings import settings
from .db.session import create_all, session_scope
from .data.loaders import sync_all
from .charts.factory import ComponentFactory
from .templates.dashboard import DashboardTemplate


class MacroDashboardApp:
    def setup(self) -> None:
        create_all()

    def update_database(self) -> None:
        with session_scope() as s:
            sync_all(s)

    def build_components(self) -> Dict[str, str]:
        factory = ComponentFactory()
        figures = factory.create_all()
        factory.save_all(figures, settings.OUTPUT_DIR)
        # Map titles to file names for embedding
        return {
            "Overview": "overview_table.html",
            "30Y vs 10Y + Spread": "mortgage_treasury_spread.html",
            "Current vs Outstanding + Spread": "lock_in_spread.html",
        }

    def build_dashboard(self) -> str:
        files = self.build_components()
        tmpl = DashboardTemplate()
        html = tmpl.generate_html(files)
        path = tmpl.save(html)
        return path


def main() -> None:  # pragma: no cover - CLI wrapper
    app = MacroDashboardApp()
    app.setup()
    app.update_database()
    path = app.build_dashboard()
    print(f"✅ Macro dashboard generated at: {path}")


if __name__ == "__main__":  # pragma: no cover
    main()

