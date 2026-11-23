"""Update: a model answer for one page becomes rows, and only where the code checks pass.

An item is stored when its title and each of its date entries pass `verify_item`. A town,
a venue or a price that fails stays empty. An item that is not stored is named in the report
with the reason; nothing waits for a person. Each item is one savepoint, so an item that is
not stored leaves no row.
"""

import hashlib
import sqlite3
from datetime import UTC, date, datetime, timedelta

from feed.verify import WEEKDAYS, verify_item

EXPAND_MONTHS = 18  # a weekly rule becomes one row for each date, this far after the ingest
_WEEKDAY_NUMBER = {name: number for number, name in enumerate(WEEKDAYS)}


def _add_months(day: date, months: int) -> date:
    month = day.month - 1 + months
    year, month = day.year + month // 12, month % 12 + 1
    for last in (day.day, 30, 29, 28):
        try:
            return date(year, month, last)
        except ValueError:
            continue
    raise ValueError(day)


def _part(part: dict) -> date:
    return date(part["year"], part["month"], part["day"])


def _occurrences(when: dict, ingested: date) -> tuple[str, list[tuple[date, date]]] | None:
    """The value for the evidence row and the day ranges of one verified date entry."""
    kind = when["kind"]
    if kind == "date":
        start = _part(when["start"])
        return start.isoformat(), [(start, start)]
    if kind == "range":
        start, end = _part(when["start"]), _part(when["end"])
        return f"{start.isoformat()}/{end.isoformat()}", [(start, end)]
    if kind == "weekly":
        first = ingested + timedelta((_WEEKDAY_NUMBER[when["weekday"]] - ingested.weekday()) % 7)
        last = _add_months(ingested, EXPAND_MONTHS)
        days = [first + timedelta(weeks=n) for n in range((last - first).days // 7 + 1)]
        return f"weekly {when['weekday']}", [(day, day) for day in days if day <= last]
    return None  # "months" (season) is slice 0b.2


def _time_shape(whens: list[dict]) -> str:
    if len(whens) > 1 or whens[0]["kind"] == "weekly":
        return "repeating dates"
    return "run" if whens[0]["kind"] == "range" else "single date"


def _title(item: dict) -> str:
    try:
        return str(item["title"]["value"]) or "(no title)"
    except (TypeError, KeyError):
        return "(no title)"


def _store_item(db, item: dict, page_id: int, page: dict, source: dict, towns: dict, model: str):
    """Returns None when the item is stored, or the reason why it is not."""
    results = {result["field"]: result for result in verify_item(item, page["text"])}
    for field, result in results.items():
        if (field == "title" or field.startswith("when")) and not result["ok"]:
            return f"{field}: {result['reason']}"

    ingested = datetime.fromisoformat(page["fetched_at"])
    ingested = (ingested.astimezone(UTC) if ingested.tzinfo else ingested).date()
    whens = []
    for index, when in enumerate(item["when"]):
        found = _occurrences(when, ingested)
        if found is None:
            return f"when[{index}]: time kind {when['kind']} is not built yet"
        whens.append((when, *found))

    def passed(field: str) -> str | None:
        if field not in results or not results[field]["ok"]:
            return None
        # The price check proves only the numbers, so the price text is the quote itself.
        text = item[field]["quote" if field == "price" else "value"]
        return " ".join(text.split())

    # The default town is only for a page that states no town. A town that the page states
    # must pass the check and be a town of the place; if not, the item is not stored.
    town = passed("town")
    if "town" in results and town is None:
        return f"town: {results['town']['reason']}"
    if town is None:
        if not source.get("default_town"):
            return "town: not stated, and the source has no default town"
        town_of_item = source["default_town"]
    elif town.casefold() in towns:
        town_of_item = towns[town.casefold()]
    else:
        return f"town: {town} is not in the place"

    at = page["fetched_at"]
    item_id = db.execute(
        "INSERT INTO item (kind, title, town, time_shape, venue, price_text, source_link, "
        "first_seen, last_seen_at, last_verified) VALUES ('event', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            passed("title"),
            town_of_item,
            _time_shape([when for when, _, _ in whens]),
            passed("venue"),
            passed("price"),
            page["url"],
            at,
            at,
            at,
        ),
    ).lastrowid

    evidence = [
        (field, passed(field), item[field]["quote"], model)
        for field in ("title", "town", "venue", "price")
        if passed(field) is not None
    ]
    if town is None:
        evidence.append(("town", town_of_item, "", "registry default"))
    seen = set()
    for when, value, ranges in whens:
        time_text = " | ".join(when["quotes"])
        evidence.append(("when", value, time_text, model))
        new = [(start, end) for start, end in ranges if (start, end) not in seen]
        seen.update(new)
        db.executemany(
            "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text) "
            "VALUES (?, ?, ?, 'day', ?)",
            [(item_id, start.isoformat(), end.isoformat(), time_text) for start, end in new],
        )
    db.executemany(
        "INSERT INTO evidence (item_id, field, value, quote, page_id, model) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(item_id, field, value, quote, page_id, by) for field, value, quote, by in evidence],
    )
    return None


def ingest_answer(
    db: sqlite3.Connection, registry: dict, source_id: str, page: dict, answer: dict
) -> dict:
    """Store the items of one model answer for one page. Returns what was stored and what not.

    page: url, text, fetched_at, status. answer: model, items (the extraction format).
    """
    model, items = answer["model"], answer["items"]
    if not isinstance(items, list):
        raise TypeError("answer.items is not a list")
    source = next(source for source in registry["sources"] if source["id"] == source_id)
    towns = {town.casefold(): town for town in registry["places"][source["place"]]["towns"]}
    page_id = db.execute(
        "INSERT INTO page (source_id, url, content_hash, fetched_at, http_status, text) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            source_id,
            page["url"],
            hashlib.sha256(page["text"].encode("utf-8")).hexdigest(),
            page["fetched_at"],
            page.get("status"),
            page["text"],
        ),
    ).lastrowid

    report = {"stored": 0, "set_aside": []}
    for item in items:
        db.execute("SAVEPOINT item")
        try:
            reason = _store_item(db, item, page_id, page, source, towns, model)
        except (TypeError, KeyError, AttributeError, ValueError, OverflowError):
            reason = "malformed item"
        if reason is None:
            report["stored"] += 1
        else:
            db.execute("ROLLBACK TO item")
            report["set_aside"].append((_title(item), reason))
        db.execute("RELEASE item")
    db.commit()
    return report
