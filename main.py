import pandas as pd
from fredapi import Fred
import datetime, os
import plotly.graph_objects as go

fred = Fred(api_key=os.environ["FRED_API_KEY"])

end = datetime.date.today()
start = "2000-01-01"

dgs5 = fred.get_series("DGS5", start, end)
dgs10 = fred.get_series("DGS10", start, end)
mort30 = fred.get_series("MORTGAGE30US", start, end)

df = pd.concat([dgs5, dgs10, mort30], axis=1)
df.columns = ["5Y", "10Y", "Mortgage30"]
df["5s10s"] = df["10Y"] - df["5Y"]

# Save data
df.to_csv("spread_vs_mortgage.csv")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df.index, y=df["5s10s"],
    mode="lines", name="5s10s Spread",
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=df.index, y=df["Mortgage30"],
    mode="lines", name="Mortgage Rate",
    yaxis="y2"
))

fig.update_layout(
    title="5s10s Treasury Spread vs 30Y Mortgage Rate",
    xaxis=dict(title="Date"),
    yaxis=dict(title="5s10s Spread (bps)", side="left"),
    yaxis2=dict(title="Mortgage Rate (%)",
                overlaying="y", side="right",
                showgrid=False),
    hovermode="x unified"
)

# Save interactive HTML
fig.write_html("index.html", include_plotlyjs="cdn")

# Add download link for CSV
with open("index.html", "a") as f:
    f.write('<p><a href="spread_vs_mortgage.csv">Download CSV</a></p>')

