"""Read and card: read-only operations. The text comes from one fixed template.

A query never starts a fetch, never writes, and gives each item that matches. A date that no
page states is never shown: an item that is held each year and has no new dates is shown as
"not confirmed", with its last real dates.
"""

import sqlite3
from datetime import date

CHANGE_GROUPS = ("new", "changed")
GROUPS = ("dated", "seasons and experiences", "not confirmed", "below the traveller bar")
PLAN_GROUPS = ("seasons and experiences", "yearly with a date", "not confirmed")
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

# The columns of an item for a short card, then the columns of one occurrence.
_ITEM = (
    "i.id, i.kind, i.category, i.title, i.town, i.price_text, i.source_link, i.below_bar, "
    "i.repeats_yearly, i.first_seen, "
    "(SELECT count(DISTINCT p.source_id) FROM evidence e JOIN page p ON p.id = e.page_id "
    " WHERE e.item_id = i.id)"
)
_N = 11  # the number of item columns
_OCCURRENCE = "o.start_date, o.end_date, o.precision, o.rule, o.time_text"


def _line(text) -> str:
    """Third-party text goes into the response as data, on one line."""
    return " ".join(str(text).split())


def _day(day: date, weekday: bool = True) -> str:
    text = f"{day.day} {_MONTHS[day.month - 1]} {day.year}"
    return f"{_DAYS[day.weekday()]} {text}" if weekday else text


def _when(start: str, end: str) -> str:
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    return _day(start) if start == end else f"{_day(start)} - {_day(end)}"


def _months(start: str, end: str, year: bool) -> str:
    """The months of a month row. The year is shown only when the page states it."""
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    first, last = _MONTHS[start.month - 1], _MONTHS[end.month - 1]
    one = (start.year, start.month) == (end.year, end.month)
    if not year:
        if (start.month, end.month) == (1, 12):
            return "All year"
        return first if one else f"{first} - {last}"
    if one:
        return f"{first} {start.year}"
    if start.year == end.year:
        return f"{first} - {last} {end.year}"
    return f"{first} {start.year} - {last} {end.year}"


def _months_of(start: str, end: str) -> set[int]:
    """The numbers of the calendar months that a row covers."""
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    count = (end.year - start.year) * 12 + end.month - start.month + 1
    return {(start.month - 1 + n) % 12 + 1 for n in range(min(count, 12))}


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _as_of(db: sqlite3.Connection) -> str:
    return (db.execute("SELECT max(fetched_at) FROM page").fetchone()[0] or "")[:10]


def _rows(db: sqlite3.Connection, place: str, where: str, values: tuple = ()) -> list:
    """Item and occurrence columns of each live item of the place, in the order of the dates."""
    # The place of an item is the place of a source that gives evidence for it.
    return db.execute(
        f"SELECT {_ITEM}, {_OCCURRENCE} FROM item i JOIN occurrence o ON o.item_id = i.id "
        "WHERE i.status = 'live' "
        "AND EXISTS (SELECT 1 FROM evidence e JOIN page p ON p.id = e.page_id "
        " JOIN source s ON s.id = p.source_id WHERE e.item_id = i.id AND s.place = ?) "
        f"AND {where} ORDER BY o.start_date, o.end_date, o.id",
        (place, *values),
    ).fetchall()


def _card(row) -> dict:
    item_id, kind, category, title, town, price, link, below, yearly, seen, sources = row[:_N]
    return {
        "id": item_id,
        "kind": kind,
        "category": category,
        "title": _line(title),
        "when": [],
        "confirmed": True,
        "range": False,
        "rule": None,  # the quote of a weekly rule, if code wrote a date from it
        "season": False,  # a page states the months and no year; code wrote the year
        "season_quote": None,  # the quote of those months: the designer sees the proof
        "below_bar": bool(below),
        "yearly": bool(yearly),
        "town": _line(town),
        "price": _line(price or "") or "not stated",
        "sources": sources,
        "source": _line(link),
        "first_seen": seen[:10],
        "changed": None,  # the latest change row, if there is one
    }


