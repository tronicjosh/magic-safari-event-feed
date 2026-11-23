"""Update: a model answer for one page becomes rows, and only where the code checks pass.

An item is stored when its title and each of its date entries pass `verify_item`. A town,
a venue or a price that fails stays empty. An item that is not stored is named in the report
with the reason; nothing waits for a person. Each item is one savepoint, so an item that is
not stored leaves no row.

An item that the database holds (the same source, town and title) is updated, not added.
An item that an answer does not hold is not touched, and no row is deleted.
"""

import hashlib
import sqlite3
from datetime import UTC, date, datetime, timedelta

from feed.extract import OUTSIDE
from feed.verify import WEEKDAYS, all_year, quote_on_page, verify_item

EXPAND_MONTHS = 18  # a weekly rule becomes one row for each date, this far after the ingest
SEASON_YEARS = 3  # a season with no year: a row for the year of the ingest and the next two
_WEEKDAY_NUMBER = {name: number for number, name in enumerate(WEEKDAYS)}
_LOGGED = ("price_text", "venue", "repeats_yearly")  # a new value of these is a change row


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


def _month_range(when: dict, year: int) -> tuple[date, date]:
    """The first day of the start month in this year, and the last day of the end month."""
    start, end = when["start"], when["end"]
    # An end month before the start month is in the next year (November to April).
    end_year = end["year"] or year + (end["month"] < start["month"])
    first_of_end = date(end_year, end["month"], 1)
    return date(year, start["month"], 1), _add_months(first_of_end, 1) - timedelta(1)


