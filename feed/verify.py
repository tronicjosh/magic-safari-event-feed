"""Verify: code checks on what the model extracted. Nothing passes on the model's word.

Check 1  the quote is on the page
Check 2  the value is in the quote (for a date: each part is in the date quotes)
Check 3  the value has the correct shape (a real date, a known weekday)
"""

import re
from datetime import date

LEVELS = ["exact", "whitespace", "punctuation"]

# The only tolerance after whitespace: typographic forms of quote marks, dashes and spaces.
_PUNCTUATION = str.maketrans(
    {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "‐": "-",
        "‑": "-",
        "−": "-",
        " ": " ",
    }
)

_EN = "january february march april may june july august september october november december"
_AF = "januarie februarie maart april mei junie julie augustus september oktober november desember"
_AF_SHORT = "jan feb mrt apr mei jun jul aug sep okt nov des"
MONTHS = {
    number: {en, en[:3], af, short} | ({"sept"} if number == 9 else set())
    for number, (en, af, short) in enumerate(
        zip(_EN.split(), _AF.split(), _AF_SHORT.split(), strict=True), start=1
    )
}

_DAYS_EN = "monday tuesday wednesday thursday friday saturday sunday"
_DAYS_AF = "maandag dinsdag woensdag donderdag vrydag saterdag sondag"
WEEKDAYS = {
    en: {en, en + "s", en[:3], af, af[:-2] + "ae"}
    for en, af in zip(_DAYS_EN.split(), _DAYS_AF.split(), strict=True)
}

# Short words that are also normal words ("whales may be seen", "we sat"). They count as a
# month or a weekday only with a capital letter.
_AMBIGUOUS = {"may", "sat", "sun"}

# A day number stands alone: "18", "18th", "5-10", "7 & 8", "(18)". It is not a part of a time
# (18:00, 18H00, 18.30, 8pm, 18 uur), a price (R18), a distance (18km), a phone number (+27),
# a date with slashes, or a page mark ([page 18]).
_DAY = re.compile(
    r"(?<![^\s\-–—&(,])(\d{1,2})(?:st|nd|rd|th|ste|de)?"
    r"(?=$|[\s\-–—&),;]|\.(?!\d))"
    r"(?!\s*:)(?!\s*(?:uur|am|pm|h|hrs|km)\b)",
    re.IGNORECASE,
)
_YEAR = re.compile(r"(?<![\w.,/+])(\d{4})(?!\w)")
_NUMERIC_DATE = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)")
_WORD = re.compile(r"[^\W\d_]+")
_CLOCK = re.compile(r"(?<![\d.,/:])\d{1,2}[:hH]\d{2}(?![\d.,/:])")
_NUMBER = re.compile(r"\d+(?:[ ,]\d{3})*(?:\.\d+)?")

# What a wrong type or a missing key raises. Such an entry fails; it does not stop the run.
_MALFORMED = (TypeError, KeyError, AttributeError, ValueError, OverflowError)


def _whitespace(text: str) -> str:
    return " ".join(text.split())


def _punctuation(text: str) -> str:
    return _whitespace(text.translate(_PUNCTUATION))


def _found(quote: str, page: str) -> bool:
    """The quote is in the page, and it does not start or end inside a word or a number."""
    before = r"(?<![^\W_])" if quote[0].isalnum() else ""
    after = r"(?![^\W_])" if quote[-1].isalnum() else ""
    return re.search(before + re.escape(quote) + after, page) is not None


def quote_on_page(quote: str, page: str) -> str | None:
    """Check 1. Returns how the quote matched, or None if it is not on the page."""
    if not quote.strip():
        return None
    if _found(quote.strip(), page):
        return "exact"
    if _found(_whitespace(quote), _whitespace(page)):
        return "whitespace"
    if _found(_punctuation(quote), _punctuation(page)):
        return "punctuation"
    return None


def value_in_quote(value: str, quote: str) -> bool:
    """Check 2 for a text value."""
    value = _punctuation(value).casefold()
    return bool(value) and value in _punctuation(quote).casefold()


def _numbers(text: str) -> set[str]:
    """The numbers of a text: "R1 500" and "R1,500" are 1500; "75.00" is 75; "75.50" is 75.5."""
    numbers = set()
    for number in _NUMBER.findall(text):
        number = re.sub(r"[ ,]", "", number)
        numbers.add(number.rstrip("0").rstrip(".") if "." in number else number)
    return numbers


def numbers_in_quote(value: str, quote: str) -> bool:
    """Check 2 for a price: each number of the value is a number of the quote."""
    wanted = _numbers(value)
    return bool(wanted) and wanted <= _numbers(quote)


def _words(text: str) -> set[str]:
    return {
        word.casefold()
        for word in _WORD.findall(text)
        if word.casefold() not in _AMBIGUOUS or word[0].isupper()
    }


def _real_date(part: dict) -> date | None:
    try:
        return date(part["year"], part["month"], part["day"])
    except (ValueError, TypeError, OverflowError):
        return None


