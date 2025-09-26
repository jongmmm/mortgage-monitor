"""Query and preparation of plot payloads.

Chart functions should be dumb renderers. All data alignment and
frequency/period semantics live here. The payloads include styling hints
like line shape (e.g., 'hv' for period series), so charts do no processing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import Observation, Series


@dataclass(frozen=True)
class SeriesPayload:
    alias: str
    title: str
    frequency: str
    is_periodic: bool
    x: List[pd.Timestamp]
    y: List[float]
    line_shape: str  # 'linear' | 'hv'
    unit: str | None = None


def _to_payload(alias: str, ser: Series, rows: Sequence[Observation]) -> SeriesPayload:
    # For periodic series, we draw a step line. We pass start dates as x
    # and set shape='hv' so the renderer displays steps between periods.
    x = [pd.to_datetime(r.period_start) for r in rows]
    y = [float(r.value) for r in rows]
    line_shape = "hv" if ser.is_periodic else "linear"
    return SeriesPayload(
        alias=alias,
        title=ser.title,
        frequency=ser.frequency,
        is_periodic=ser.is_periodic,
        x=x,
        y=y,
        line_shape=line_shape,
        unit=ser.unit,
    )


def get_series(session: Session, alias: str) -> SeriesPayload:
    ser = session.execute(select(Series).where(Series.alias == alias)).scalar_one()
    rows = (
        session.execute(
            select(Observation)
            .where(Observation.series_id == ser.id)
            .order_by(Observation.period_start)
        )
        .scalars()
        .all()
    )
    return _to_payload(alias, ser, rows)


@dataclass(frozen=True)
class PreparedSpreadChart:
    top_series: List[SeriesPayload]  # exactly two series
    spread_series: SeriesPayload     # precomputed spread payload aligned to top domain


def prepare_spread_chart(session: Session, left_alias: str, right_alias: str) -> PreparedSpreadChart:
    left = get_series(session, left_alias)
    right = get_series(session, right_alias)

    # Align on union of timestamps using forward-fill at the DataFrame layer.
    # This is the sole place alignment occurs; chart does not process.
    df = pd.DataFrame({
        left.alias: pd.Series(left.y, index=pd.DatetimeIndex(left.x)),
        right.alias: pd.Series(right.y, index=pd.DatetimeIndex(right.x)),
    }).sort_index()
    df = df.ffill()

    spread = df[left.alias] - df[right.alias]
    spread_payload = SeriesPayload(
        alias=f"{left.alias}_minus_{right.alias}",
        title=f"{left.title} - {right.title}",
        frequency=left.frequency,  # arbitrary; visual only
        is_periodic=False,
        x=list(df.index.to_pydatetime()),
        y=[float(v) for v in spread.values],
        line_shape="linear",
        unit=left.unit,
    )

    return PreparedSpreadChart(top_series=[left, right], spread_series=spread_payload)


def latest_values(session: Session, aliases: Iterable[str]) -> pd.DataFrame:
    records = []
    for a in aliases:
        p = get_series(session, a)
        if p.x:
            records.append(
                {
                    "alias": a,
                    "title": p.title,
                    "value": p.y[-1],
                    "date": pd.to_datetime(p.x[-1]).date(),
                    "unit": p.unit,
                }
            )
    return pd.DataFrame.from_records(records)

