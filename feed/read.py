"""Read and card: read-only operations. The text comes from one fixed template.

A query never starts a fetch, never writes, and gives each item that matches.
"""

import sqlite3
from datetime import date

GROUPS = ("dated", "seasons and experiences", "not confirmed")
_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _day(day: date, weekday: bool = True) -> str:
    text = f"{day.day} {_MONTHS[day.month - 1]} {day.year}"
    return f"{_DAYS[day.weekday()]} {text}" if weekday else text


def _when(start: str, end: str) -> str:
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    return _day(start) if start == end else f"{_day(start)} - {_day(end)}"


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def what_is_on(db: sqlite3.Connection, registry: dict, place: str, start: date, end: date) -> dict:
    """Each live item of the place that has an occurrence in the window, start to end."""
    if end < start:
        raise ValueError("the window ends before it starts")
    # The place of an item is the place of a source that gives evidence for it.
    rows = db.execute(
        "SELECT i.id, i.kind, i.category, i.title, i.town, i.price_text, i.source_link, "
        "o.start_date, o.end_date, "
        "(SELECT count(DISTINCT p.source_id) FROM evidence e JOIN page p ON p.id = e.page_id "
        " WHERE e.item_id = i.id) "
        "FROM item i JOIN occurrence o ON o.item_id = i.id "
        "WHERE i.status = 'live' AND o.precision = 'day' "
        "AND o.start_date <= ? AND o.end_date >= ? "
        "AND EXISTS (SELECT 1 FROM evidence e JOIN page p ON p.id = e.page_id "
        " JOIN source s ON s.id = p.source_id WHERE e.item_id = i.id AND s.place = ?) "
        "ORDER BY o.start_date, o.end_date",
        (end.isoformat(), start.isoformat(), place),
    ).fetchall()

    cards = {}
    for item_id, kind, category, title, town, price, link, first, last, sources in rows:
        card = cards.setdefault(
            item_id,
            {
                "id": item_id,
                "kind": kind,
                "category": category,
                "title": title,
                "when": [],
                "confirmed": True,
                "town": town,
                "price": price or "not stated",
                "sources": sources,
                "source": link,
                "first": max(first, start.isoformat()),  # the first day in the window
            },
        )
        card["when"].append(_when(first, last))
    # Neutral order: the first day in the window, then the title, then the id.
    ordered = sorted(cards.values(), key=lambda c: (c.pop("first"), c["title"].casefold(), c["id"]))
    for card in ordered:
        card["when"] = ", ".join(card["when"])

    # Seasons and "not confirmed" are slice 0b.2. Until then those groups are empty.
    groups = [{"name": name, "cards": []} for name in GROUPS]
    groups[0]["cards"] = ordered
    categories = {}
    for card in ordered:
        categories[card["category"]] = categories.get(card["category"], 0) + 1
    counts = {
        "items": len(cards),
        "groups": {group["name"]: len(group["cards"]) for group in groups},
        "categories": dict(sorted(categories.items())),
    }
    as_of = (db.execute("SELECT max(fetched_at) FROM page").fetchone()[0] or "")[:10]
    data = {
        "place": place,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "as_of": as_of,
        "counts": counts,
        "groups": groups,
    }
    return {"data": data, "text": _text(registry["places"][place]["name"], start, end, data)}


def _text(place_name: str, start: date, end: date, data: dict) -> str:
    counts = data["counts"]
    by_group = " · ".join(f"{number} {name}" for name, number in counts["groups"].items())
    by_category = " · ".join(f"{name} {number}" for name, number in counts["categories"].items())
    window = f"{_day(start, False)} - {_day(end, False)}"
    lines = [
        f"what_is_on · {place_name} · {window} · as of {data['as_of']}",
        "",
        "counts",
        f"  in the window   {_count(counts['items'], 'item')}: {by_group}",
        f"  by category     {by_category or 'none'}",
    ]
    for group in data["groups"]:
        lines += ["", group["name"]]
        if not group["cards"]:
            lines.append("    none")
        for card in group["cards"]:
            state = "confirmed" if card["confirmed"] else "not confirmed"
            label = f"[{card['kind']} · {card['category']}] {card['title']}"
            sources = _count(card["sources"], "source")
            lines += [
                f"{label} · {card['when']} ({state}) · {card['town']}",
                f"    price: {card['price']} · {sources} · id {card['id']}",
                f"    source: {card['source']}",
            ]
    return "\n".join(lines) + "\n"
