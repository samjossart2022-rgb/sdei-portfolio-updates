# South Dakota Funding & Ecosystem Tracker

A lightweight pipeline to track SD (and nearby) startup **fundings, hires, launches, awards**, save them to **Google Sheets**, and view them in a **Streamlit** dashboard. Optional weekly **email summary**.

## What you get
- **Scrapers** using `requests` + `BeautifulSoup` with a `sources.yaml` to add/remove sites.
- **Cleaner** that normalizes fields (Company, Round, Amount, Investors, Sector, Source URL, etc.).
- **CSV + Google Sheets** push (`gspread` with a service account).
- **Streamlit dashboard** with filters by sector, stage, county, month.
- **Weekly summary email** script (counts last 7 days).

---

## Quickstart

### 0) Create a virtual environment
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1) Configure environment
Copy `.env.example` to `.env` and fill values:
```
# Google Sheets
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json   # path to your Google SA JSON
GOOGLE_SHEET_NAME=SD Funding Tracker

# Email (optional, for weekly summary)
MAIL_SMTP_SERVER=smtp.gmail.com
MAIL_SMTP_PORT=587
MAIL_USER=you@example.com
MAIL_PASSWORD=your_app_password
MAIL_TO=recipient1@example.com,recipient2@example.com
```

**Google Sheets setup:**  
- Create a Service Account in Google Cloud → enable **Google Sheets API**.
- Download the JSON credentials file → save as `service_account.json` in project root (or set an absolute path).
- Share your Google Sheet (it will be created if missing) with the service account email (found inside the JSON).

### 2) Add sources
Edit `src/sources.yaml`. Start with a few press/news pages you care about. Examples are included and can be tweaked.

### 3) Run the pipeline
```bash
# 1) Scrape + clean + write CSV + update Google Sheet
python -m src.ingest

# 2) Run the Streamlit dashboard
streamlit run streamlit_app.py
```

### 4) Weekly auto-update (cron / Task Scheduler)
**Cron (Linux/macOS):**
```
# Every Friday at 8:00 AM Central
0 8 * * FRI cd /path/to/sd_funding_tracker && .venv/bin/python -m src.ingest >> logs.txt 2>&1
```
**Windows Task Scheduler:** create a weekly task that runs:
```
.path\to\sd_funding_tracker\.venv\Scripts\python.exe -m src.ingest
```

### 5) Send weekly email summary (optional)
```bash
python -m src.email_summary
```
Add this to cron right after the ingest if you want auto emails.

---

## Project structure
```
sd_funding_tracker/
├── data/
│   └── data.csv
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── ingest.py
│   ├── email_summary.py
│   ├── scraper/
│   │   ├── base.py
│   │   └── parsers/
│   │       ├── press_generic.py
│   │       └── sba_awards.py
│   ├── sources.yaml
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Notes
- The example parsers are simple and opinionated. Duplicate detection uses a hash on (headline + date).
- If a site offers an RSS feed, consider adding it here for simpler parsing.
- You can easily add parsers per domain if the HTML differs significantly.
