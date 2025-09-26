"""SQLAlchemy v2 ORM models for macro_dashboard.

Schema principles:
- sources: external providers (FRED, NMDB)
- series: logical time series, with frequency + periodicity metadata
- observations: raw values with period_start/period_end and optional as_of (vintage)

Revisions strategy (v1):
- Keep latest value per (series_id, period_start).
- Track `as_of` date; on sync, we upsert and update when values change.
  Future versions can extend to full-vintage storage by including `as_of` in the PK.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(20))  # e.g., "FRED", "NMDB"
    base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    series: Mapped[list[Series]] = relationship(back_populates="source")


class Series(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))

    # Provider-specific code (e.g., FRED ID) and our alias
    code: Mapped[str] = mapped_column(String(64), index=True)  # provider code
    alias: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    frequency: Mapped[str] = mapped_column(String(2))  # D,W,M,Q,A
    is_periodic: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    source: Mapped[Source] = relationship(back_populates="series")
    observations: Mapped[list[Observation]] = relationship(
        back_populates="series", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("source_id", "code", name="uq_series_source_code"),
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id"), index=True)

    # Period semantics
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date] = mapped_column(Date)  # equals start if instantaneous

    value: Mapped[float] = mapped_column(Float)

    # As-of date for revision tracking (latest-only in v1)
    as_of: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    series: Mapped[Series] = relationship(back_populates="observations")

    __table_args__ = (
        UniqueConstraint("series_id", "period_start", name="uq_obs_series_period"),
    )