def _occurrences(when: dict, ingested: date) -> tuple[str, str, str | None, list] | str:
    """One verified date entry: the value for the evidence row, the precision, the rule and
    the day ranges. A text is the reason why the entry is not stored."""
    kind = when["kind"]
    if kind == "date":
        start = _part(when["start"])
        return start.isoformat(), "day", None, [(start, start)]
    if kind == "range":
        start, end = _part(when["start"]), _part(when["end"])
        return f"{start.isoformat()}/{end.isoformat()}", "day", None, [(start, end)]
    if kind == "weekly":
        if when.get("ongoing") is not True:
            return "the weekly rule is not marked as a rule with no end"
        first = ingested + timedelta((_WEEKDAY_NUMBER[when["weekday"]] - ingested.weekday()) % 7)
        last = _add_months(ingested, EXPAND_MONTHS)
        days = [first + timedelta(weeks=n) for n in range((last - first).days // 7 + 1)]
        return f"weekly {when['weekday']}", "day", "weekly", [(d, d) for d in days if d <= last]
    if kind == "months":
        months = f"months {when['start']['month']:02d} to {when['end']['month']:02d}"
        if when["start"]["year"]:
            first, last = _month_range(when, when["start"]["year"])
            if last < first:
                return "months: end is before start"
            return f"{months} from {first.year}", "month", None, [(first, last)]
        if when["end"]["year"]:
            return "months: an end year needs a start year"
        # A season with no year. The year is the only date that code writes without a quote.
        # From the season that is running at the ingest (it can have started last year) to
        # the season that starts two years after the ingest. A season that is over has no row.
        years = range(ingested.year - 1, ingested.year + SEASON_YEARS)
        ranges = [_month_range(when, year) for year in years]
        return (
            months,
            "month",
            "season",
            [(first, last) for first, last in ranges if last >= ingested],
        )
    return f"time kind {kind} is not known"


def _ingest_date(fetched_at: str) -> date:
    at = datetime.fromisoformat(fetched_at)
    return (at.astimezone(UTC) if at.tzinfo else at).date()


def extend_rules(db: sqlite3.Connection, url: str, fetched_at: str) -> None:
    """An unchanged page still states its rules. Write the dates that a later ingest adds:
    the next weeks of a weekly rule and the next years of a season. Nothing is deleted."""
    ingested = _ingest_date(fetched_at)
    rules = db.execute(
        "SELECT item_id, rule, time_text, max(start_date), max(end_date) FROM occurrence "
        "WHERE rule IS NOT NULL AND item_id IN (SELECT item_id FROM evidence WHERE page_id = "
        "(SELECT max(id) FROM page WHERE url = ?)) GROUP BY item_id, rule, time_text",
        (url,),
    ).fetchall()
    for item_id, rule, time_text, start, end in rules:
        start, end = date.fromisoformat(start), date.fromisoformat(end)
        new = []
        if rule == "weekly":
            last = _add_months(ingested, EXPAND_MONTHS)
            while (start := start + timedelta(7)) <= last:
                new.append((start, start, "day"))
        else:  # a season: the same months of the next year
            while start.year < ingested.year + SEASON_YEARS - 1:
                start = start.replace(year=start.year + 1)
                end = _add_months(date(end.year, end.month, 1), 13) - timedelta(1)
                new.append((start, end, "month"))
        db.executemany(
            "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text, rule) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(item_id, a.isoformat(), b.isoformat(), p, time_text, rule) for a, b, p in new],
        )


def _is_season(when: dict) -> bool:
    return when["kind"] == "months" and not when["start"]["year"]


def _time_shape(whens: list[dict]) -> str:
    if all(_is_season(when) for when in whens):
        return "season"
    if len(whens) > 1 or whens[0]["kind"] == "weekly":
        return "repeating dates"
    return "run" if whens[0]["kind"] in ("range", "months") else "single date"


def _title(item: dict) -> str:
    try:
        return str(item["title"]["value"]) or "(no title)"
    except (TypeError, KeyError):
        return "(no title)"


def _same_title(title: str) -> str:
    """The identity of a title: letter case and whitespace do not count."""
    return " ".join(title.split()).casefold()


def _yearly_quote(item: dict, text: str) -> str | None:
    """The quote for "held each year". It counts only when it is on the page. Every other
    answer, also one of a wrong type, is "not stated"."""
    yearly = item.get("yearly")
    if not isinstance(yearly, dict) or yearly.get("value") != "yes":
        return None
    quote = yearly.get("quote")
    return quote if isinstance(quote, str) and quote_on_page(quote, text) else None


def _check_item(item, page: dict, source: dict, towns, model: str, categories) -> dict | str:
    """The checks, with no write. Returns the values to store, or the reason why not."""
    checks = verify_item(item, page["text"], towns={*towns, OUTSIDE})
    results = {result["field"]: result for result in checks}
    for field, result in results.items():
        if (field == "title" or field.startswith("when")) and not result["ok"]:
            return f"{field}: {result['reason']}"

    ingested = _ingest_date(page["fetched_at"])
    # Months with no year are a season only with proof that the item is held each year. If
    # not, "October" in a calendar of one year would become October of three years.
    yearly = _yearly_quote(item, page["text"])
    if yearly is None and any(_is_season(when) and not all_year(when) for when in item["when"]):
        return "when: months with no year, and no proof on the page that it is held each year"
    whens = []
    for index, when in enumerate(item["when"]):
        found = _occurrences(when, ingested)
        if isinstance(found, str):
            return f"when[{index}]: {found}"
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
    elif town == OUTSIDE:
        return "town: outside the place"
    else:
        town_of_item = town

    # The soft bar of the registry: the item is stored, and shown in its own group. A "no"
    # counts only with a quote that is on the page.
    below_bar = None
    bar = item.get("traveller") or {}
    if bar.get("value") == "no" and quote_on_page(bar.get("quote") or "", page["text"]):
        below_bar = bar["quote"]

    evidence = [
        (field, passed(field), item[field]["quote"], model)
        for field in ("title", "town", "venue", "price")
        if passed(field) is not None
    ]
    if town is None:
        evidence.append(("town", town_of_item, "", "registry default"))
    if below_bar is not None:
        evidence.append(("traveller", "no", below_bar, model))
    if yearly is not None:
        evidence.append(("yearly", "yes", yearly, model))
    occurrences = []  # for each date entry: its evidence value and its rows
    for when, value, precision, rule, ranges in whens:
        time_text = " | ".join(" ".join(quote.split()) for quote in when["quotes"])
        evidence.append(("when", value, time_text, model))
        rows = [
            (start.isoformat(), end.isoformat(), precision, time_text, rule)
            for start, end in ranges
        ]
        occurrences.append((value, rows))

    # The category is a choice of the model from the list of the registry. A value that is
    # not in the list is stored as "other".
    category = item.get("category")
    category = category if isinstance(category, str) and category in categories else "other"

    time_shape = _time_shape([when for when, *_ in whens])
    return {
        # A venue or a price that failed its check: the item is stored with that field empty.
        "left_empty": [
            f"{field}: {results[field]['reason']}"
            for field in ("venue", "price")
            if field in results and not results[field]["ok"]
        ],
        "category": category,
        "kind": "season" if time_shape == "season" else "event",
        "title": passed("title"),
        "town": town_of_item,
        "below_bar": int(below_bar is not None),
        "time_shape": time_shape,
        "venue": passed("venue"),
        "price_text": passed("price"),
        "repeats_yearly": int(yearly is not None),
        "occurrences": occurrences,
        "evidence": evidence,
    }


def _find_item(db, source_id: str, new: dict, page_id: int) -> int | None:
    """The item with this identity: the same source, the same town and the same title.

    Two items of one page are never one item (two "Live Music" evenings), so an item that
    this page has given already is not a match. Of several matches, the one that shares a
    date with the new item is taken.
    """
    rows = db.execute(
        "SELECT DISTINCT i.id, i.title FROM item i JOIN evidence e ON e.item_id = i.id "
        "JOIN page p ON p.id = e.page_id WHERE p.source_id = ? AND i.town = ? "
        "AND i.id NOT IN (SELECT item_id FROM evidence WHERE page_id = ?) ORDER BY i.id",
        (source_id, new["town"], page_id),
    )
    same = [id for id, held in rows if _same_title(held) == _same_title(new["title"])]
    dates = {row[:2] for _, entry in new["occurrences"] for row in entry}
    for item_id in same:
        held = db.execute(
            "SELECT start_date, end_date FROM occurrence WHERE item_id = ?", (item_id,)
        )
        if dates & set(held):
            return item_id
    return same[0] if same else None


def _write_evidence(db, item_id: int, page_id: int, evidence: list) -> None:
    db.executemany(
        "INSERT INTO evidence (item_id, field, value, quote, page_id, model) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(item_id, field, value, quote, page_id, by) for field, value, quote, by in evidence],
    )


def _log_change(db, item_id: int, field: str, old, new, at: str) -> None:
    db.execute(
        "INSERT INTO change (item_id, field, old_value, new_value, found_at, actor) "
        "VALUES (?, ?, ?, ?, ?, 'ingest')",
        (item_id, field, None if old is None else str(old), str(new), at),
    )


def _write_item(db, new: dict, page_id: int, page: dict, source_id: str) -> str:
    """Add the item, or update the item with the same identity. Returns "stored" or "updated"."""
    at = page["fetched_at"]
    item_id = _find_item(db, source_id, new, page_id)
    if item_id is None:
        outcome = "stored"
        item_id = db.execute(
            "INSERT INTO item (kind, category, title, town, below_bar, time_shape, venue, "
            "price_text, repeats_yearly, source_link, first_seen, last_seen_at, last_verified) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                new["kind"],
                new["category"],
                new["title"],
                new["town"],
                new["below_bar"],
                new["time_shape"],
                new["venue"],
                new["price_text"],
                new["repeats_yearly"],
                page["url"],
                at,
                at,
                at,
            ),
        ).lastrowid
    else:
        outcome = "updated"
        db.execute(
            "UPDATE item SET last_seen_at = ?, last_verified = ? WHERE id = ?", (at, at, item_id)
        )
        old = db.execute(
            f"SELECT {', '.join(_LOGGED)}, source_link FROM item WHERE id = ?", (item_id,)
        ).fetchone()
        # Only the page that gave the item its fields can change them. A second page of the
        # source with a different wording ("Birkenhead" and "Birkenhead Brewery") is not a change.
        same_page = old[-1] == page["url"]
        for field, was in zip(_LOGGED, old, strict=False):
            # An empty value is "not stated on this page"; it never replaces a stored value.
            if same_page and new[field] and new[field] != was:
                db.execute(f"UPDATE item SET {field} = ? WHERE id = ?", (new[field], item_id))
                _log_change(db, item_id, field, was, new[field], at)

    held = set(
        db.execute(
            "SELECT start_date, end_date, precision FROM occurrence WHERE item_id = ?", (item_id,)
        )
    )
    # The date entries that the item has from an earlier page. A later date of the same weekly
    # rule or season is not a change; a new entry of an item that exists is.
    known = {
        value
        for (value,) in db.execute(
            "SELECT value FROM evidence WHERE item_id = ? AND field = 'when'", (item_id,)
        )
    }
    for value, rows in new["occurrences"]:
        added = [row for row in rows if row[:3] not in held]
        held.update(row[:3] for row in added)
        db.executemany(
            "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text, rule) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(item_id, *row) for row in added],
        )
        if outcome == "updated" and added and value not in known:
            _log_change(db, item_id, "when", None, value, at)
    _write_evidence(db, item_id, page_id, new["evidence"])
    return outcome


def ingest_answer(
    db: sqlite3.Connection, registry: dict, source_id: str, page: dict, answer: dict
) -> dict:
    """Store the items of one model answer for one page. Returns what was stored, what was
    updated and what not.

    page: url, text, fetched_at, status. answer: model, items (the extraction format).
    """
    model, items = answer["model"], answer["items"]
    if not isinstance(items, list):
        raise TypeError("answer.items is not a list")
    source = next(source for source in registry["sources"] if source["id"] == source_id)
    towns = registry["places"][source["place"]]["towns"]
    categories = registry.get("categories", [])
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

    report = {"stored": 0, "updated": 0, "set_aside": []}
    for item in items:
        db.execute("SAVEPOINT item")
        try:
            new = _check_item(item, page, source, towns, model, categories)
            reason = new if isinstance(new, str) else None
            outcome = None if reason else _write_item(db, new, page_id, page, source_id)
        except (TypeError, KeyError, AttributeError, ValueError, OverflowError):
            reason, outcome = "malformed item", None
        if outcome:
            report[outcome] += 1
            for empty in new["left_empty"]:  # the key is in the report only when there is one
                report.setdefault("left_empty", []).append((new["title"], empty))
        else:
            db.execute("ROLLBACK TO item")
            report["set_aside"].append((_title(item), reason))
        db.execute("RELEASE item")
    db.commit()
    return report
