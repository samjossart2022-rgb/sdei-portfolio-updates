from __future__ import annotations
from bs4 import BeautifulSoup
from ... import base
from ...utils import make_row
def parse(url: str, meta: dict) -> list[dict]:
    """Best-effort parser for SBIR.gov awards search page.
    This may need tweaks if SBIR changes markup.
    """
    soup = base.fetch_html(url)
    items = []
    # Look for award cards/rows
    rows = soup.select(".views-row, .result-item, .node--type-award")
    for r in rows[:100]:
        headline_el = r.select_one("h3, h2, a")
        headline = (headline_el.get_text(strip=True) if headline_el else "SBIR Award")
        link = headline_el.get("href") if headline_el and headline_el.has_attr("href") else url
        if link.startswith("/"):
            from urllib.parse import urljoin
            link = urljoin(url, link)

        date_el = r.find("time")
        dt = date_el.get("datetime") if (date_el and date_el.has_attr("datetime")) else (date_el.get_text(strip=True) if date_el else "")

        company_el = r.select_one(".company, .views-field-title, .field--name-field-awardee")
        company = company_el.get_text(strip=True) if company_el else ""

        items.append(make_row(
            date=dt,
            type=meta.get("type","award"),
            company=company,
            headline=headline,
            round="",
            amount="",
            investors="",
            sector=meta.get("sector",""),
            county=meta.get("county",""),
            source_url=link
        ))
    return items
