"""Slice 0b.2: seasons, months with a year, "held each year", and the second run of an item.

Hand cases 7, 8 and 16 of docs/design.md are here at the level of the database. The last
tests use real saved pages and the saved model answers of T11 and T13. No model call.
"""

import json
from pathlib import Path

import pytest

import feed.update
from feed.store import open_db
from feed.update import ingest_answer

CASES = Path("evals/cases")
PAGES = Path("evals/pages")
FIRST = "2026-11-23T12:00:00+00:00"
SECOND = "2026-11-30T12:00:00+00:00"
EMPTY = {"value": "", "quote": ""}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def hand():
    registry = _load(CASES / "registry.json")
    registry["sources"].append(dict(registry["sources"][0], id="second"))
    return open_db(":memory:", registry), registry


def _when(kind: str, start=(0, 0, 0), end=(0, 0, 0), quotes=(), **more) -> dict:
    part = ("day", "month", "year")
    return {
        "kind": kind,
        "start": dict(zip(part, start, strict=True)),
        "end": dict(zip(part, end, strict=True)),
        "weekday": "",
        "ongoing": False,
        "quotes": list(quotes),
    } | more


def _months(start: tuple, end: tuple, quote: str) -> dict:
    return _when("months", (0, *start), (0, *end), [quote])


def _item(title: str, *whens: dict, **fields) -> dict:
    item = {"title": {"value": title, "quote": title}, "town": EMPTY, "venue": EMPTY}
    return item | {"price": EMPTY, "when": list(whens)} | fields


def _ingest(hand, text: str, *items, at: str = FIRST, source: str = "hand") -> dict:
    db, registry = hand
    page = {"url": "https://example.org/page", "text": text, "fetched_at": at, "status": 200}
    return ingest_answer(db, registry, source, page, {"model": "hand", "items": list(items)})


def _rows(hand, title: str) -> list[tuple]:
    return (
        hand[0]
        .execute(
            "SELECT o.start_date, o.end_date, o.precision, o.rule FROM occurrence o "
            "JOIN item i ON i.id = o.item_id WHERE i.title = ? ORDER BY o.start_date",
            (title,),
        )
        .fetchall()
    )


def _one(hand, sql: str, *values):
    return hand[0].execute(sql, values).fetchone()


def _counts(hand) -> tuple:
    return tuple(
        _one(hand, f"SELECT count(*) FROM {table}")[0]
        for table in ("item", "occurrence", "evidence", "change")
    )


# Kind "months".

WHALES = (
    "Whale season\nThe whales are in the bay from June to November.\n"
    "The whales come back every year.\n"
)
YEARLY = {"value": "yes", "quote": "come back every year"}
NO_PROOF = "when: months with no year, and no proof on the page that it is held each year"
WHALE_QUOTE = "from June to November"


def test_a_season_with_no_year_is_one_row_for_this_year_and_the_next_two(hand):
    season = _months((6, 0), (11, 0), WHALE_QUOTE)
    report = _ingest(hand, WHALES, _item("Whale season", season, yearly=YEARLY))
    assert report == {"stored": 1, "updated": 0, "set_aside": []}
    assert _rows(hand, "Whale season") == [
        ("2026-06-01", "2026-11-30", "month", "season"),
        ("2027-06-01", "2027-11-30", "month", "season"),
        ("2028-06-01", "2028-11-30", "month", "season"),
    ]
    item = _one(hand, "SELECT kind, time_shape, repeats_yearly FROM item")
    assert item == ("season", "season", 1)
    quote = _one(hand, "SELECT quote FROM evidence WHERE field = 'when'")[0]
    assert quote == WHALE_QUOTE
    assert _one(hand, "SELECT DISTINCT time_text FROM occurrence")[0] == WHALE_QUOTE


def test_a_season_over_the_year_end_goes_into_the_next_year(hand):
    text = "Summer season\nDecember to February\nIt is held every year.\n"
    season = _months((12, 0), (2, 0), "December to February")
    yearly = {"value": "yes", "quote": "held every year"}
    assert _ingest(hand, text, _item("Summer season", season, yearly=yearly))["stored"] == 1
    assert _rows(hand, "Summer season") == [
        ("2026-12-01", "2027-02-28", "month", "season"),
        ("2027-12-01", "2028-02-29", "month", "season"),  # 2028 is a leap year
        ("2028-12-01", "2029-02-28", "month", "season"),
    ]