def _add(card: dict, occurrence) -> None:
    """Add one real occurrence row to a card."""
    first, last, precision, rule, time_text = occurrence
    if precision == "month":
        text = _months(first, last, year=rule is None)
        if rule is not None:
            card["season"], card["season_quote"] = True, _line(time_text)
    else:
        text = _when(first, last)
        card["range"] = card["range"] or first != last
        if rule:
            card["rule"] = _line(time_text)
    if text not in card["when"]:
        card["when"].append(text)


def _last_held(card: dict, occurrence, as_of: str) -> None:
    """The card of a yearly item with no new dates: its last real dates, and no other date."""
    first, last, precision, _rule, _ = occurrence
    text = _months(first, last, year=True) if precision == "month" else _when(first, last)
    # Dates that are not past were not "held": they are the last dates that a page states.
    card["when"] = [f"{'Last held' if last < as_of else 'Last stated dates'} {text}"]
    card["confirmed"] = False


def _state(card: dict) -> str:
    if not card["confirmed"]:
        return "not confirmed"
    if card["rule"]:  # code wrote the date from a rule; the designer sees the proof
        return f'weekly rule: "{card["rule"]}"'
    if card["season"]:
        return f'season, no year stated: "{card["season_quote"]}"'
    if card["range"]:  # the page gives a first and a last day, not each day
        return "confirmed; a range, each day is not stated"
    return "confirmed"


def _changes(db: sqlite3.Connection, item_id: int, since: str = "") -> list[dict]:
    """The change rows of an item that were found on or after a date, the oldest first."""
    rows = db.execute(
        "SELECT field, old_value, new_value, found_at, actor FROM change "
        "WHERE item_id = ? AND substr(found_at, 1, 10) >= ? ORDER BY found_at, id",
        (item_id, since),
    ).fetchall()
    return [
        {"field": field, "old": old, "new": new, "found_at": at[:10], "actor": actor}
        for field, old, new, at, actor in rows
    ]


def _change_text(change: dict) -> str:
    new = "nothing" if change["new"] is None else f'"{_line(change["new"])}"'
    if change["old"] is None:
        return f"{change['found_at']}: {_line(change['field'])} added {new}"
    return f'{change["found_at"]}: {_line(change["field"])} "{_line(change["old"])}" -> {new}'


def _finish(db: sqlite3.Connection, card: dict) -> dict:
    card["when"] = ", ".join(card["when"])
    card["state"] = _state(card)
    card["changed"] = (_changes(db, card["id"]) or [None])[-1]
    return card


