# Mortgage Monitor Dashboard

A GitHub page dashboard updated daily.

🔗 **Live Dashboard**: [jongmmm.github.io/mortgage-monitor](https://jongmmm.github.io/mortgage-monitor)

## 📊 Data Sources

- **FRED API**: [MORTGAGE30US](https://fred.stlouisfed.org/series/MORTGAGE30US) - 30-Year Fixed Rate Mortgage Average
- **FHFA NMDB**: [Outstanding Mortgage Statistics](https://www.fhfa.gov/document/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip) - National, All Mortgages, Quarterly

## 🔍 Data Notes

- NMDB data uses `GEOLEVEL='National'` and `MARKET='All Mortgages'` and Values Weighted by Dollar Loan Volume
- Dashboard updates automatically via GitHub Actions