def test_months_with_a_year_is_one_row_with_no_rule(hand):
    text = "Arts festival\nJune 2027\n"
    when = _months((6, 2027), (6, 2027), "June 2027")
    assert _ingest(hand, text, _item("Arts festival", when))["stored"] == 1
    assert _rows(hand, "Arts festival") == [("2027-06-01", "2027-06-30", "month", None)]
    assert _one(hand, "SELECT kind, time_shape FROM item") == ("event", "run")


def test_months_with_a_year_and_an_end_month_before_the_start_goes_into_the_next_year(hand):
    text = "Winter show\nNovember 2026 to April\n"
    when = _months((11, 2026), (4, 0), "November 2026 to April")
    assert _ingest(hand, text, _item("Winter show", when))["stored"] == 1
    assert _rows(hand, "Winter show") == [("2026-11-01", "2027-04-30", "month", None)]


def test_months_with_a_stated_end_year_uses_it(hand):
    text = "Long show\nNovember 2026 to April 2028\n"
    when = _months((11, 2026), (4, 2028), "November 2026 to April 2028")
    assert _ingest(hand, text, _item("Long show", when))["stored"] == 1
    assert _rows(hand, "Long show") == [("2026-11-01", "2028-04-30", "month", None)]


@pytest.mark.parametrize(
    ("start", "end", "reason"),
    [
        ((6, 2027), (4, 2027), "when[0]: months: end is before start"),
        ((6, 0), (8, 2027), NO_PROOF),
    ],
)
def test_months_with_years_that_do_not_fit_are_not_stored(hand, start, end, reason):
    text = "Odd show\nApril to June to August 2027\n"
    item = _item("Odd show", _months(start, end, "April to June to August 2027"))
    assert _ingest(hand, text, item) == {
        "stored": 0,
        "updated": 0,
        "set_aside": [("Odd show", reason)],
    }
    assert _counts(hand) == (0, 0, 0, 0)


def test_a_season_and_a_dated_entry_in_one_item_is_an_event(hand):
    text = WHALES + "Opening day 5 June 2027\n"
    day = _when("date", (5, 6, 2027), quotes=["Opening day 5 June 2027"])
    item = _item("Whale season", _months((6, 0), (11, 0), WHALE_QUOTE), day, yearly=YEARLY)
    assert _ingest(hand, text, item)["stored"] == 1
    assert _one(hand, "SELECT kind, time_shape FROM item") == ("event", "repeating dates")
    assert ("2027-06-05", "2027-06-05", "day", None) in _rows(hand, "Whale season")
    assert len(_rows(hand, "Whale season")) == 4


def test_a_months_entry_with_a_month_that_the_quote_does_not_hold_is_not_stored(hand):
    item = _item("Whale season", _months((5, 0), (11, 0), WHALE_QUOTE))
    report = _ingest(hand, WHALES, item)
    assert report["set_aside"] == [("Whale season", "when[0]: start month 5 not in quotes")]
    assert _counts(hand) == (0, 0, 0, 0)


# Held each year.

SEASON = _months((6, 0), (11, 0), WHALE_QUOTE)
YEARLY_TEXT = WHALES + "Opening day 5 June 2027\n"
OPENING = _when("date", (5, 6, 2027), quotes=["Opening day 5 June 2027"])


def test_yearly_with_a_quote_on_the_page_is_stored_with_evidence(hand):
    assert _ingest(hand, YEARLY_TEXT, _item("Whale season", SEASON, yearly=YEARLY))["stored"] == 1
    assert _one(hand, "SELECT repeats_yearly FROM item")[0] == 1
    row = _one(hand, "SELECT value, quote, model FROM evidence WHERE field = 'yearly'")
    assert row == ("yes", "come back every year", "hand")