def _shift(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:  # 29 February
        return day.replace(year=day.year + years, day=28)


def _moved_into(first: str, last: str, start: date, end: date) -> date | None:
    """The first day in the window of the row moved by 1 or more whole years, or None.

    The result is used for the order of the cards only. It is never shown.
    """
    first, last = date.fromisoformat(first), date.fromisoformat(last)
    for years in range(1, end.year - first.year + 1):
        if _shift(first, years) <= end and _shift(last, years) >= start:
            return max(_shift(first, years), start)
    return None


def _holes(registry: dict, places: list[str]) -> dict:
    """What the feed does not have: from the registry only."""
    return {
        "sources": {
            place: sum(1 for source in registry["sources"] if source["place"] == place)
            for place in places
        },
        "not_collected": [
            {"name": row["name"], "reason": row["reason"], "declares": row.get("declares")}
            for row in registry.get("not_collected", [])
        ],
    }


def _holes_lines(registry: dict, holes: dict) -> list[str]:
    lines = ["", "holes"]
    for place, number in holes["sources"].items():
        name = _line(registry["places"][place]["name"])
        lines.append(f"  sources         {_count(number, 'source')} in the registry for {name}")
    for row in holes["not_collected"]:
        declares = f" (declares {_line(row['declares'])})" if row["declares"] else ""
        lines.append(f"  not collected   {_line(row['name'])}: {_line(row['reason'])}{declares}")
    if not holes["not_collected"]:
        lines.append("  not collected   none")
    return lines


def _counts(cards: list[dict], groups: dict[str, int]) -> dict:
    categories = {}
    for card in cards:
        categories[card["category"]] = categories.get(card["category"], 0) + 1
    return {"items": len(cards), "groups": groups, "categories": dict(sorted(categories.items()))}


def _counts_lines(counts: dict, scope: str) -> list[str]:
    by_group = " · ".join(f"{number} {name}" for name, number in counts["groups"].items())
    by_category = " · ".join(f"{name} {number}" for name, number in counts["categories"].items())
    return [
        "counts",
        f"  {scope:<16}{_count(counts['items'], 'item')}: {by_group}",
        f"  by category     {by_category or 'none'}",
    ]


def _card_lines(card: dict, mark_below: bool = False, changes: list | None = None) -> list[str]:
    """The short card. `changes` replaces the line of the latest change."""
    when = f"{card['when']} ({card['state']})" if card["state"] else card["when"]
    if not card["confirmed"]:  # the last real dates; no date is given for this period
        when = f"not confirmed ({card['when']})"
    below = " · below the traveller bar" if mark_below and card["below_bar"] else ""
    if changes is None:
        changes = [card["changed"]] if card["changed"] else []
    return [
        f"[{card['kind']} · {card['category']}] {card['title']} · {when} · {card['town']}{below}",
        (
            f"    price: {card['price']} · {_count(card['sources'], 'source')} · "
            f"first seen {card['first_seen']} · id {card['id']}"
        ),
        *(f"    changed {_change_text(change)}" for change in changes),
        f"    source: {card['source']}",
    ]


def what_is_on(db: sqlite3.Connection, registry: dict, place: str, start: date, end: date) -> dict:
    """Each live item of the place that has an occurrence in the window, start to end."""
    if end < start:
        raise ValueError("the window ends before it starts")
    cards, first_day = {}, {}
    # A day row and a month row match alike: the range of the row overlaps the window.
    in_window = _rows(
        db, place, "o.start_date <= ? AND o.end_date >= ?", (end.isoformat(), start.isoformat())
    )
    for row in in_window:
        if row[0] not in cards:
            cards[row[0]] = _card(row)
            first_day[row[0]] = max(row[_N], start.isoformat())  # the first day in the window
        _add(cards[row[0]], row[_N:])

    # Held each year, and no row in the window: if the latest real dates, moved by whole
    # years, overlap the window, the item is "not confirmed". No other item is projected.
    latest = {row[0]: row for row in _rows(db, place, "i.repeats_yearly = 1")}
    for item_id, row in latest.items():
        moved = None if item_id in cards else _moved_into(row[_N], row[_N + 1], start, end)
        if moved is not None:
            cards[item_id] = _card(row)
            _last_held(cards[item_id], row[_N:], _as_of(db))
            first_day[item_id] = moved.isoformat()

    # Neutral order: the first day in the window, then the title, then the id.
    ordered = sorted(
        (_finish(db, card) for card in cards.values()),
        key=lambda card: (first_day[card["id"]], card["title"].casefold(), card["id"]),
    )
    groups = [{"name": name, "cards": []} for name in GROUPS]
    for card in ordered:
        if card["below_bar"]:
            group = 3
        elif not card["confirmed"]:
            group = 2
        else:
            group = 1 if card["kind"] != "event" else 0
        groups[group]["cards"].append(card)
    data = {
        "place": place,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "as_of": _as_of(db),
        "counts": _counts(ordered, {group["name"]: len(group["cards"]) for group in groups}),
        "groups": groups,
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    window = f"{_day(start, False)} - {_day(end, False)}"
    lines = [f"what_is_on · {place_name} · {window} · as of {data['as_of']}", ""]
    lines += _counts_lines(data["counts"], "in the window")
    for group in groups:
        lines += ["", group["name"]]
        if not group["cards"]:
            lines.append("    none")
        for card in group["cards"]:
            lines += _card_lines(card)
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}


def when_to_go(
    db: sqlite3.Connection,
    registry: dict,
    place: str,
    from_month: int | None = None,
    to_month: int | None = None,
) -> dict:
    """For a trip with no dates: the seasons and the yearly items of the place, by month.

    One of the two months alone is a range of that one month. A range can go over the year
    end (11 to 2). An event that is not held each year is not listed.
    """
    first = from_month if from_month is not None else to_month
    last = to_month if to_month is not None else from_month
    if first is None:
        first, last = 1, 12
    if not all(isinstance(month, int) and 1 <= month <= 12 for month in (first, last)):
        raise ValueError("a month is a number from 1 to 12")
    numbers = [(first - 1 + n) % 12 + 1 for n in range((last - first) % 12 + 1)]

    as_of = _as_of(db)
    items = {}
    for row in _rows(db, place, "(i.kind != 'event' OR i.repeats_yearly = 1)"):
        items.setdefault(row[0], []).append(row)
    listed = []  # (group, card, the months that the item covers)
    for rows in items.values():
        card = _card(rows[0])
        if card["kind"] != "event":
            group, shown = 0, rows
        else:
            # A real date that is not past is shown. If there is none: the last real dates.
            group, shown = 1, [row for row in rows if row[_N + 1] >= as_of]
        if shown:
            for row in shown:
                _add(card, row[_N:])
        else:
            group, shown = 2, rows[-1:]
            _last_held(card, rows[-1][_N:], as_of)
        covers = set().union(*(_months_of(row[_N], row[_N + 1]) for row in shown))
        if covers & set(numbers):
            listed.append((group, _finish(db, card), covers))
    listed.sort(key=lambda entry: (entry[0], entry[1]["title"].casefold(), entry[1]["id"]))

    months = [
        {
            "month": number,
            "name": _MONTHS[number - 1],
            "cards": [card for _, card, covers in listed if number in covers],
        }
        for number in numbers
    ]
    groups = {
        name: sum(1 for group, _, _ in listed if group == index)
        for index, name in enumerate(PLAN_GROUPS)
    }
    data = {
        "place": place,
        "from_month": first,
        "to_month": last,
        "as_of": as_of,
        "counts": _counts([card for _, card, _ in listed], groups),
        "months": months,
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    span = _MONTHS[first - 1] if first == last else f"{_MONTHS[first - 1]} - {_MONTHS[last - 1]}"
    lines = [f"when_to_go · {place_name} · {span} · as of {as_of}", ""]
    lines += _counts_lines(data["counts"], "in the months")
    for month in months:
        lines += ["", month["name"]]
        if not month["cards"]:
            lines.append("    none")
        for card in month["cards"]:
            lines += _card_lines(card, mark_below=True)
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}


def _full_when(occurrences: list) -> list[str]:
    """Each occurrence of an item. The dates of a weekly rule are one line: the rule."""
    lines, rules = [], {}
    for first, last, precision, rule, time_text in occurrences:
        if precision == "day" and rule:
            if time_text not in rules:
                rules[time_text] = [len(lines), 0, first, last]
                lines.append("")
            rules[time_text][1] += 1
            rules[time_text][3] = last
            continue
        card = {"when": [], "confirmed": True, "range": False, "rule": None, "season": False}
        card["season_quote"] = None
        _add(card, (first, last, precision, rule, time_text))
        line = f"{card['when'][0]} ({_state(card)})"
        if line not in lines:
            lines.append(line)
    for quote, (index, number, first, last) in rules.items():
        lines[index] = (
            f'weekly rule: "{_line(quote)}" · {_count(number, "date")} that code wrote from the '
            f"rule, {_when(first, first)} to {_when(last, last)}"
        )
    return lines or ["not stated"]


def tell_me_more(db: sqlite3.Connection, registry: dict, ids: list[int]) -> dict:
    """The full card of each id, in the order of the ids: each fact with its quote."""
    cards = []
    for item_id in ids:
        row = db.execute(
            f"SELECT {_ITEM}, i.venue, i.last_seen_at, i.last_verified FROM item i "
            "WHERE i.id = ? AND i.status = 'live'",
            (item_id,),
        ).fetchone()
        if row is None:
            cards.append({"id": item_id, "found": False})
            continue
        occurrences = db.execute(
            f"SELECT {_OCCURRENCE} FROM occurrence o WHERE o.item_id = ? "
            "ORDER BY o.start_date, o.end_date, o.id",
            (item_id,),
        ).fetchall()
        evidence = db.execute(
            "SELECT e.field, e.quote, e.model, p.url FROM evidence e "
            "JOIN page p ON p.id = e.page_id WHERE e.item_id = ? ORDER BY e.id",
            (item_id,),
        ).fetchall()
        base = _card(row)
        cards.append(
            {
                "id": item_id,
                "found": True,
                "title": base["title"],
                "kind": base["kind"],
                "category": base["category"],
                "when": _full_when(occurrences),
                "town": base["town"],
                "venue": _line(row[_N] or "") or "not stated",
                "price": base["price"],
                "yearly": base["yearly"],
                "below_bar": base["below_bar"],
                "source": base["source"],
                "sources": base["sources"],
                "evidence": [
                    {"field": field, "quote": _line(quote), "model": model, "page": _line(url)}
                    for field, quote, model, url in evidence
                ],
                "last_seen_at": row[_N + 1][:10],
                "last_verified": row[_N + 2][:10],
                "changes": _changes(db, item_id),
            }
        )
    found = sum(card["found"] for card in cards)
    data = {
        "as_of": _as_of(db),
        "counts": {"ids": len(cards), "found": found},
        "cards": cards,
        "holes": _holes(registry, list(registry["places"])),
    }

    lines = [f"tell_me_more · {found} of {_count(len(cards), 'id')} found · as of {data['as_of']}"]
    for card in cards:
        if not card["found"]:
            lines += ["", f"id {_line(card['id'])}: not found"]
            continue
        rows = [("title", card["title"]), ("kind", card["kind"]), ("category", card["category"])]
        rows += [("when", when) for when in card["when"]]
        rows += [
            ("town", card["town"]),
            ("venue", card["venue"]),
            ("price", card["price"]),
            ("yearly", "yes" if card["yearly"] else "no"),
            ("bar", ("below" if card["below_bar"] else "not below") + " the traveller bar"),
            ("source", card["source"]),
            ("sources", _count(card["sources"], "source")),
        ]
        rows += [
            ("evidence", f'{e["field"]}: "{e["quote"]}" ({e["model"]}, {e["page"]})')
            for e in card["evidence"]
        ]
        seen = f"last_seen_at {card['last_seen_at']} · last_verified {card['last_verified']}"
        rows.append(("seen", seen))
        rows += [("changes", f"{_change_text(c)} ({c['actor']})") for c in card["changes"]] or [
            ("changes", "none")
        ]
        lines += ["", f"id {card['id']}"]
        lines += [f"  {label:<10}{text}" for label, text in rows]
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}


