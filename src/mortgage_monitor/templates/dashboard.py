"""HTML dashboard template generation."""

import datetime
from typing import Dict
from zoneinfo import ZoneInfo

from ..charts.registry import ChartRegistry


class DashboardTemplate:
    """Generates HTML dashboard template."""

    def __init__(self, metrics: Dict[str, float]):
        """Initialize with metrics data.

        Args:
            metrics: Dictionary of key metrics for display.
        """
        self.metrics = metrics

    def generate_html(self) -> str:
        """Generate complete HTML dashboard.

        Returns:
            Complete HTML string for dashboard.
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Mortgage Market Monitoring Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    {self._get_header()}
    {self._get_charts_section()}
</body>
</html>"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for the dashboard."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 1.2em;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 8px;
        }
        .metric {
            text-align: center;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .chart-container {
            margin-bottom: 40px;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-frame {
            width: 100%;
            height: 570px;
            border: none;
            border-radius: 5px;
            display: block;
        }
        .explanation {
            margin-top: 5px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 0 5px 5px 0;
        }
        .explanation ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .explanation li {
            margin-bottom: 5px;
        }
        h3 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h4 {
            color: #34495e;
            margin-top: 25px;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        
        /* Tab styles */
        .tabs-container {
            margin-top: 20px;
        }
        
        .tab-navigation {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        .tab-button {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px 8px 0 0;
            padding: 12px 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #495057;
            transition: all 0.3s ease;
            border-bottom: none;
            flex: 1;
            min-width: 120px;
        }
        
        .tab-button:hover {
            background: #e9ecef;
            color: #2c3e50;
        }
        
        .tab-button.active {
            background: #3498db;
            color: white;
            border-color: #3498db;
            box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3);
        }
        
        .page-content {
            display: none;
        }
        
        .page-content.active {
            display: block;
        }
        
        /* Mobile responsive design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .metrics {
                grid-template-columns: 1fr;
                gap: 15px;
                padding: 15px;
            }
            
            .tab-navigation {
                flex-direction: column;
                gap: 8px;
            }
            
            .tab-button {
                flex: none;
                min-width: auto;
                text-align: center;
                padding: 15px;
                font-size: 16px;
            }
            
            .chart-frame {
                height: 400px;
            }
            
            .chart-container {
                margin-bottom: 30px;
                padding: 15px;
            }
            
            .explanation {
                padding: 12px;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 10px;
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            .subtitle {
                font-size: 1em;
            }
            
            .chart-frame {
                height: 350px;
            }
            
            .metric-value {
                font-size: 1.5em;
            }
        }
        """

    def _get_header(self) -> str:
        """Get dashboard header HTML."""
        # Get current time in EST
        est_time = datetime.datetime.now(ZoneInfo("America/New_York"))
        current_time = est_time.strftime("%Y-%m-%d %H:%M:%S EST")
        return f"""
    <div class="container">
        <h1>🏠 Mortgage Market Monitor</h1>
        <p class="subtitle"> <small style="color: #95a5a6;">Last updated: {current_time}</small></p>
        """

    def _get_charts_section(self) -> str:
        """Get charts section HTML dynamically from registry with page support."""
        pages = ChartRegistry.get_charts_by_page()

        # If only one page (default), don't show tabs
        if len(pages) == 1 and "Overview" in pages:
            sections = []
            for chart_meta in pages["Overview"]:
                sections.append(self._render_chart_section(chart_meta))
            return "\n".join(sections)

        # Multiple pages - show tabs
        return self._render_tabbed_pages(pages)

    def _render_chart_section(self, chart_meta) -> str:
        """Render a single chart section.

        Args:
            chart_meta: Chart metadata from registry.

        Returns:
            HTML string for the chart section.
        """
        # Generate explanation points if available
        explanation_html = ""
        if chart_meta.explanation:
            explanation_html = f"<p>{chart_meta.explanation}</p>"

        # Generate data sources list
        data_sources_html = ""
        if chart_meta.data_sources:
            source_items = []
            for source in chart_meta.data_sources:
                source_items.append(
                    f'<li><a href="{source.url}" target="_blank">{source.name}</a></li>'
                )
            data_sources_html = f"""
            <h4>Data Sources</h4>
            <ul>
                {"".join(source_items)}
            </ul>"""

        return f"""
    <div class="chart-container">
        <iframe src="{chart_meta.name}_chart.html" class="chart-frame"></iframe>
        <div class="explanation">
            <h4>{chart_meta.title}</h4>
            {explanation_html}
            {data_sources_html}
        </div>
    </div>"""

    def _render_tabbed_pages(self, pages: Dict[str, list]) -> str:
        """Render tabbed interface for multiple pages.

        Args:
            pages: Dictionary mapping page names to chart lists.

        Returns:
            HTML string for tabbed interface.
        """
        # Use registry's page ordering instead of alphabetical
        page_names = ChartRegistry.get_page_names()

        # Generate tab navigation
        tab_nav = []
        for i, page_name in enumerate(page_names):
            active_class = "active" if i == 0 else ""
            tab_nav.append(
                f'<button class="tab-button {active_class}" onclick="showPage(\'{page_name}\')">{page_name}</button>'
            )

        # Generate page content
        page_content = []
        for i, (page_name, charts) in enumerate(
            [(name, pages[name]) for name in page_names]
        ):
            active_class = "active" if i == 0 else ""
            chart_sections = []
            for chart_meta in charts:
                chart_sections.append(self._render_chart_section(chart_meta))

            page_content.append(f"""
            <div id="page-{page_name}" class="page-content {active_class}">
                {"".join(chart_sections)}
            </div>""")

        return f"""
        <div class="tabs-container">
            <div class="tab-navigation">
                {"".join(tab_nav)}
            </div>
            {"".join(page_content)}
        </div>
        
        <script>
        function showPage(pageName) {{
            // Hide all pages
            const pages = document.querySelectorAll('.page-content');
            pages.forEach(page => page.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab-button');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected page
            const selectedPage = document.getElementById('page-' + pageName);
            selectedPage.classList.add('active');
            
            // Refresh iframes in the newly shown page to fix rendering issues
            const iframes = selectedPage.querySelectorAll('iframe');
            iframes.forEach(iframe => {{
                const src = iframe.src;
                iframe.src = '';
                setTimeout(() => {{ iframe.src = src; }}, 10);
            }});
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
        </script>"""
