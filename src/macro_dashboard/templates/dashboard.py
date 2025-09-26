"""Basic dashboard HTML template for macro_dashboard."""

from __future__ import annotations

import os
from typing import Dict

from ..config.settings import settings


class DashboardTemplate:
    def __init__(self) -> None:
        pass

    def generate_html(self, component_files: Dict[str, str]) -> str:
        # Create simple HTML embedding each component iframe
        parts = []
        parts.append("<h1>Macro Dashboard</h1>")
        for title, fname in component_files.items():
            parts.append(f"<h2>{title}</h2>")
            parts.append(
                f"<iframe src=\"{fname}\" style=\"width:100%;height:540px;border:none;\"></iframe>"
            )
        return "\n".join(parts)

    def save(self, html: str) -> str:
        out_dir = settings.OUTPUT_DIR
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, settings.DASHBOARD_FILE)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path

