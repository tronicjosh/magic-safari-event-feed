"""Ingest: the weekly run. registry -> fetch -> render -> hash -> extract -> verify -> store.

Only a page whose text changed goes to the model, so a run costs O(changed pages). The
report gives the measured tokens and cost of each page; nothing is estimated.

Run: python -m feed.ingest   (database: the environment variable FEED_DB, default feed.db)
"""

import hashlib
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import anthropic
import httpx

from feed.env import load_env
from feed.extract import extract
from feed.fetch import fetch_page
from feed.store import open_db
from feed.update import ingest_answer

MODEL = "claude-haiku-5-5"
REGISTRY = Path("registry.json")
RUNS = Path("runs/runs.md")
_MODEL_FAILURES = (anthropic.AnthropicError, httpx.HTTPError, ValueError, LookupError)


def _unchanged(db: sqlite3.Connection, url: str, text: str) -> bool:
    """True when the newest stored page of this URL has the same text."""
    newest = db.execute(
        "SELECT content_hash FROM page WHERE url = ? ORDER BY id DESC LIMIT 1", (url,)
    ).fetchone()
    return newest is not None and newest[0] == hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ingest_page(db, registry, source, page, fetch, extract, model, client) -> dict:
    line = {
        "source": source["id"],
        "page": page["id"],
        "url": page["url"],
        "fetched": False,
        "status": None,
        "changed": None,
        "stored": 0,
        "updated": 0,
        "set_aside": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
    }
    fetched = fetch(page)
    line["url"], line["status"] = fetched["url"], fetched["status"]
    if fetched.get("error"):
        line["error"] = fetched["error"]
    if fetched["status"] != 200 or not fetched["text"].strip():
        line.setdefault("error", "the page has no text")
        return line
    line["fetched"] = True

    line["changed"] = not _unchanged(db, fetched["url"], fetched["text"])
    if not line["changed"]:
        # No model call and no new row. The page still lists its items: they were seen.
        db.execute(
            "UPDATE item SET last_seen_at = ?, last_verified = ? WHERE id IN (SELECT e.item_id "
            "FROM evidence e WHERE e.page_id = (SELECT max(id) FROM page WHERE url = ?))",
            (fetched["fetched_at"], fetched["fetched_at"], fetched["url"]),
        )
        db.commit()
        return line

    towns = registry["places"][source["place"]]["towns"]
    try:
        answer = extract(
            client,
            model,
            page["id"],
            fetched["text"],
            towns,
            registry["bars"],
            registry.get("categories", []),
        )
    except _MODEL_FAILURES as error:  # one page must not stop the run or lose its report
        line["error"] = f"extract: {type(error).__name__}: {error}"
        return line
    for key in ("input_tokens", "output_tokens", "cost_usd"):
        line[key] = answer[key]
    if not isinstance(answer.get("items"), list):
        # A refusal or a cut answer. No page row is written, so the next run tries again.
        line["error"] = f"extract: no items, stop reason {answer.get('stop_reason')}"
        return line
    stored = ingest_answer(db, registry, source["id"], fetched, answer)
    for key in ("stored", "updated", "set_aside"):
        line[key] = stored[key]
    line["left_empty"] = stored.get("left_empty", [])
    return line


