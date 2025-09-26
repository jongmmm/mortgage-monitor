"""Data loaders for FRED and NMDB that write to SQLite via ORM.

Design goals:
- Preserve frequency and period semantics in DB schema
- Upsert latest values (replace on revision) without expanding steps
- Keep loader concerns separate from chart rendering
"""

from __future__ import annotations

import io
import zipfile
from datetime import date, datetime
from typing import Iterable

import pandas as pd
import requests
from fredapi import Fred
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.models import Observation, Series, Source
from .registry import SeriesDef, iter_all_series


def _get_or_create_source(session: Session, name: str, kind: str, base_url: str | None) -> Source:
    src = session.execute(select(Source).where(Source.name == name)).scalar_one_or_none()
    if src:
        return src
    src = Source(name=name, kind=kind, base_url=base_url)
    session.add(src)
    session.flush()
    return src


def _get_or_create_series(session: Session, sdef: SeriesDef, source: Source) -> Series:
    ser = session.execute(
        select(Series).where(Series.alias == sdef.alias)
    ).scalar_one_or_none()
    if ser:
        return ser
    ser = Series(
        source_id=source.id,
        code=sdef.code,
        alias=sdef.alias,
        title=sdef.title,
        unit=sdef.unit,
        frequency=sdef.frequency,
        is_periodic=sdef.is_periodic,
        last_refreshed_at=None,
    )
    session.add(ser)
    session.flush()
    return ser


def upsert_observation(
    session: Session,
    series: Series,
    start: date,
    end: date,
    value: float,
    as_of: date | None,
) -> None:
    # Unique on (series_id, period_start)
    existing = session.execute(
        select(Observation).where(
            Observation.series_id == series.id,
            Observation.period_start == start,
        )
    ).scalar_one_or_none()

    if existing:
        # Update if changed
        changed = False
        if existing.value != value:
            existing.value = value
            changed = True
        if existing.period_end != end:
            existing.period_end = end
            changed = True
        if as_of and existing.as_of != as_of:
            existing.as_of = as_of
            changed = True
        if changed:
            existing.updated_at = datetime.utcnow()
    else:
        session.add(
            Observation(
                series_id=series.id,
                period_start=start,
                period_end=end,
                value=float(value),
                as_of=as_of,
            )
        )


def load_fred(session: Session, series_defs: Iterable[SeriesDef]) -> None:
    if not settings.FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is required to load FRED data")

    fred = Fred(settings.FRED_API_KEY)
    source = _get_or_create_source(
        session,
        name="FRED",
        kind="FRED",
        base_url="https://fred.stlouisfed.org/",
    )

    for sdef in series_defs:
        ser = _get_or_create_series(session, sdef, source)
        # Fetch pandas Series indexed by Timestamp
        ts = fred.get_series(sdef.code, settings.START_DATE, settings.END_DATE)
        ts = ts.dropna()
        for dt, val in ts.items():
            d = dt.date() if hasattr(dt, "date") else date.fromisoformat(str(dt))
            # Instantaneous: start=end=d
            upsert_observation(session, ser, d, d, float(val), as_of=date.today())
        ser.last_refreshed_at = datetime.utcnow()


def load_nmdb_quarterly_rate(session: Session, sdef: SeriesDef) -> None:
    source = _get_or_create_source(
        session,
        name="NMDB",
        kind="NMDB",
        base_url="https://www.fhfa.gov/",
    )
    ser = _get_or_create_series(session, sdef, source)

    url = "https://www.fhfa.gov/document/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip"
    r = requests.get(url, timeout=60)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        df = pd.read_csv(zf.open(csv_name))

    # Filter for National / All Mortgages / Average Interest Rate
    filtered = df.query(
        "GEOLEVEL=='National' and MARKET=='All Mortgages' and SERIESID=='AVE_INTRATE'"
    ).copy()
    val_col = "VALUE2" if "VALUE2" in filtered.columns else "VALUE1"
    period_raw = filtered["PERIOD"].astype(str).str.upper()
    year = period_raw.str.extract(r"(\d{4})")[0].astype(int)
    quarter = period_raw.str.extract(r"Q([1-4])")[0].astype(int)

    # Create proper quarterly period start/end
    pidx = pd.PeriodIndex(year.astype(str) + "Q" + quarter.astype(str), freq="Q-DEC")
    start_dates = pidx.to_timestamp(how="start").normalize().date
    end_dates = pidx.to_timestamp(how="end").normalize().date
    values = pd.to_numeric(filtered[val_col], errors="coerce")

    for s, e, v in zip(start_dates, end_dates, values):
        if pd.notna(v):
            upsert_observation(session, ser, s, e, float(v), as_of=date.today())
    ser.last_refreshed_at = datetime.utcnow()


def sync_all(session: Session) -> None:
    """Fetch all predefined series and upsert into DB."""
    fred_defs = [s for s in iter_all_series() if s.source == "FRED"]
    if fred_defs:
        load_fred(session, fred_defs)

    nmdb_defs = [s for s in iter_all_series() if s.source == "NMDB"]
    for sdef in nmdb_defs:
        load_nmdb_quarterly_rate(session, sdef)

