from __future__ import annotations
import os, pandas as pd
from datetime import datetime, timedelta
import smtplib, ssl
from email.mime.text import MIMEText
from . import config

def load_data():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "data.csv"))
    if not os.path.exists(data_path):
        return pd.DataFrame(columns=["date","type","company","headline","round","amount","investors","sector","county","source_url"])
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

def build_summary(df: pd.DataFrame) -> str:
    now = datetime.utcnow().date()
    recent = df[df["date"].dt.date >= (now - timedelta(days=7))]
    counts = recent["type"].value_counts().to_dict()
    def plural(word, n): return word if n == 1 else word + "s"
    parts = []
    for key in ["funding","hire","launch","award","general"]:
        n = counts.get(key, 0)
        parts.append(f"{n} {plural(key, n)}")
    line = ", ".join(parts)
    tops = recent.head(10)[["date","headline","company","source_url"]].fillna("")
    bullets = "\n".join([f"- {r.date.date()} — {r.headline} ({r.company}) — {r.source_url}" for r in tops.itertuples(index=False)])
    return f"""Weekly SD Ecosystem Summary
{line}

Highlights:
{bullets if bullets else "- No new items in the last 7 days."}
"""

def send_email(body: str):
    if not (config.MAIL_USER and config.MAIL_PASSWORD and config.MAIL_TO):
        print("[INFO] Email not configured; set MAIL_* envs to enable.")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "SD Ecosystem Weekly Summary"
    msg["From"] = config.MAIL_USER
    msg["To"] = ", ".join(config.MAIL_TO)

    context = ssl.create_default_context()
    with smtplib.SMTP(config.MAIL_SMTP_SERVER, config.MAIL_SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(config.MAIL_USER, config.MAIL_PASSWORD)
        server.sendmail(config.MAIL_USER, config.MAIL_TO, msg.as_string())
    print("[OK] Sent weekly summary email.")

def main():
    df = load_data()
    body = build_summary(df)
    print(body)
    send_email(body)

if __name__ == "__main__":
    main()