def _shape(when: dict) -> str | None:
    kind, start, end = when["kind"], when["start"], when["end"]
    # A part that the kind does not use must be 0, because no check reads it.
    if kind == "weekly" and any(list(start.values()) + list(end.values())):
        return "shape: weekly must have no start and no end"
    if kind == "date" and any(end.values()):
        return "shape: date must have no end"
    if kind == "months" and (start["day"] or end["day"]):
        return "shape: months must have no days"

    if kind in ("date", "range"):
        sides = [("start", start)] + ([("end", end)] if kind == "range" else [])
        for _, part in sides:
            if not (part["day"] and part["month"] and part["year"]):
                return f"shape: {kind} needs day, month and year"
        for side, part in sides:
            if _real_date(part) is None:
                return f"shape: {side} is not a real date"
        if kind == "range" and _real_date(end) < _real_date(start):
            return "shape: end is before start"
    elif kind == "months":
        if not (1 <= start["month"] <= 12 and 1 <= end["month"] <= 12):
            return "shape: months needs a start month and an end month"
    elif kind == "weekly":
        if when["weekday"] not in WEEKDAYS:
            return "shape: weekday not known"
    else:
        return "shape: kind not known"
    return None


def check_when(when: dict) -> list[str]:
    """Checks 2 and 3 for one date entry. Returns the failures; an empty list is a pass."""
    shape = _shape(when)
    if shape:
        return [shape]

    text = "\n".join(when["quotes"])
    words = _words(text)
    if when["kind"] == "weekly":
        if not words & WEEKDAYS[when["weekday"]]:
            return [f"weekday {when['weekday']} not in quotes"]
        # A weekly rule becomes a date for each week, so the quote must hold no date. One rule,
        # not a list of date forms: no digit, except a clock time with minutes (09:00, 14h00).
        # The meaning of the words ("first", "closed") is the model's judgment, and the card
        # shows the quote.
        digit = any(char.isdigit() for char in _CLOCK.sub(" ", text))
        if digit or any(words & names for names in MONTHS.values()):
            return ["weekly quote holds a date or a number"]
        return []

    numeric = {tuple(int(n) for n in found) for found in _NUMERIC_DATE.findall(text)}
    days = {int(n) for n in _DAY.findall(text)}
    years = {int(n) for n in _YEAR.findall(text)}
    failures = []
    sides = [("start", when["start"])]
    if when["kind"] != "date":
        sides.append(("end", when["end"]))
    for side, part in sides:
        if (part["day"], part["month"], part["year"]) in numeric:
            continue
        if part["day"] and part["day"] not in days:
            failures.append(f"{side} day {part['day']} not in quotes")
        if part["month"] and not words & MONTHS[part["month"]]:
            failures.append(f"{side} month {part['month']} not in quotes")
        if part["year"] and part["year"] not in years:
            failures.append(f"{side} year {part['year']} not in quotes")
    return failures


def _result(field: str, ok: bool, reason: str = "", level: str | None = None) -> dict:
    return {"field": field, "ok": ok, "reason": reason, "level": level}


def _verify_field(field: str, entry: dict | None, page: str, towns=None) -> dict | None:
    if entry is None:
        entry = {"value": "", "quote": ""}
    if field == "town" and towns is not None:
        # The model chooses the town. Code checks the list, and that the quote is page text.
        # Only the exact empty value means "the page states no town".
        if entry["value"] == "":
            return None
        if entry["value"] not in towns:
            return _result(field, False, "town not in the list")
        level = quote_on_page(entry["quote"], page)
        if level is None:
            return _result(field, False, "quote not on page")
        return _result(field, True, level=level)
    if not entry["value"].strip():
        return _result("title", False, "no title") if field == "title" else None
    level = quote_on_page(entry["quote"], page)
    check = numbers_in_quote if field == "price" else value_in_quote
    if level is None:
        return _result(field, False, "quote not on page")
    if not check(entry["value"], entry["quote"]):
        return _result(field, False, "value not in quote", level)
    return _result(field, True, level=level)


def _verify_when(field: str, when: dict, page: str) -> dict:
    levels = [quote_on_page(quote, page) for quote in when["quotes"]]
    if not levels or None in levels:
        return _result(field, False, "quote not on page")
    failures = check_when(when)
    return _result(field, not failures, "; ".join(failures), max(levels, key=LEVELS.index))


def verify_item(item: dict, page: str, towns=None) -> list[dict]:
    """All checks for one extracted item. One result for each field that has a value.

    towns: the closed list of town values. With it, the town is a choice of the model from the
    list, and the value is not searched in the quote. Without it, the town is a quoted value.
    """
    results = []
    for field in ("title", "town", "venue", "price"):
        try:
            result = _verify_field(field, item.get(field), page, towns)
        except _MALFORMED:
            result = _result(field, False, "malformed entry")
        if result:
            results.append(result)

    whens = item.get("when")
    if not whens:
        results.append(_result("when", False, "no date or availability extracted"))
    elif not isinstance(whens, list):
        results.append(_result("when", False, "malformed entry"))
    else:
        for index, when in enumerate(whens):
            try:
                results.append(_verify_when(f"when[{index}]", when, page))
            except _MALFORMED:
                results.append(_result(f"when[{index}]", False, "malformed entry"))
    return results
