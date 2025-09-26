"""Database engine/session helpers."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..config.settings import settings
from .models import Base


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def get_engine(echo: bool = False):
    _ensure_parent_dir(settings.DB_PATH)
    url = f"sqlite+pysqlite:///{settings.DB_PATH}"
    return create_engine(url, echo=echo)


def create_all(echo: bool = False) -> None:
    engine = get_engine(echo=echo)
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(echo: bool = False) -> Iterator[Session]:
    engine = get_engine(echo=echo)
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

