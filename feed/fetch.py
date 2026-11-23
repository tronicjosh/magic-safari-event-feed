"""Fetch: one page of the registry becomes its visible text. The kind of the page is data.

Kinds: `html` (the page itself), `wp_page` (the page data of a WordPress site), `pdf_latest`
(the media list of a WordPress site, then the newest PDF whose link holds `match`).
One request at a time, with a pause between two requests to one host. A fetch that fails
raises nothing: the result has the status and an empty text, and `error` says why.
"""

import json
import time
from datetime import UTC, datetime

import httpx
from pypdf.errors import PyPdfError

from feed.render import html_to_text, pdf_to_text

PAUSE = 2.0  # seconds between two requests to one host
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/json,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-ZA,en;q=0.9",
}
# What a request, an answer in a different format or a broken PDF can raise.
_FAILURES = (httpx.HTTPError, httpx.InvalidURL, PyPdfError, ValueError, LookupError, TypeError)
_last_request: dict[str, float] = {}  # host -> the time of the last request to it


def _get(client: httpx.Client, url: str) -> httpx.Response:
    host = httpx.URL(url).host
    if host in _last_request:
        wait = _last_request[host] + PAUSE - time.monotonic()
        if wait > 0:
            time.sleep(wait)
    try:
        return client.get(url)
    finally:
        _last_request[host] = time.monotonic()


def _text(client: httpx.Client, page: dict, result: dict) -> str:
    response = _get(client, page["url"])
    result["status"] = response.status_code
    if response.status_code != 200:
        return ""
    kind = page["kind"]
    if kind == "html":
        return html_to_text(response.text)
    if kind == "wp_page":
        body = response.text  # T10: the site sends a <style> block before the JSON
        data = json.loads(body[body.index('{"id"') :])
        return data["title"]["rendered"] + "\n" + html_to_text(data["content"]["rendered"])
    if kind == "pdf_latest":
        rows = json.loads(response.text[response.text.index("[") :])  # newest first
        links = [row["source_url"] for row in rows if page["match"] in row["source_url"]]
        if not links:
            raise LookupError(f"no PDF link holds {page['match']!r}")
        link = links[0]
        # The link is data of the site. It is followed only on the host of the registry page.
        if httpx.URL(link).host != httpx.URL(page["url"]).host:
            raise ValueError(f"the PDF link is on a different host: {link}")
        result["url"] = link
        pdf = _get(client, link)
        result["status"] = pdf.status_code
        return pdf_to_text(pdf.content) if pdf.status_code == 200 else ""
    raise ValueError(f"unknown page kind: {kind}")


def fetch_page(page: dict, client: httpx.Client | None = None) -> dict:
    """Fetch one registry page (id, url, kind). Returns url, text, fetched_at, status.

    `status` is the HTTP status of the last answer, or None when there was no answer.
    For `pdf_latest`, `url` is the link of the PDF. `client` is for tests.
    """
    result = {
        "url": page["url"],
        "text": "",
        "fetched_at": datetime.now(UTC).isoformat(),
        "status": None,
    }
    own = client or httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)
    try:
        result["text"] = _text(own, page, result)
    except _FAILURES as error:  # a fetch never stops the run; the report names the page
        result["url"] = page["url"]
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        if client is None:
            own.close()
    return result