@pytest.mark.parametrize(
    "yearly",
    [
        {"value": "yes", "quote": "held annually"},  # the quote is not on the page
        {"value": "yes", "quote": ""},
        {"value": "", "quote": ""},
        {"value": "no", "quote": "come back every year"},
        {"value": "yes"},
        {"value": "yes", "quote": 5},
        "yes",
        None,
    ],
)
def test_yearly_without_a_quote_on_the_page_is_not_stored_and_the_item_is(hand, yearly):
    report = _ingest(hand, YEARLY_TEXT, _item("Whale season", OPENING, yearly=yearly))
    assert report == {"stored": 1, "updated": 0, "set_aside": []}
    assert _one(hand, "SELECT repeats_yearly FROM item")[0] == 0
    assert _one(hand, "SELECT count(*) FROM evidence WHERE field = 'yearly'")[0] == 0


@pytest.mark.parametrize("yearly", [None, {"value": "yes", "quote": "held annually"}])
def test_months_with_no_year_and_no_proof_of_each_year_is_not_stored(hand, yearly):
    """ "October" in a calendar of one year must not become October of three years."""
    report = _ingest(hand, YEARLY_TEXT, _item("Whale season", SEASON, yearly=yearly))
    assert report == {"stored": 0, "updated": 0, "set_aside": [("Whale season", NO_PROOF)]}
    assert _counts(hand) == (0, 0, 0, 0)


def test_the_category_is_a_choice_from_the_list_of_the_registry(hand):
    text = "Arts festival\nJune 2027\nWine fair\nJuly 2027\n"
    festival = _item(
        "Arts festival", _months((6, 2027), (6, 2027), "June 2027"), category="festival"
    )
    fair = _item("Wine fair", _months((7, 2027), (7, 2027), "July 2027"), category="the best")
    assert _ingest(hand, text, festival, fair)["stored"] == 2
    rows = hand[0].execute("SELECT title, category FROM item ORDER BY title").fetchall()
    assert rows == [("Arts festival", "festival"), ("Wine fair", "other")]


@pytest.mark.parametrize("category", [None, 5, ["festival"], {"value": "festival"}])
def test_a_category_of_a_wrong_type_is_stored_as_other(hand, category):
    text = "Arts festival\nJune 2027\n"
    item = _item("Arts festival", _months((6, 2027), (6, 2027), "June 2027"), category=category)
    assert _ingest(hand, text, item)["stored"] == 1
    assert _one(hand, "SELECT category FROM item")[0] == "other"


def test_a_season_that_is_running_at_the_ingest_has_a_row(hand):
    """November to April, ingested in January: the season of this winter is on now."""
    text = "Shark season\nNovember to April\nThe sharks come back every year.\n"
    season = _months((11, 0), (4, 0), "November to April")
    item = _item("Shark season", season, yearly=YEARLY)
    assert _ingest(hand, text, item, at="2027-01-05T08:00:00+00:00")["stored"] == 1
    assert [row[:2] for row in _rows(hand, "Shark season")] == [
        ("2026-11-01", "2027-04-30"),  # the running season
        ("2027-11-01", "2028-04-30"),
        ("2028-11-01", "2029-04-30"),
        ("2029-11-01", "2030-04-30"),
    ]


def test_a_season_that_is_over_at_the_ingest_has_no_row(hand):
    item = _item("Whale season", SEASON, yearly=YEARLY)
    assert _ingest(hand, WHALES, item, at="2026-12-05T08:00:00+00:00")["stored"] == 1
    assert [row[0] for row in _rows(hand, "Whale season")] == ["2027-06-01", "2028-06-01"]


def test_all_year_needs_no_second_proof_and_keeps_its_quote(hand):
    text = "Country Market\nopen throughout the year\n"
    item = _item("Country Market", _months((1, 0), (12, 0), "open throughout the year"))
    assert _ingest(hand, text, item) == {"stored": 1, "updated": 0, "set_aside": []}
    rows = _rows(hand, "Country Market")
    assert rows[0] == ("2026-01-01", "2026-12-31", "month", "season") and len(rows) == 3
    assert _one(hand, "SELECT DISTINCT time_text FROM occurrence")[0] == "open throughout the year"


