"""Read and card: read-only operations. The text comes from one fixed template.

A query never starts a fetch, never writes, and gives each item that matches. A date that no
page states is never shown: an item that is held each year and has no new dates is shown as
"not confirmed", with its last real dates.
"""

import re
import sqlite3
from datetime import date
from urllib.parse import urlsplit

CHANGE_GROUPS = ("new", "changed")
GROUPS = ("dated", "seasons and experiences", "not confirmed", "below the traveller bar")
PLAN_GROUPS = ("seasons and experiences", "yearly with a date", "not confirmed", "each week")
FIND_GROUPS = ("coming or current", "past")
_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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
    "i.repeats_yearly, i.first_seen, i.venue, "
    "(SELECT count(DISTINCT p.source_id) FROM evidence e JOIN page p ON p.id = e.page_id "
    " WHERE e.item_id = i.id)"
)
_N = 12  # the number of item columns
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
    # The last ingest: a new page, or an unchanged page that still lists its items.
    newest = db.execute(
        "SELECT max(at) FROM (SELECT max(fetched_at) AS at FROM page "
        "UNION ALL SELECT max(last_seen_at) FROM item)"
    ).fetchone()[0]
    return (newest or "")[:10]


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
    item_id, kind, category, title, town, price, link, below, yearly, seen, venue = row[: _N - 1]
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
        "all_year": False,  # January to December: a rule of the page, not a season
        "dateless": False,  # a rule after the last date that code wrote: no date is shown
        "below_bar": bool(below),
        "yearly": bool(yearly),
        "town": _line(town),
        "venue": _venue(venue),  # empty: no page states it
        "price": _line(price or "") or "not stated",
        "sources": row[_N - 1],
        "source": _line(link),
        "first_seen": seen[:10],
        "changed": None,  # the latest change row, if there is one
        "match": None,  # find: the quote that holds the text, if no other field holds it
    }


def _add(card: dict, occurrence) -> None:
    """Add one real occurrence row to a card."""
    first, last, precision, rule, time_text = occurrence
    if precision == "month":
        text = _months(first, last, year=rule is None)
        if rule is not None:
            card["season"], card["season_quote"] = True, _line(time_text)
            card["all_year"] = text == "All year"
        else:  # a month that a page states with its year: the days in it are not stated
            card["range"] = True
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
        state = f'weekly rule: "{card["rule"]}"'
    elif card["season"] and card.get("all_year"):
        state = f'a rule of the page: "{card["season_quote"]}"'
    elif card["season"]:
        state = f'season, no year stated: "{card["season_quote"]}"'
    else:
        state = "confirmed"
    if card["range"]:  # the page gives a first and a last day, not each day
        state += "; a range, each day is not stated"
    return state


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


def _collected(db: sqlite3.Connection, place: str) -> dict:
    """The sources of the place that the feed holds a page of, and the day of the last
    collection. A page that did not change has no new row: its items were seen on that day."""
    pages = db.execute(
        "SELECT p.source_id, p.url, p.fetched_at FROM page p JOIN source s ON s.id = p.source_id "
        "WHERE s.place = ?",
        (place,),
    ).fetchall()
    seen = db.execute(
        "SELECT max(i.last_seen_at) FROM item i JOIN evidence e ON e.item_id = i.id "
        "JOIN page p ON p.id = e.page_id JOIN source s ON s.id = p.source_id WHERE s.place = ?",
        (place,),
    ).fetchone()[0]
    hosts = {_line(urlsplit(url).hostname or url).removeprefix("www.") for _, url, _ in pages}
    return {
        "sources": len({source for source, _, _ in pages}),
        "last": max([at for _, _, at in pages] + [seen or ""], default="")[:10],
        "hosts": sorted(hosts),
    }


def _counts_lines(counts: dict, scope: str, collected: dict) -> list[str]:
    by_group = " · ".join(f"{number} {name}" for name, number in counts["groups"].items())
    by_category = " · ".join(f"{name} {number}" for name, number in counts["categories"].items())
    sources = "none collected"
    if collected["sources"]:
        sources = f"{collected['sources']}, last collected on {collected['last']}: "
        sources += ", ".join(collected["hosts"])
    return [
        "counts",
        f"  {scope:<16}{_count(counts['items'], 'item')}: {by_group}",
        f"  by category     {by_category or 'none'}",
        f"  sources         {sources}",
    ]