def what_changed(db: sqlite3.Connection, registry: dict, place: str, since: date) -> dict:
    """The items of the place that are new or changed on or after a date.

    The feed has no memory of an earlier look: the caller gives the date. An item that is new
    is not also in "changed".
    """
    day, as_of = since.isoformat(), _as_of(db)
    items = {}
    where = (
        "(substr(i.first_seen, 1, 10) >= ? OR EXISTS (SELECT 1 FROM change c "
        "WHERE c.item_id = i.id AND substr(c.found_at, 1, 10) >= ?))"
    )
    for row in _rows(db, place, where, (day, day)):
        items.setdefault(row[0], []).append(row)
    found = []  # (group, the date of the order, card)
    for rows in items.values():
        card = _finish(db, _card(rows[0]))
        # Each real date that is not past, or the last real date. A weekly rule is one part.
        shown = [row[_N:] for row in rows if row[_N + 1] >= as_of] or [rows[-1][_N:]]
        card["when"] = ", ".join(_full_when(shown))
        card["state"] = ""  # each part of `when` has its own state
        if card["first_seen"] >= day:
            found.append((0, card["first_seen"], card))
        else:
            card["changes"] = _changes(db, card["id"], day)
            found.append((1, card["changes"][0]["found_at"], card))
    found.sort(key=lambda entry: (*entry[:2], entry[2]["title"].casefold(), entry[2]["id"]))
    groups = [
        {"name": name, "cards": [card for group, _, card in found if group == index]}
        for index, name in enumerate(CHANGE_GROUPS)
    ]
    cards = [card for _, _, card in found]
    data = {
        "place": place,
        "since": day,
        "as_of": as_of,
        "counts": _counts(cards, {group["name"]: len(group["cards"]) for group in groups}),
        "groups": groups,
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    lines = [f"what_changed · {place_name} · since {_day(since, False)} · as of {as_of}", ""]
    lines += _counts_lines(data["counts"], "since the date")
    for group in groups:
        lines += ["", group["name"]]
        if not group["cards"]:
            lines.append("    none")
        for card in group["cards"]:
            lines += _card_lines(card, mark_below=True, changes=card.get("changes"))
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}