def test_all_year_with_a_quote_that_is_not_on_the_page_is_not_stored(hand):
    text = "Country Market\nopen on Saturdays\n"
    item = _item("Country Market", _months((1, 0), (12, 0), "open throughout the year"))
    assert _ingest(hand, text, item)["set_aside"] == [
        ("Country Market", "when[0]: quote not on page")
    ]


# The second run.

SHOW = "Harbour Concert\nTown Hall\nTickets R200\n12 December 2026\n"
SHOW_2 = "HARBOUR  CONCERT\nTown Hall\nTickets R250\n12 December 2026\n19 December 2026\n"


def _show(title: str, cost: str, *days: int, **fields) -> dict:
    whens = [_when("date", (day, 12, 2026), quotes=[f"{day} December 2026"]) for day in days]
    stated = {
        "venue": {"value": "Town Hall", "quote": "Town Hall"},
        "price": {"value": cost, "quote": f"Tickets {cost}"},
    }
    return _item(title, *whens, **(stated | fields))


def test_the_same_item_on_a_second_run_is_updated_and_not_added(hand):
    assert _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))["stored"] == 1
    report = _ingest(hand, SHOW_2, _show("HARBOUR  CONCERT", "R250", 12, 19), at=SECOND)
    assert report == {"stored": 0, "updated": 1, "set_aside": []}

    item = _one(
        hand,
        "SELECT title, first_seen, last_seen_at, last_verified, price_text, venue FROM item",
    )
    assert item == ("Harbour Concert", FIRST, SECOND, SECOND, "Tickets R250", "Town Hall")
    assert _one(hand, "SELECT count(*) FROM item")[0] == 1
    assert _rows(hand, "Harbour Concert") == [
        ("2026-12-12", "2026-12-12", "day", None),
        ("2026-12-19", "2026-12-19", "day", None),
    ]
    changes = (
        hand[0]
        .execute("SELECT item_id, field, old_value, new_value, found_at, actor FROM change")
        .fetchall()
    )
    assert changes == [
        (1, "price_text", "Tickets R200", "Tickets R250", SECOND, "ingest"),
        (1, "when", None, "2026-12-19", SECOND, "ingest"),  # the new date; 12 December is not
    ]
    value = _one(hand, "SELECT value FROM evidence WHERE field = 'when' ORDER BY id DESC")[0]
    assert value == changes[1][3]
    # the evidence of the new page is added: title, town (default), venue, price, two dates
    pages = (
        hand[0]
        .execute(
            "SELECT p.fetched_at, count(*) FROM evidence e JOIN page p ON p.id = e.page_id "
            "GROUP BY p.id ORDER BY p.id"
        )
        .fetchall()
    )
    assert pages == [(FIRST, 5), (SECOND, 6)]


def test_a_second_run_with_no_new_value_writes_no_change_row(hand):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))
    # no price and no venue this time: the stored values stay
    item = _show("Harbour Concert", "R200", 12, price=EMPTY, venue=EMPTY)
    assert _ingest(hand, SHOW, item, at=SECOND)["updated"] == 1
    assert _one(hand, "SELECT price_text, venue FROM item") == ("Tickets R200", "Town Hall")
    assert _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), at=SECOND)["updated"] == 1
    assert _counts(hand)[3] == 0
    assert len(_rows(hand, "Harbour Concert")) == 1


def test_a_second_run_fills_an_empty_venue_and_logs_it(hand):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12, venue=EMPTY))
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), at=SECOND)
    change = _one(hand, "SELECT field, old_value, new_value FROM change")
    assert change == ("venue", None, "Town Hall")
    assert _one(hand, "SELECT venue FROM item")[0] == "Town Hall"


def test_yearly_on_a_second_run_is_set_and_logged_and_is_never_taken_back(hand):
    text = SHOW + "Held each year\n"
    yearly = {"value": "yes", "quote": "Held each year"}
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))
    _ingest(hand, text, _show("Harbour Concert", "R200", 12, yearly=yearly), at=SECOND)
    assert _one(hand, "SELECT repeats_yearly FROM item")[0] == 1
    change = _one(hand, "SELECT field, old_value, new_value, found_at, actor FROM change")
    assert change == ("repeats_yearly", "0", "1", SECOND, "ingest")
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), at=SECOND)
    assert _one(hand, "SELECT repeats_yearly FROM item")[0] == 1
    assert _counts(hand)[3] == 1


