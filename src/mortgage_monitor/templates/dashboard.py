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
        """Get charts section HTML dynamically from registry."""
        sections = []
        
        for chart_meta in ChartRegistry.get_all_charts():
            sections.append(self._render_chart_section(chart_meta))
        
        return "\n".join(sections)
    
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
                source_items.append(f'<li><a href="{source.url}" target="_blank">{source.name}</a></li>')
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
