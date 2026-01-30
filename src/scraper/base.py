from __future__ import annotations
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SD-Funding-Tracker/1.0)"
}

def fetch_html(url: str, timeout: int = 20) -> BeautifulSoup:
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")
