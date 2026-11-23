"""Slice 0b.1: a saved answer goes through verify into SQLite, and what_is_on reads it.

Hand cases 1 to 3 of docs/design.md use the fixtures in evals/cases/. The last tests use real
saved pages and the saved model answers of T2. No model call.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from feed.read import what_is_on
from feed.store import open_db
from feed.update import ingest_answer

CASES = Path("evals/cases")
PAGES = Path("evals/pages")
ANSWERS = Path("research/t2/out")
INGESTED = "2026-11-23T12:00:00+00:00"
ZERO = {"day": 0, "month": 0, "year": 0}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ingest_case(db, registry, name: str) -> dict:
    page = {
        "url": f"https://example.org/{name}",
        "text": (CASES / f"{name}.txt").read_text(encoding="utf-8"),
        "fetched_at": INGESTED,
        "status": 200,
    }
    return ingest_answer(db, registry, "hand", page, _load(CASES / f"{name}.json"))


@pytest.fixture
def hand():
    registry = _load(CASES / "registry.json")
    db = open_db(":memory:", registry)
    for name in ("market", "show"):
        report = _ingest_case(db, registry, name)
        assert report["stored"] == 1 and not report["set_aside"]
    return db, registry


def _titles(answer: dict) -> list[str]:
    return [card["title"] for group in answer["data"]["groups"] for card in group["cards"]]


def test_case_1_market_each_saturday_no_match(hand):
    db, registry = hand
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 7), date(2027, 6, 10))
    assert "Harbour Square Market" not in _titles(answer)


def test_case_2_market_each_saturday_match(hand):
    db, registry = hand
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 11), date(2027, 6, 13))
    # The show of case 3 is also on Friday 11 and Saturday 12 June.
    assert _titles(answer) == ["The Whale Song: a musical", "Harbour Square Market"]
    card = answer["data"]["groups"][0]["cards"][1]
    assert card["when"] == "Sat 12 June 2027"
    assert card["town"] == "Hermanus"
    assert "Harbour Square Market · Sat 12 June 2027 (confirmed) · Hermanus" in answer["text"]
    assert answer["data"]["counts"]["items"] == 2


def test_case_3_show_with_many_dates_no_match(hand):
    db, registry = hand
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 13), date(2027, 6, 14))
    assert _titles(answer) == []
    assert answer["data"]["counts"]["items"] == 0


def test_show_is_returned_on_a_day_that_it_is_on(hand):
    db, registry = hand
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 15), date(2027, 6, 15))
    assert _titles(answer) == ["The Whale Song: a musical"]
    card = answer["data"]["groups"][0]["cards"][0]
    assert card["when"] == "Tue 15 June 2027"
    assert card["price"] == "Tickets R250"  # the quote: the check proves only the number


def test_weekly_rule_stops_18_months_after_the_ingest(hand):
    db, _ = hand
    last = db.execute(
        "SELECT max(start_date) FROM occurrence o JOIN item i ON i.id = o.item_id "
        "WHERE i.title = 'Harbour Square Market'"
    ).fetchone()[0]
    assert last == "2028-05-20"  # the last Saturday on or before 23 May 2028


def test_each_stored_fact_has_evidence_with_a_quote_on_the_page(hand):
    db, _ = hand
    rows = db.execute(
        "SELECT e.field, e.quote, p.text FROM evidence e JOIN page p ON p.id = e.page_id"
    ).fetchall()
    assert {row[0] for row in rows} >= {"title", "town", "venue", "price", "when"}
    for _, quote, text in rows:
        assert all(part in text for part in quote.split(" | "))


def test_a_field_that_fails_the_check_stays_empty(hand):
    db, registry = hand
    answer = _load(CASES / "show.json")
    answer["items"][0]["title"] = {"value": "Second show", "quote": "The Whale Song: a musical"}
    answer["items"][0]["price"] = {"value": "R25", "quote": "Tickets R250"}
    page = {"url": "u", "text": (CASES / "show.txt").read_text(encoding="utf-8")}
    page |= {"fetched_at": INGESTED, "status": 200}
    report = ingest_answer(db, registry, "hand", page, answer)
    assert report == {"stored": 0, "set_aside": [("Second show", "title: value not in quote")]}

    answer["items"][0]["title"] = {"value": "The Whale Song", "quote": "The Whale Song"}
    report = ingest_answer(db, registry, "hand", page, answer)
    assert report["stored"] == 1
    price = db.execute("SELECT price_text FROM item WHERE title = 'The Whale Song'").fetchone()
    assert price[0] is None


def test_an_item_with_a_false_date_is_not_stored(hand):
    db, registry = hand
    answer = _load(CASES / "market.json")
    answer["items"][0]["when"][0]["weekday"] = "sunday"
    page = {"url": "u", "text": (CASES / "market.txt").read_text(encoding="utf-8")}
    page |= {"fetched_at": INGESTED, "status": 200}
    report = ingest_answer(db, registry, "hand", page, answer)
    assert report["stored"] == 0
    assert report["set_aside"][0][1].startswith("when[0]")


def test_a_town_outside_the_place_is_not_given_the_default_town(hand):
    db, registry = hand
    answer = _load(CASES / "market.json")
    text = (CASES / "market.txt").read_text(encoding="utf-8").replace("Hermanus", "Pringle Bay")
    answer["items"][0]["town"] = {"value": "Pringle Bay", "quote": "Harbour Square, Pringle Bay"}
    answer["items"][0]["venue"] = {"value": "", "quote": ""}
    page = {"url": "u", "text": text, "fetched_at": INGESTED, "status": 200}
    report = ingest_answer(db, registry, "hand", page, answer)
    assert report == {
        "stored": 0,
        "set_aside": [("Harbour Square Market", "town: Pringle Bay is not in the place")],
    }


def test_same_query_gives_the_same_text(hand):
    db, registry = hand
    first = what_is_on(db, registry, "hermanus", date(2027, 6, 1), date(2027, 6, 30))
    second = what_is_on(db, registry, "hermanus", date(2027, 6, 1), date(2027, 6, 30))
    assert first == second
    assert _titles(first) == ["The Whale Song: a musical", "Harbour Square Market"]


# Faults that the blind review found. Each test failed before its repair.


def _counts(db) -> tuple:
    return tuple(
        db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("item", "occurrence", "evidence")
    )


def _page(name: str) -> dict:
    text = (CASES / f"{name}.txt").read_text(encoding="utf-8")
    return {"url": "u", "text": text, "fetched_at": INGESTED, "status": 200}


def test_an_item_that_is_not_an_object_does_not_stop_the_page(hand):
    db, registry = hand
    before = _counts(db)
    good = _load(CASES / "market.json")["items"][0]
    bad = dict(good, when=[{"kind": "date"}])
    answer = {"model": "hand", "items": [None, "text", bad, good]}
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report["stored"] == 1 and len(report["set_aside"]) == 3
    assert not db.in_transaction
    one = ingest_answer(db, registry, "hand", _page("market"), {"model": "hand", "items": [good]})
    after = _counts(db)
    assert one["stored"] == 1
    # the three bad items left no row: the two good items added the same number of rows
    assert [(a - b) % 2 for a, b in zip(after, before, strict=True)] == [0, 0, 0]
    assert after[0] - before[0] == 2


def test_an_item_that_is_not_stored_leaves_no_row(hand):
    db, registry = hand
    before = _counts(db)
    answer = _load(CASES / "show.json")
    answer["items"][0]["when"].append(
        {
            "kind": "months",
            "start": {"day": 0, "month": 6, "year": 2027},
            "end": {"day": 0, "month": 6, "year": 2027},
            "weekday": "",
            "quotes": ["Tue 1 June 2027 19:30"],
        }
    )
    report = ingest_answer(db, registry, "hand", _page("show"), answer)
    assert report["stored"] == 0
    assert "months is not built yet" in report["set_aside"][0][1]
    assert _counts(db) == before


def test_a_town_that_fails_the_check_does_not_get_the_default_town(hand):
    db, registry = hand
    before = _counts(db)
    answer = _load(CASES / "market.json")
    answer["items"][0]["town"] = {"value": "Pringle Bay", "quote": "not on the page"}
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report == {
        "stored": 0,
        "set_aside": [("Harbour Square Market", "town: quote not on page")],
    }
    assert _counts(db) == before


def test_a_source_with_no_default_town_does_not_guess(hand):
    db, registry = hand
    registry["sources"][0]["default_town"] = None
    answer = _load(CASES / "market.json")
    answer["items"][0]["town"] = {"value": "", "quote": ""}
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report["set_aside"][0][1] == "town: not stated, and the source has no default town"


def test_the_default_town_has_an_evidence_row(hand):
    db, registry = hand
    answer = _load(CASES / "market.json")
    answer["items"][0]["title"] = {"value": "Harbour Square", "quote": "Harbour Square Market"}
    answer["items"][0]["town"] = {"value": "", "quote": ""}
    assert ingest_answer(db, registry, "hand", _page("market"), answer)["stored"] == 1
    row = db.execute(
        "SELECT e.value, e.model FROM evidence e JOIN item i ON i.id = e.item_id "
        "WHERE i.title = 'Harbour Square' AND e.field = 'town'"
    ).fetchone()
    assert row == ("Hermanus", "registry default")


def test_a_range_is_one_row_and_its_edges_are_in_the_window(hand):
    db, registry = hand
    answer = _load(CASES / "show.json")
    item = answer["items"][0]
    item["title"] = {"value": "The Whale Song", "quote": "The Whale Song"}
    item["when"] = [
        {
            "kind": "range",
            "start": {"day": 8, "month": 6, "year": 2027},
            "end": {"day": 10, "month": 6, "year": 2027},
            "weekday": "",
            "quotes": ["Tue 8 June 2027 19:30", "Thu 10 June 2027 19:30"],
        }
    ]
    assert ingest_answer(db, registry, "hand", _page("show"), answer)["stored"] == 1

    def on(first: int, last: int) -> bool:
        answer = what_is_on(db, registry, "hermanus", date(2027, 6, first), date(2027, 6, last))
        return "The Whale Song" in _titles(answer)

    assert [on(6, 7), on(7, 8), on(10, 11), on(11, 11)] == [False, True, True, False]
    card = next(
        card
        for card in what_is_on(db, registry, "hermanus", date(2027, 6, 9), date(2027, 6, 9))[
            "data"
        ]["groups"][0]["cards"]
        if card["title"] == "The Whale Song"
    )
    assert card["when"] == "Tue 8 June 2027 - Thu 10 June 2027"


def test_the_same_day_is_on_a_card_one_time(hand):
    db, registry = hand
    answer = _load(CASES / "show.json")
    item = answer["items"][0]
    item["title"] = {"value": "The Whale Song", "quote": "The Whale Song"}
    item["when"] = [item["when"][0], item["when"][0]]
    assert ingest_answer(db, registry, "hand", _page("show"), answer)["stored"] == 1
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 1), date(2027, 6, 1))
    whens = {card["title"]: card["when"] for card in answer["data"]["groups"][0]["cards"]}
    assert whens["The Whale Song"] == "Tue 1 June 2027"


def test_order_is_first_day_in_the_window_then_title():
    registry = _load(CASES / "registry.json")
    db = open_db(":memory:", registry)
    text = "Charlie\nBravo\nalpha\n5 June 2027\n1 June 2027\n30 June 2027\n"

    def item(title: str, first: int, last: int) -> dict:
        when = {
            "kind": "range" if last != first else "date",
            "start": {"day": first, "month": 6, "year": 2027},
            "end": {"day": last, "month": 6, "year": 2027} if last != first else dict(ZERO),
            "weekday": "",
            "quotes": [f"{first} June 2027", f"{last} June 2027"],
        }
        empty = {"value": "", "quote": ""}
        title = {"value": title, "quote": title}
        return {"title": title, "town": empty, "venue": empty, "price": empty, "when": [when]}

    items = [item("Charlie", 5, 5), item("Bravo", 1, 30), item("alpha", 5, 5)]
    page = {"url": "u", "text": text, "fetched_at": INGESTED, "status": 200}
    assert (
        ingest_answer(db, registry, "hand", page, {"model": "hand", "items": items})["stored"] == 3
    )
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 5), date(2027, 6, 6))
    assert _titles(answer) == ["alpha", "Bravo", "Charlie"]


def test_an_item_of_a_second_place_with_the_same_town_name_is_not_returned(hand):
    db, registry = hand
    registry["places"]["other"] = {"name": "Other", "towns": ["Stanford"]}
    registry["sources"].append(
        dict(registry["sources"][0], id="other_source", place="other", default_town="Stanford")
    )
    db = open_db(":memory:", registry)
    answer = _load(CASES / "market.json")
    answer["items"][0]["town"] = {"value": "", "quote": ""}
    assert ingest_answer(db, registry, "other_source", _page("market"), answer)["stored"] == 1
    assert _titles(what_is_on(db, registry, "hermanus", date(2027, 6, 12), date(2027, 6, 12))) == []
    assert _titles(what_is_on(db, registry, "other", date(2027, 6, 12), date(2027, 6, 12))) == [
        "Harbour Square Market"
    ]


def test_a_default_town_outside_the_place_is_a_registry_error():
    registry = _load(CASES / "registry.json")
    registry["sources"][0]["default_town"] = "Kleinmond"
    with pytest.raises(ValueError, match="default town"):
        open_db(":memory:", registry)


def test_a_window_that_ends_before_it_starts_is_an_error(hand):
    db, registry = hand
    with pytest.raises(ValueError, match="window"):
        what_is_on(db, registry, "hermanus", date(2027, 6, 7), date(2027, 6, 5))


def test_a_title_over_two_lines_is_stored_as_one_line(hand):
    db, registry = hand
    answer = _load(CASES / "market.json")
    answer["items"][0]["title"] = {
        "value": "Harbour Square Market\nEvery Saturday",
        "quote": "Harbour Square Market\nEvery Saturday",
    }
    assert ingest_answer(db, registry, "hand", _page("market"), answer)["stored"] == 1
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 12), date(2027, 6, 12))
    assert "Harbour Square Market Every Saturday" in _titles(answer)
    assert len(answer["text"].splitlines()) == 5 + 3 + 3 * len(_titles(answer)) + 3 * 2 - 1


def test_weekly_rows_start_on_the_first_such_day_after_the_ingest(hand):
    db, _ = hand
    rows = db.execute(
        "SELECT min(start_date), count(*), count(DISTINCT start_date) FROM occurrence o "
        "JOIN item i ON i.id = o.item_id WHERE i.title = 'Harbour Square Market'"
    ).fetchone()
    assert rows == ("2026-11-28", 78, 78)  # the ingest is on Monday 23 November 2026


# Real saved pages and real saved answers.


@pytest.fixture
def real():
    registry = _load(Path("registry.json"))
    db = open_db(":memory:", registry)
    index = _load(PAGES / "index.json")
    reports = {}
    for source_id, page_id in (
        ("hermanus_tourism", "ht_festivals"),
        ("overstrand_municipality", "overstrand_weekend"),
    ):
        page = {
            "url": index[page_id]["url"],
            "text": (PAGES / f"{page_id}.txt").read_text(encoding="utf-8"),
            "fetched_at": index[page_id]["fetched_at"],
            "status": index[page_id]["status"],
        }
        answer = _load(ANSWERS / f"{page_id}.claude-haiku-5-5.json")
        reports[page_id] = ingest_answer(db, registry, source_id, page, answer)
    return db, registry, reports


def test_real_weekly_market_is_on_a_saturday_only(real):
    db, registry, _ = real
    weekend = what_is_on(db, registry, "hermanus", date(2027, 6, 11), date(2027, 6, 13))
    cards = {c["title"]: c for g in weekend["data"]["groups"] for c in g["cards"]}
    assert cards["Akwaaba Market"]["when"] == "Sat 12 June 2027"
    assert cards["Akwaaba Market"]["town"] == "Hermanus"  # no town on the page: source default
    week = what_is_on(db, registry, "hermanus", date(2027, 6, 7), date(2027, 6, 10))
    assert "Akwaaba Market" not in _titles(week)


def test_real_single_date_item(real):
    db, registry, reports = real
    answer = what_is_on(db, registry, "hermanus", date(2026, 11, 18), date(2026, 11, 18))
    cards = {c["title"]: c for g in answer["data"]["groups"] for c in g["cards"]}
    assert cards["Book Launch: Treasured Islands"]["when"] == "Wed 18 November 2026"
    assert cards["5-Course Dinner Fundraiser"]["town"] == "Stanford"
    assert "Bring & Braai" not in cards  # Pringle Bay is not a town of the place
    assert ("Bring & Braai", "town: Pringle Bay is not in the place") in reports[
        "overstrand_weekend"
    ]["set_aside"]
    assert "Beach Clean-up" not in cards  # no town on the page, and a regional source
    assert answer["data"]["counts"]["items"] == len(cards)


def test_real_report_counts_each_item_one_time(real):
    _, _, reports = real
    for page_id, report in reports.items():
        answer = _load(ANSWERS / f"{page_id}.claude-haiku-5-5.json")
        assert report["stored"] + len(report["set_aside"]) == len(answer["items"])
