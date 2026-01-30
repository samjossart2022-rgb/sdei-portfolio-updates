import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "SD Funding Tracker")

MAIL_SMTP_SERVER = os.getenv("MAIL_SMTP_SERVER", "smtp.gmail.com")
MAIL_SMTP_PORT = int(os.getenv("MAIL_SMTP_PORT", "587"))
MAIL_USER = os.getenv("MAIL_USER", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_TO = [e.strip() for e in os.getenv("MAIL_TO", "").split(",") if e.strip()]
