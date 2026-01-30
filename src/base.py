# src/base.py
from __future__ import annotations
from typing import Optional
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

def fetch_html(url: str, timeout: int = 20, headers: Optional[dict] = None) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup parser."""
    h = DEFAULT_HEADERS.copy()
    if headers:
        h.update(headers)
    resp = requests.get(url, headers=h, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")