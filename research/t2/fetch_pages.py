"""T2 step 1: save about 10 real sources into evals/pages/ as raw file + visible text.

Run: ./.venv/Scripts/python research/t2/fetch_pages.py
One request at a time, 2 seconds between requests. A page that is already saved is not
fetched again (delete its files to fetch it again).
"""

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from feed.render import html_to_text, pdf_to_text

PAGES = Path("evals/pages")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/json,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-ZA,en;q=0.9",
}
MEDIA = "https://whalecoast.info/wp-json/wp/v2/media"

# id, kind, url. kind: html | wp_page (WordPress page API) | pdf_latest (media API, then PDF)
SOURCES = [
    (
        "ot_monthly_pdf",
        "pdf_latest",
        (
            f"{MEDIA}?search=Events&mime_type=application/pdf&per_page=10&orderby=date&order=desc"
            "&_fields=id,date,source_url"
        ),
        "Tourism-",
    ),
    (
        "ot_yearly_pdf",
        "pdf_latest",
        (
            f"{MEDIA}?search=Cape-Whale-Coast-Events&per_page=5&orderby=date&order=desc"
            "&_fields=id,date,source_url"
        ),
        "Cape-Whale-Coast-Events",
    ),
    (
        "overstrand_weekend",
        "wp_page",
        "https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content",
        None,
    ),
    (
        "ht_festivals",
        "html",
        "https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/",
        None,
    ),
    ("ht_whale_watching", "html", "https://hermanus-tourism.co.za/whale-watching/", None),
    ("whale_festival", "html", "https://hermanuswhalefestival.co.za/", None),
    ("kalfiefees", "html", "https://kalfiefees-hermanus.co.za/", None),
    ("xplorio_events", "html", "https://xplorio.com/hermanus/en/things-to-do/events", None),
    ("wesgro_events_p1", "html", "https://www.wesgro.co.za/travel/events?q=hermanus", None),
    ("southern_right_charters", "html", "https://www.southernrightcharters.co.za/", None),
    ("white_shark_projects", "html", "https://www.whitesharkprojects.co.za/", None),
    # Second batch (2026-11-23): experience and season pages, the items closest to what
    # Magic Safari sells. URLs are from research/t9_experiences.md.
    ("x_marine_dynamics", "html", "https://www.sharkwatchsa.com/en/shark-cage-diving/", None),
    ("x_dyer_island_cruises", "html", "https://www.whalewatchsa.com/", None),
    ("x_hermanus_whale_cruises", "html", "https://www.hermanus-whale-cruises.co.za/", None),
    ("x_walker_bay_kayaking", "html", "https://walkerbayadventures.co.za/sea-kayaking/", None),
    ("x_creation_wines", "html", "https://www.creationwines.com/activities/", None),
    ("x_hamilton_russell", "html", "https://www.hamiltonrussellvineyards.com/", None),
    ("x_bouchard_finlayson", "html", "https://bouchardfinlayson.co.za/", None),
    ("x_grootbos", "html", "https://www.grootbos.com/en/experiences", None),
    ("x_heart_of_abalone", "html", "https://www.heartofabalone.co.za/", None),
    ("x_african_horse_company", "html", "https://www.africanhorseco.com/", None),
    (
        "x_ht_southern_right_whales",
        "html",
        "https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/",
        None,
    ),
    (
        "x_ht_whale_and_shark_viewing",
        "html",
        "https://hermanus-tourism.co.za/things-to-do/whale-and-shark-viewing/",
        None,
    ),
]


def get(client: httpx.Client, url: str) -> httpx.Response:
    time.sleep(2)
    return client.get(url)


def fetch_one(client: httpx.Client, sid: str, kind: str, url: str, name_part: str | None) -> dict:
    meta = {"id": sid, "kind": kind, "requested": url, "fetched_at": datetime.now(UTC).isoformat()}
    response = get(client, url)
    meta["status"] = response.status_code
    if response.status_code != 200:
        return meta

    if kind == "pdf_latest":
        rows = json.loads(response.text[response.text.index("[") :])
        rows = [r for r in rows if name_part in r["source_url"]]
        meta["media_rows"] = rows[:3]
        newest = rows[0]
        meta["url"] = newest["source_url"]
        meta["uploaded"] = newest["date"]
        pdf = get(client, newest["source_url"])
        meta["status"] = pdf.status_code
        if pdf.status_code != 200:
            return meta
        (PAGES / f"{sid}.pdf").write_bytes(pdf.content)
        text = pdf_to_text(pdf.content)
    elif kind == "wp_page":
        body = response.text
        (PAGES / f"{sid}.raw.txt").write_text(body, encoding="utf-8")
        page = json.loads(body[body.index('{"id"') :])  # odd result in T10: <style> before JSON
        meta["url"] = url
        meta["modified"] = page["modified"]
        meta["bytes_before_json"] = body.index('{"id"')
        text = page["title"]["rendered"] + "\n" + html_to_text(page["content"]["rendered"])
    else:
        (PAGES / f"{sid}.html").write_bytes(response.content)
        meta["url"] = str(response.url)
        text = html_to_text(response.text)

    (PAGES / f"{sid}.txt").write_text(text, encoding="utf-8")
    meta["text_chars"] = len(text)
    return meta


def main() -> int:
    PAGES.mkdir(parents=True, exist_ok=True)
    index_path = PAGES / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60) as client:
        for sid, kind, url, name_part in SOURCES:
            if (PAGES / f"{sid}.txt").exists():
                print(f"skip  {sid} (saved)")
                continue
            try:
                meta = fetch_one(client, sid, kind, url, name_part)
            except (httpx.HTTPError, ValueError, LookupError) as error:  # report, do not hide
                meta = {"id": sid, "requested": url, "error": f"{type(error).__name__}: {error}"}
            index[sid] = meta
            print(
                f"{meta.get('status', 'ERR')}  {sid}  chars={meta.get('text_chars')}  "
                f"{meta.get('url', '')} {meta.get('error', '')}"
            )
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