def _venue(text: str | None) -> str:
    """A venue for the short card. It is third-party text: the mark that divides the fields of
    a card is taken out of it, and it has a limit."""
    venue = "".join(c for c in _line(text or "").replace("·", ",") if c.isprintable())
    return venue if len(venue) <= 80 else venue[:79].rstrip() + "…"


def _same(a: str, b: str) -> bool:
    """Two venues that differ only in case, spaces and punctuation are one venue."""
    return [c for c in a.casefold() if c.isalnum()] == [c for c in b.casefold() if c.isalnum()]


def _card_lines(card: dict, mark_below: bool = False, changes: list | None = None) -> list[str]:
    """The short card. `changes` replaces the line of the latest change."""
    when = f"{card['when']} ({card['state']})" if card["state"] else card["when"]
    if not card["confirmed"]:  # the last real dates; no date is given for this period
        when = f"not confirmed ({card['when']})"
    venue = f" · venue: {card['venue']}" if card["venue"] else ""  # no words when there is none
    below = " · below the traveller bar" if mark_below and card["below_bar"] else ""
    if changes is None:
        changes = [card["changed"]] if card["changed"] else []
    return [
        (
            f"[{card['kind']} · {card['category']}] {card['title']} · {when} · {card['town']}"
            f"{venue}{below}"
        ),
        (
            f"    price: {card['price']} · {_count(card['sources'], 'source')} · "
            f"first seen {card['first_seen']} · id {card['id']}{_also(card)}"
        ),
        *(f"    changed {_change_text(change)}" for change in changes),
        *([f'    match in a quote of the page: "{card["match"]}"'] if card["match"] else []),
        f"    source: {card['source']}",
    ]


def _also(card: dict) -> str:
    """The other ids of a card that is one item from two or more sources."""
    others = [str(item_id) for item_id in card.get("ids", [])[1:]]
    return f" (also id {', '.join(others)})" if others else ""


def _merge(cards: list[dict]) -> list[dict]:
    """One card for the same item from two sources: equal title, town, time and kind.

    The order of the first card is kept. The sources are added, and the card keeps each id.
    """
    merged, seen = [], {}
    for card in cards:
        key = (card["title"].casefold(), card["town"], card["when"], card["kind"])
        key += (card["below_bar"], card["confirmed"])
        if key in seen:
            first = seen[key]
            first["sources"] += card["sources"]
            first["ids"].append(card["id"])
            # A venue of the second source is not lost. Two different venues are both shown.
            known = first["venue"].split(" / ") if first["venue"] else []
            if card["venue"] and not any(_same(card["venue"], venue) for venue in known):
                first["venue"] = " / ".join([*known, card["venue"]])
        else:
            card["ids"] = [card["id"]]
            seen[key] = card
            merged.append(card)
    return merged