def run_ingest(
    db: sqlite3.Connection,
    registry: dict,
    fetch=fetch_page,
    extract=extract,
    model: str = MODEL,
    client=None,
) -> dict:
    """Run the ingest for each page of each source of the registry. Returns the report.

    fetch: page of the registry -> url, text, fetched_at, status (`feed.fetch.fetch_page`).
    extract: the signature of `feed.extract.extract`; `client` is its first argument.
    """
    report = {"started_at": datetime.now(UTC).isoformat(), "model": model, "pages": []}
    for source in registry["sources"]:
        for page in source.get("pages", []):
            report["pages"].append(
                _ingest_page(db, registry, source, page, fetch, extract, model, client)
            )
    pages = report["pages"]
    fetched = [page for page in pages if page["fetched"]]
    changed = [page for page in fetched if page["changed"]]
    report["totals"] = {
        "pages": len(pages),
        "fetched": len(fetched),
        "failed": len(pages) - len(fetched),
        "changed": len(changed),
        "unchanged": len(fetched) - len(changed),
        "extract_calls": sum(1 for page in pages if page["input_tokens"]),
        "stored": sum(page["stored"] for page in pages),
        "updated": sum(page["updated"] for page in pages),
        "set_aside": sum(len(page["set_aside"]) for page in pages),
        "input_tokens": sum(page["input_tokens"] for page in pages),
        "output_tokens": sum(page["output_tokens"] for page in pages),
        "cost_usd": round(sum(page["cost_usd"] for page in pages), 6),
    }
    return report


def format_report(report: dict) -> str:
    """The report as text: one line for each page, the items that were not stored, the totals."""
    lines = [f"Ingest {report['started_at']}  model {report['model']}"]
    for page in report["pages"]:
        name = f"{page['source']} / {page['page']}"
        if not page["fetched"]:
            lines.append(f"  FAILED     {name}  status {page['status']}  {page['error']}")
            continue
        if not page["changed"]:
            lines.append(f"  unchanged  {name}")
            continue
        lines.append(
            f"  changed    {name}  stored {page['stored']}  updated {page['updated']}  set aside {len(page['set_aside'])}  "
            f"tokens in {page['input_tokens']:,}  out {page['output_tokens']:,}  "
            f"cost {page['cost_usd']:.6f} USD" + (f"  {page['error']}" if "error" in page else "")
        )
        lines.extend(f"      set aside: {title}: {reason}" for title, reason in page["set_aside"])
        empty = page.get("left_empty", [])
        lines.extend(f"      field left empty: {title}: {reason}" for title, reason in empty)
    totals = report["totals"]
    lines.append(
        f"Totals: {totals['pages']} pages, {totals['failed']} failed, {totals['changed']} "
        f"changed, {totals['unchanged']} unchanged, {totals['extract_calls']} model calls. "
        f"Items stored {totals['stored']}, updated {totals['updated']}, set aside {totals['set_aside']}. "
        f"Tokens in {totals['input_tokens']:,}, out {totals['output_tokens']:,}. "
        f"Measured cost {totals['cost_usd']:.6f} USD."
    )
    return "\n".join(lines)


def run_line(report: dict) -> str:
    """One table row for runs/runs.md, in the columns of that file."""
    totals = report["totals"]
    failed = [page["page"] for page in report["pages"] if not page["fetched"]]
    cells = [
        report["started_at"][:10],
        (
            f"Ingest, {totals['pages']} pages: {totals['changed']} changed, "
            f"{totals['unchanged']} unchanged, {totals['failed']} failed"
        ),
        report["model"],
        f"{totals['input_tokens']:,}",
        f"{totals['output_tokens']:,}",
        f"{totals['cost_usd']:.6f}",
        str(totals["stored"] + totals["updated"] + totals["set_aside"]),
        f"{totals['stored']} new, {totals['updated']} updated",
        str(totals["set_aside"]),
        f"{totals['extract_calls']} model calls. Live: items stored. For review: items set "
        "aside, in the report only." + (f" Failed: {', '.join(failed)}." if failed else ""),
    ]
    return "| " + " | ".join(cells) + " |"


def main() -> int:
    load_env()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    db = open_db(os.environ.get("FEED_DB", "feed.db"), registry)
    report = run_ingest(
        db, registry, fetch=fetch_page, extract=extract, model=MODEL, client=anthropic.Anthropic()
    )
    print(format_report(report))
    before = RUNS.read_text(encoding="utf-8")
    with RUNS.open("a", encoding="utf-8") as runs:
        runs.write(("" if before.endswith("\n") else "\n") + run_line(report) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
