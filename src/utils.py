from __future__ import annotations
import hashlib
import pandas as pd
from datetime import datetime

COLUMNS = [
    "date", "type", "company", "headline", "round", "amount",
    "investors", "sector", "county", "source_url"
]

def make_row(**kwargs):
    row = {c: kwargs.get(c, "") for c in COLUMNS}
    # Coerce date to ISO YYYY-MM-DD
    dt = kwargs.get("date")
    if isinstance(dt, str):
        try:
            pd.to_datetime(dt)  # validate
        except Exception:
            dt = datetime.utcnow().date().isoformat()
    elif dt is None:
        dt = datetime.utcnow().date().isoformat()
    else:
        dt = pd.to_datetime(dt).date().isoformat()
    row["date"] = dt
    return row

def hash_row(row: dict) -> str:
    s = f"{row.get('headline','')}|{row.get('date','')}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    keys = df.apply(lambda r: f"{r.get('headline','')}|{r.get('date','')}", axis=1)
    return df.loc[keys.drop_duplicates().index]

def normalize_amount(text: str) -> str:
    # best-effort normalizer; leave as-is if ambiguous
    if not text:
        return ""
    return text.replace("$", "").replace(",", "").strip()