def _weekly_rules(db: sqlite3.Connection, place: str) -> dict[int, tuple[dict, str]]:
    """Each item with a weekly rule: a card with the rule and no date, and the last date
    that code wrote from the rule."""
    found = {}
    for row in _rows(db, place, "o.rule = 'weekly'"):
        card, days, _ = found.get(row[0]) or (_card(row), [], "")
        weekday = date.fromisoformat(row[_N]).weekday()
        if weekday not in days:
            days.append(weekday)
        card["rule"] = _line(row[_N + 4])
        found[row[0]] = (card, days, row[_N])  # the rows are in the order of the dates
    for card, days, _ in found.values():
        card["when"] = ["Each " + " and ".join(_WEEKDAYS[day] for day in sorted(days))]
        card["dateless"] = True
    return {item_id: (card, last) for item_id, (card, _, last) in found.items()}


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
    # Only a date that a page states can be "last held": never a row that code wrote.
    yearly = _rows(db, place, "i.repeats_yearly = 1 AND o.rule IS NULL")
    latest = {row[0]: row for row in yearly}
    for item_id, row in latest.items():
        moved = None if item_id in cards else _moved_into(row[_N], row[_N + 1], start, end)
        if moved is not None:
            cards[item_id] = _card(row)
            _last_held(cards[item_id], row[_N:], _as_of(db))
            first_day[item_id] = moved.isoformat()

    # The horizon. Code writes the dates of a rule only some time ahead. For a window after
    # the last such date, the item is not lost: it is listed with its rule and no date.
    # For a window that only crosses that date, the item has its dates up to it, and a note.
    horizon, crossed = "", ""
    for item_id, (card, last) in _weekly_rules(db, place).items():
        if item_id not in cards and last < start.isoformat():
            cards[item_id], first_day[item_id] = card, start.isoformat()
            horizon = max(horizon, last)
        elif item_id in cards and last < end.isoformat():
            crossed = max(crossed, last)
    last_season = {row[0]: row for row in _rows(db, place, "o.rule = 'season'")}
    window_months = _months_of(start.isoformat(), end.isoformat())
    for item_id, row in last_season.items():
        after = row[_N + 1] < start.isoformat()
        if item_id not in cards and after and _months_of(row[_N], row[_N + 1]) & window_months:
            cards[item_id] = _card(row)
            _add(cards[item_id], row[_N:])
            first_day[item_id] = start.isoformat()
            horizon = max(horizon, row[_N + 1])

    # Neutral order: the first day in the window, then the title, then the id.
    ordered = sorted(
        (_finish(db, card) for card in cards.values()),
        key=lambda card: (first_day[card["id"]], card["title"].casefold(), card["id"]),
    )
    ordered = _merge(ordered)
    groups = [{"name": name, "cards": []} for name in GROUPS]
    for card in ordered:
        if card["below_bar"]:
            group = 3
        elif not card["confirmed"]:
            group = 2
        else:
            group = 1 if card["kind"] != "event" or card["dateless"] else 0
        groups[group]["cards"].append(card)
    notes = []
    if horizon:
        notes.append(
            f"The feed writes dates from rules until {horizon}. This window is after that "
            "date: an item from a rule is listed with its rule and no date."
        )
    if crossed:
        notes.append(
            f"The feed writes dates from rules until {crossed}. This window goes past that "
            "date: an item from a rule has no written date after it."
        )
    if not ordered:
        notes.append("The feed has no item for these dates.")
    data = {
        "place": place,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "as_of": _as_of(db),
        "counts": _counts(ordered, {group["name"]: len(group["cards"]) for group in groups}),
        "notes": notes,
        "groups": groups,
        "collected": _collected(db, place),
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    window = f"{_day(start, False)} - {_day(end, False)}"
    lines = [f"what_is_on · {place_name} · {window} · as of {data['as_of']}", ""]
    lines += _counts_lines(data["counts"], "in the window", data["collected"])
    lines += [f"  note            {note}" for note in notes]
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
            real = [row for row in rows if row[_N + 3] is None]  # dates that a page states
            if not real:
                continue
            group, shown = 2, real[-1:]
            _last_held(card, real[-1][_N:], as_of)
        covers = set().union(*(_months_of(row[_N], row[_N + 1]) for row in shown))
        if covers & set(numbers):
            listed.append((group, _finish(db, card), covers))
    listed.sort(key=lambda entry: (entry[0], entry[1]["title"].casefold(), entry[1]["id"]))
    kept = {id(card) for card in _merge([card for _, card, _ in listed])}
    listed = [entry for entry in listed if id(entry[1]) in kept]
    # A weekly item is on in each month: it is listed one time, as its rule, with no date.
    weekly = [_finish(db, card) for card, _ in _weekly_rules(db, place).values()]
    weekly = _merge(sorted(weekly, key=lambda card: (card["title"].casefold(), card["id"])))

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
        for index, name in enumerate(PLAN_GROUPS[:3])
    }
    groups[PLAN_GROUPS[3]] = len(weekly)
    note = "This answer has seasons, weekly items and yearly events only. For the dated events "
    notes = [note + "of a period, call what_is_on with dates, or find."]
    data = {
        "place": place,
        "from_month": first,
        "to_month": last,
        "as_of": as_of,
        "counts": _counts([card for _, card, _ in listed] + weekly, groups),
        "notes": notes,
        "each_week": weekly,
        "months": months,
        "collected": _collected(db, place),
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    span = _MONTHS[first - 1] if first == last else f"{_MONTHS[first - 1]} - {_MONTHS[last - 1]}"
    lines = [f"when_to_go · {place_name} · {span} · as of {as_of}", ""]
    lines += _counts_lines(data["counts"], "in the months", data["collected"])
    lines += [f"  note            {note}" for note in notes]
    lines += ["", "each week, in each month"]
    if not weekly:
        lines.append("    none")
    for card in weekly:
        lines += _card_lines(card, mark_below=True)
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
        card["season_quote"], card["all_year"] = None, False
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
            f"SELECT {_ITEM}, i.last_seen_at, i.last_verified FROM item i "
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
                "venue": base["venue"] or "not stated",
                "price": base["price"],
                "yearly": base["yearly"],
                "below_bar": base["below_bar"],
                "source": base["source"],
                "sources": base["sources"],
                "evidence": [
                    {"field": field, "quote": _line(quote), "model": model, "page": _line(url)}
                    for field, quote, model, url in evidence
                ],
                "last_seen_at": row[_N][:10],
                "last_verified": row[_N + 1][:10],
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
    is not also in "changed". The feed cannot know what changed before its first collection
    of the place: an item of that first collection is not "new", it is only counted.
    """
    day, as_of = since.isoformat(), _as_of(db)
    first = db.execute(
        "SELECT min(substr(p.fetched_at, 1, 10)) FROM page p JOIN source s ON s.id = p.source_id "
        "WHERE s.place = ?",
        (place,),
    ).fetchone()[0]
    # The earlier look was before the feed's first collection ended: on that day or before.
    before_first = bool(first) and day <= first
    at_first = 0
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
        changes = _changes(db, card["id"], day)
        if before_first and card["first_seen"] == first and not changes:
            at_first += 1  # in the feed from its first collection: not known to be new
        elif card["first_seen"] >= day and not (before_first and card["first_seen"] == first):
            found.append((0, card["first_seen"], card))
        else:
            card["changes"] = changes
            found.append((1, changes[0]["found_at"], card))
    found.sort(key=lambda entry: (*entry[:2], entry[2]["title"].casefold(), entry[2]["id"]))
    groups = [
        {"name": name, "cards": [card for group, _, card in found if group == index]}
        for index, name in enumerate(CHANGE_GROUPS)
    ]
    groups[0]["cards"] = _merge(groups[0]["cards"])
    cards = [card for group in groups for card in group["cards"]]
    notes = []
    if before_first:
        note = f"The feed first collected this place on {first}. It cannot say what changed "
        note += f"before or on that day. {_count(at_first, 'item')} of that first collection: "
        notes = [note + "not listed as new."]
    data = {
        "place": place,
        "since": day,
        "notes": notes,
        "as_of": as_of,
        "first_collected": first,
        "at_first_collection": at_first,
        "counts": _counts(cards, {group["name"]: len(group["cards"]) for group in groups}),
        "groups": groups,
        "collected": _collected(db, place),
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    lines = [f"what_changed · {place_name} · since {_day(since, False)} · as of {as_of}", ""]
    lines += _counts_lines(data["counts"], "since the date", data["collected"])
    if before_first:
        lines += [
            f"  first look      The feed first collected {place_name} on {first}.",
            f"                  It cannot say what changed before or on {first}.",
            f"                  {_count(at_first, 'item')} of that first collection: not listed as new.",
        ]
    for group in groups:
        lines += ["", group["name"]]
        if not group["cards"]:
            lines.append("    none")
        for card in group["cards"]:
            lines += _card_lines(card, mark_below=True, changes=card.get("changes"))
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}


def _holds(hay: str, word: str) -> bool:
    """A word of the search is in the text if the text holds it ("art" finds "FynArts"). A
    long word can also be two words of the text with no space ("artwalk" finds "art walk").
    A short word cannot: "spa" is not in "bus park"."""
    return word in hay or (len(word) >= 6 and word in hay.replace(" ", ""))


def _in_quote(quote: str, words: list[str]) -> str | None:
    """The quote for the short card, if it holds each word of the search as a whole word
    ("free" is not in "carefree"). A long quote is cut to the part that holds the first word."""
    text = "".join(c for c in _line(quote) if c.isprintable())
    found = [re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text.casefold()) for word in words]
    if not all(found):
        return None
    if len(text) <= 160:
        return text
    first = max(0, min(found[0].start() - 60, len(text) - 160))
    part = text[first : first + 160].strip()
    return ("…" if first else "") + part + ("…" if first + 160 < len(text) else "")


def find(db: sqlite3.Connection, registry: dict, place: str, text: str) -> dict:
    """Each live item of the place whose title, category, venue or town holds the text, or
    that has a stored quote of a page with each word of the text as a whole word.

    For a named item or a subject ("wine") when the trip has no dates. Each
    word of the text must be in the item. The order is neutral: by date, then by title.
    There is no score. A card that matched only in a quote shows the quote.
    """
    words = _line(text).casefold().split()
    if not words:
        raise ValueError("give a name or a word to find")
    as_of = _as_of(db)
    wanted = []
    for item_id, title, category, venue, town in db.execute(
        "SELECT i.id, i.title, i.category, coalesce(i.venue, ''), i.town FROM item i "
        "WHERE i.status = 'live' ORDER BY i.id"
    ):
        hay = f"{title} {category} {venue} {town}".casefold()
        if all(_holds(hay, word) for word in words):
            wanted.append(item_id)
    quotes = {}  # an item that matched in no field: its first quote that holds the text
    for item_id, quote in db.execute(
        "SELECT e.item_id, e.quote FROM evidence e JOIN item i ON i.id = e.item_id "
        "WHERE i.status = 'live' ORDER BY e.id"
    ):
        if item_id not in wanted and item_id not in quotes:
            match = _in_quote(quote, words)
            if match:
                quotes[item_id] = match
    wanted += quotes
    items = {}
    if wanted:
        marks = ", ".join("?" * len(wanted))
        for row in _rows(db, place, f"i.id IN ({marks})", tuple(wanted)):
            items.setdefault(row[0], []).append(row)

    found = []  # (group, the date of the order, card)
    for rows in items.values():
        card = _finish(db, _card(rows[0]))
        card["match"] = quotes.get(card["id"])
        coming = [row for row in rows if row[_N + 1] >= as_of]
        real = [row for row in rows if row[_N + 3] is None]
        if coming:
            card["when"] = ", ".join(_full_when([row[_N:] for row in coming]))
            card["state"] = ""  # each part of `when` has its own state
            found.append((0, coming[0][_N], card))
        elif real:
            if card["yearly"]:
                _last_held(card, real[-1][_N:], as_of)
                card["when"], card["state"] = card["when"][0], "not confirmed"
            else:
                card["when"] = ", ".join(_full_when([real[-1][_N:]]))
                card["state"] = ""
            found.append((1, real[-1][_N], card))
    found.sort(key=lambda entry: (*entry[:2], entry[2]["title"].casefold(), entry[2]["id"]))
    groups = [
        {"name": name, "cards": _merge([card for group, _, card in found if group == index])}
        for index, name in enumerate(FIND_GROUPS)
    ]
    cards = [card for group in groups for card in group["cards"]]
    notes = [] if cards else ["The feed has no item that holds this text."]
    data = {
        "place": place,
        "text": " ".join(words),
        "as_of": as_of,
        "counts": _counts(cards, {group["name"]: len(group["cards"]) for group in groups}),
        "notes": notes,
        "groups": groups,
        "collected": _collected(db, place),
        "holes": _holes(registry, [place]),
    }

    place_name = _line(registry["places"][place]["name"])
    lines = [f'find · {place_name} · "{data["text"]}" · as of {as_of}', ""]
    lines += _counts_lines(data["counts"], "with the text", data["collected"])
    lines += [f"  note            {note}" for note in notes]
    for group in groups:
        lines += ["", group["name"]]
        if not group["cards"]:
            lines.append("    none")
        for card in group["cards"]:
            lines += _card_lines(card, mark_below=True)
    lines += _holes_lines(registry, data["holes"])
    return {"data": data, "text": "\n".join(lines) + "\n"}
