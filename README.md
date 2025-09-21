# Mortgage Monitor Dashboard

A simple dashboard that overlays FHFA NMDB quarterly average mortgage interest rates with current 30Y mortgage rates from FRED.

## 🏗️ Architecture

```
mortgage-monitor/
├── src/mortgage_monitor/           # Main package
│   ├── config/settings.py         # Application settings
│   ├── data/fetchers.py           # FRED and FHFA NMDB data fetching
│   ├── charts/
│   │   ├── lock_in.py             # NMDB vs Current Rate chart
│   │   └── factory.py             # Chart creation
│   ├── templates/dashboard.py      # HTML dashboard generation
│   └── app.py                     # Main application
├── data/                          # Data storage with subfolders
│   ├── fred/                      # FRED data files
│   └── nmdb/                      # NMDB data files
├── output/                        # Generated dashboard
└── main.py                        # Entry point
```

## 🚀 Features

- **NMDB Quarterly Data**: FHFA National Mortgage Database quarterly average interest rates
- **Current Mortgage Rates**: FRED 30Y mortgage rate data
- **Mobile-Friendly**: Responsive chart with horizontal legend
- **Data Organization**: Saves all interim data in organized subfolders

## 📊 Data Sources

- **FRED API**: MORTGAGE30US (30-Year Fixed Rate Mortgage Average)
- **FHFA NMDB**: Outstanding Mortgage Statistics (National, All Mortgages, Quarterly)

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.13+
- FRED API Key (required)

### Setup
1. Clone the repository
2. Install dependencies: `uv sync`
3. Set environment variable:
   ```bash
   export FRED_API_KEY="your_fred_api_key"
   ```

### Running the Dashboard
```bash
# Simple entry point
uv run python main.py
```

## 📁 Output

The application generates:
- `data/mortgage_dashboard_data.csv` - Combined dataset
- `data/fred/MORTGAGE30US.csv` - FRED mortgage rate data
- `data/nmdb/raw_nmdb.csv` - Full NMDB ZIP contents
- `data/nmdb/filtered_nmdb.csv` - Filtered national data
- `data/nmdb/quarterly_rate.csv` - Final quarterly rates
- `output/index.html` - Main dashboard
- `output/lock_in_chart.html` - Chart file

## 🔧 Development

### Code Quality
```bash
uv run ruff check --fix  # Lint and fix code
```

### Design Principles
- **Simplicity**: Minimal, focused functionality
- **Data Transparency**: All interim data saved with clear naming
- **Mobile-First**: Responsive design for narrow screens
- **DRY Code**: No over-engineering or unused features

## 📈 What the Chart Shows

- **Red Line**: Current 30Y mortgage rates (daily/weekly frequency from FRED)
- **Blue Line with Markers**: NMDB quarterly average interest rates (quarter-end dates)
- **Data Range**: 2013Q1 to present (NMDB availability)
- **Filtering**: National level, All Mortgages, using VALUE2 (effective rate)

## 🔍 Data Notes

- NMDB data uses `GEOLEVEL='National'` and `MARKET='All Mortgages'`
- VALUE2 column used (lower rate, likely net of fees/points)
- Quarterly dates represent quarter-end (e.g., 2025Q1 = 2025-03-31)
- Only complete quarters included (no partial year data)