def test_the_same_title_of_a_second_source_or_a_second_town_is_a_new_item(hand):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))
    assert _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), source="second")["stored"] == 1
    text = SHOW + "Stanford\n"
    town = {"value": "Stanford", "quote": "Stanford"}
    assert _ingest(hand, text, _show("Harbour Concert", "R200", 12, town=town))["stored"] == 1
    assert _ingest(hand, SHOW, _show("Harbour", "R200", 12))["stored"] == 1  # a different title
    assert _one(hand, "SELECT count(*) FROM item")[0] == 4
    # each of them is found again
    assert _ingest(hand, text, _show("Harbour Concert", "R200", 12, town=town))["updated"] == 1
    assert _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), source="second")["updated"]
    assert _one(hand, "SELECT count(*) FROM item")[0] == 4


def test_a_weekly_rule_on_a_second_run_adds_only_the_new_dates(hand):
    text = (CASES / "market.txt").read_text(encoding="utf-8")
    market = _load(CASES / "market.json")["items"][0]
    _ingest(hand, text, market)
    assert len(_rows(hand, "Harbour Square Market")) == 78
    assert _ingest(hand, text, market, at=SECOND)["updated"] == 1
    rows = _rows(hand, "Harbour Square Market")
    assert len(rows) == len(set(rows)) == 79
    assert (rows[0][0], rows[-1][0]) == ("2026-11-28", "2028-05-27")  # no row is deleted
    assert _counts(hand)[3] == 0  # a later date of the same rule is not a change


def test_a_season_on_a_second_run_in_the_next_year_adds_one_year(hand):
    item = _item("Whale season", SEASON, yearly=YEARLY)
    _ingest(hand, WHALES, item)
    assert _ingest(hand, WHALES, item, at="2027-02-01T08:00:00+00:00")["updated"] == 1
    assert [row[0] for row in _rows(hand, "Whale season")] == [
        "2026-06-01",
        "2027-06-01",
        "2028-06-01",
        "2029-06-01",
    ]
    assert _counts(hand)[3] == 0  # a later year of the same season is not a change


def test_a_new_date_entry_on_a_second_run_is_one_change_row_for_each_entry(hand):
    text = SHOW + "19 December 2026\n27 to 29 December 2026\nEvery Friday\n"
    assert _ingest(hand, text, _show("Harbour Concert", "R200", 12))["stored"] == 1
    assert _counts(hand)[3] == 0  # the first time is not a change: first_seen is the record
    days = _when("range", (27, 12, 2026), (29, 12, 2026), ["27 to 29 December 2026"])
    rule = _when("weekly", quotes=["Every Friday"], weekday="friday", ongoing=True)
    item = _show("Harbour Concert", "R200", 12, 19, 19)
    item["when"] += [days, rule]
    assert _ingest(hand, text, item, at=SECOND)["updated"] == 1
    changes = (
        hand[0]
        .execute("SELECT field, old_value, new_value, found_at, actor FROM change ORDER BY id")
        .fetchall()
    )
    assert changes == [
        ("when", None, "2026-12-19", SECOND, "ingest"),  # given two times, logged one time
        ("when", None, "2026-12-27/2026-12-29", SECOND, "ingest"),
        ("when", None, "weekly friday", SECOND, "ingest"),
    ]
    # the same answer again, also one week later: no new row
    assert _ingest(hand, text, item, at=SECOND)["updated"] == 1
    assert _ingest(hand, text, item, at="2026-12-07T12:00:00+00:00")["updated"] == 1
    assert _counts(hand)[3] == 3
    # a day that the item has, given as a range of one day: no row is added, so no change
    same = _when("range", (12, 12, 2026), (12, 12, 2026), ["12 December 2026"])
    item = _show("Harbour Concert", "R200") | {"when": [same]}
    assert _ingest(hand, text, item, at=SECOND)["updated"] == 1
    assert _counts(hand)[3] == 3


