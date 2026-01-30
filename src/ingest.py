from __future__ import annotations
import os, yaml, pandas as pd
from .utils import COLUMNS, drop_duplicates
from .scraper.parsers import press_generic, sba_awards
from . import config

PARSER_MAP = {
    "press_generic": press_generic.parse,
    "sba_awards": sba_awards.parse,
}

def load_sources():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "sources.yaml"), "r", encoding="utf-8") as f:
        y = yaml.safe_load(f)
    return y.get("sources", [])

def run_scrapers():
    rows = []
    for src in load_sources():
        parser_name = src.get("parser")
        url = src.get("url")
        if not parser_name or not url:
            continue
        parser = PARSER_MAP.get(parser_name)
        if not parser:
            print(f"[WARN] Unknown parser: {parser_name} ({url})")
            continue
        try:
            items = parser(url, src)
            rows.extend(items)
            print(f"[OK] {src.get('name','(unnamed)')} -> {len(items)} rows")
        except Exception as e:
            print(f"[ERR] {src.get('name','(unnamed)')} -> {e}")
    return rows

def write_csv_and_sheet(df: pd.DataFrame):
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "data.csv")
    df.to_csv(csv_path, index=False)
    print(f"[OK] Wrote CSV -> {csv_path}")
    # Google Sheets (best-effort; skip if no creds)
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(config.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
        gc = gspread.authorize(creds)
        try:
            sh = gc.open(config.GOOGLE_SHEET_NAME)
        except Exception:
            sh = gc.create(config.GOOGLE_SHEET_NAME)
        ws = sh.sheet1
        # Rebuild the sheet with selected columns for the public view
        public_cols = ["company", "round", "amount", "investors", "sector", "source_url"]
        ws.clear()
        if df.empty:
            ws.update([public_cols])
        else:
            ws.update([public_cols] + df[public_cols].fillna("").astype(str).values.tolist())
        print(f"[OK] Updated Google Sheet -> {config.GOOGLE_SHEET_NAME}")
    except Exception as e:
        print(f"[INFO] Skipping Google Sheets update: {e}")

def main():
    rows = run_scrapers()
    df = pd.DataFrame(rows, columns=COLUMNS)
    df = df.dropna(how="all").fillna("")
    df = df.sort_values(by=["date"], ascending=False, na_position="last")
    df = drop_duplicates(df)
    write_csv_and_sheet(df)

if __name__ == "__main__":
    main()