def test_the_report_counts_each_item_one_time(hand):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))
    items = [_show("Harbour Concert", "R200", 12), _show("Harbour", "R200", 12), None]
    report = _ingest(hand, SHOW, *items, at=SECOND)
    assert (report["stored"], report["updated"], len(report["set_aside"])) == (1, 1, 1)


def test_an_update_that_fails_after_its_first_write_changes_nothing(hand, monkeypatch):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12))
    before = hand[0].execute("SELECT * FROM item").fetchall(), _counts(hand)

    def fail(*_):
        raise ValueError("no evidence")

    monkeypatch.setattr(feed.update, "_write_evidence", fail)
    items = [_show("Harbour Concert", "R250", 12, 19), _show("Harbour", "R250", 19)]
    report = _ingest(hand, SHOW + "Tickets R250\n19 December 2026\n", *items, at=SECOND)
    assert report["set_aside"] == [
        ("Harbour Concert", "malformed item"),
        ("Harbour", "malformed item"),
    ]
    assert (hand[0].execute("SELECT * FROM item").fetchall(), _counts(hand)) == before
    assert not hand[0].in_transaction


# Hand cases 7, 8 and 16 of docs/design.md. There is no retry and no review queue.

ENTRY = "Night Market\nEntry R75\n12 December 2026\n"
DAY = _when("date", (12, 12, 2026), quotes=["12 December 2026"])


def test_case_7_a_value_that_its_quote_does_not_hold_leaves_the_field_empty(hand):
    item = _item("Night Market", DAY, price={"value": "750", "quote": "Entry R75"})
    assert _ingest(hand, ENTRY, item) == {
        "stored": 1,
        "updated": 0,
        "set_aside": [],
        "left_empty": [("Night Market", "price: value not in quote")],  # the report says why
    }
    assert _one(hand, "SELECT price_text FROM item")[0] is None
    assert _one(hand, "SELECT count(*) FROM evidence WHERE field = 'price'")[0] == 0
    assert "750" not in json.dumps(hand[0].execute("SELECT * FROM evidence").fetchall())


def test_case_7_a_false_price_on_a_second_run_does_not_replace_the_price(hand):
    _ingest(hand, ENTRY, _item("Night Market", DAY, price={"value": "R75", "quote": "Entry R75"}))
    item = _item("Night Market", DAY, price={"value": "750", "quote": "Entry R75"})
    assert _ingest(hand, ENTRY, item, at=SECOND)["updated"] == 1
    assert _one(hand, "SELECT price_text FROM item")[0] == "Entry R75"
    assert _counts(hand)[3] == 0


def test_case_8_a_quote_that_is_not_on_the_page_leaves_the_field_empty(hand):
    invented = {"value": "R75", "quote": "Entry fee R75"}
    venue = {"value": "Old Harbour", "quote": "at the Old Harbour"}
    assert _ingest(hand, ENTRY, _item("Night Market", DAY, price=invented, venue=venue))["stored"]
    assert _one(hand, "SELECT price_text, venue FROM item") == (None, None)
    fields = hand[0].execute("SELECT field FROM evidence ORDER BY field").fetchall()
    assert fields == [("title",), ("town",), ("when",)]


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"title": {"value": "Night Market", "quote": "The Night Market"}}, "title: quote not"),
        ({"when": [dict(DAY, quotes=["Sat 12 December 2026"])]}, "when[0]: quote not"),
    ],
)
def test_case_8_a_title_or_a_date_with_a_quote_not_on_the_page_keeps_the_item_out(
    hand, change, reason
):
    report = _ingest(hand, ENTRY, _item("Night Market", DAY) | change)
    assert report == {
        "stored": 0,
        "updated": 0,
        "set_aside": [("Night Market", reason + " on page")],
    }
    assert _counts(hand) == (0, 0, 0, 0)


def test_case_16_an_item_that_a_later_answer_does_not_hold_is_not_changed(hand):
    _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), _show("Harbour", "R200", 12))
    sql = "SELECT * FROM item WHERE title = 'Harbour'"
    before = _one(hand, sql), _rows(hand, "Harbour")
    counts = _counts(hand)
    report = _ingest(hand, SHOW, _show("Harbour Concert", "R200", 12), at=SECOND)
    assert report == {"stored": 0, "updated": 1, "set_aside": []}
    assert (_one(hand, sql), _rows(hand, "Harbour")) == before
    status = _one(hand, "SELECT status, last_seen_at FROM item WHERE title = 'Harbour'")
    assert status == ("live", FIRST)
    # the other item was seen again, and no row of a table is deleted
    assert _one(hand, "SELECT last_seen_at FROM item WHERE title = 'Harbour Concert'")[0] == SECOND
    assert all(after >= was for after, was in zip(_counts(hand), counts, strict=True))
    assert _ingest(hand, SHOW, at=SECOND) == {"stored": 0, "updated": 0, "set_aside": []}
    assert _one(hand, "SELECT count(*) FROM item WHERE last_seen_at = ?", FIRST)[0] == 1


# Real saved pages and real saved answers (T11 format: no "ongoing", no "traveller").


def _real(hand, folder: str, page_id: str, source: str = "hand") -> dict:
    index = _load(PAGES / "index.json")[page_id]
    page = {
        "url": index["url"],
        "text": (PAGES / f"{page_id}.txt").read_text(encoding="utf-8"),
        "fetched_at": index["fetched_at"],
        "status": index["status"],
    }
    answer = _load(Path("research") / folder / "out" / f"{page_id}.claude-haiku-5-5.json")
    return ingest_answer(hand[0], hand[1], source, page, answer)


def test_real_whale_season(hand):
    report = _real(hand, "t11", "x_ht_southern_right_whales")
    assert report == {"stored": 1, "updated": 0, "set_aside": []}
    item = _one(hand, "SELECT title, kind, time_shape, repeats_yearly, town FROM item")
    assert item == ("Southern Right Whales", "season", "season", 1, "Hermanus")
    assert _rows(hand, "Southern Right Whales") == [
        ("2026-06-01", "2026-11-30", "month", "season"),
        ("2027-06-01", "2027-11-30", "month", "season"),
        ("2028-06-01", "2028-11-30", "month", "season"),
    ]
    text = _one(hand, "SELECT text FROM page")[0]
    quotes = dict(hand[0].execute("SELECT field, quote FROM evidence WHERE quote != ''"))
    assert quotes["yearly"] == "whales that visit Walker Bay annually"
    assert "from June till end November" in quotes["when"]
    assert all(quote in text for quote in quotes.values())


def test_real_whale_festival(hand):
    report = _real(hand, "t11", "whale_festival")
    assert report == {"stored": 1, "updated": 0, "set_aside": []}
    item = _one(hand, "SELECT title, kind, time_shape, repeats_yearly, town FROM item")
    assert item == ("Hermanus Whale Festival 2026", "event", "run", 1, "Hermanus")
    assert _rows(hand, item[0]) == [("2026-10-02", "2026-10-04", "day", None)]
    yearly = _one(hand, "SELECT value, quote FROM evidence WHERE field = 'yearly'")
    assert yearly[0] == "yes" and yearly[1].endswith("to the shores of Hermanus each year")


def test_real_festivals_page_yearly_and_months_that_no_quote_proves():
    registry = _load(Path("registry.json"))
    real = open_db(":memory:", registry), registry
    report = _real(real, "t13", "ht_festivals", source="hermanus_tourism")
    yearly = real[0].execute("SELECT title FROM item WHERE repeats_yearly = 1").fetchall()
    assert yearly == [("Whale Festival",)]
    # "every month", "throughout the year": the model gave months 1 to 12. No month name can
    # prove that, so the item is stored as "all year" and its quote goes to the card.
    quotes = dict(
        real[0].execute(
            "SELECT DISTINCT i.title, o.time_text FROM item i JOIN occurrence o "
            "ON o.item_id = i.id WHERE o.precision = 'month' AND o.rule = 'season'"
        )
    )
    assert quotes["Hermanus Country Market"] == "throughout the year"
    assert quotes["Hermanus First Friday Artwalk"] == "On the First Friday of every month"
    assert len(quotes) == 5
    reasons = dict(report["set_aside"])
    assert "Hermanus Country Market" not in reasons
    assert not any("not built" in reason for reason in reasons.values())
