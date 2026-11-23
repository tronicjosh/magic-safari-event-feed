"""Slice 0b.1: a saved answer goes through verify into SQLite, and what_is_on reads it.

Hand cases 1 to 3 of docs/design.md use the fixtures in evals/cases/. The last tests use real
saved pages and the saved model answers of T13 (research/t13/out). No model call.
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
ANSWERS = Path("research/t13/out")
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
    assert (
        'Harbour Square Market · Sat 12 June 2027 (weekly rule: "Every Saturday from 09:00 '
        'to 13:00") · Hermanus'
    ) in answer["text"]
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
    reason = ("Second show", "title: value not in quote")
    assert report == {"stored": 0, "updated": 0, "set_aside": [reason]}

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
        "updated": 0,
        "set_aside": [("Harbour Square Market", "town: town not in the list")],
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
    # the market of the fixture is in the database, so the good item is an update
    assert report["updated"] == 1 and len(report["set_aside"]) == 3
    assert report["stored"] == 0
    assert not db.in_transaction
    middle = _counts(db)
    one = ingest_answer(db, registry, "hand", _page("market"), {"model": "hand", "items": [good]})
    after = _counts(db)
    assert one["updated"] == 1
    # the three bad items left no row: the good item added the same rows with them and alone
    # (no item, no occurrence, its evidence for the page)
    added = [a - b for a, b in zip(middle, before, strict=True)]
    assert added == [a - b for a, b in zip(after, middle, strict=True)]
    assert added[:2] == [0, 0] and added[2] > 0


def test_an_item_that_is_not_stored_leaves_no_row(hand):
    db, registry = hand
    before = _counts(db)
    answer = _load(CASES / "show.json")
    # The last entry passes the checks of verify, and update can not store it: months with
    # an end year and no start year. The 20 dates before it must leave no row.
    answer["items"][0]["when"].append(
        {
            "kind": "months",
            "start": {"day": 0, "month": 6, "year": 0},
            "end": {"day": 0, "month": 6, "year": 2027},
            "weekday": "",
            "quotes": ["Tue 1 June 2027 19:30"],
        }
    )
    report = ingest_answer(db, registry, "hand", _page("show"), answer)
    assert report["stored"] == 0 and report["updated"] == 0
    assert "months: an end year needs a start year" in report["set_aside"][0][1]
    assert _counts(db) == before


def test_a_town_that_fails_the_check_does_not_get_the_default_town(hand):
    db, registry = hand
    before = _counts(db)
    answer = _load(CASES / "market.json")
    answer["items"][0]["town"] = {"value": "Stanford", "quote": "not on the page"}
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report == {
        "stored": 0,
        "updated": 0,
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
    assert not any(line.startswith("Every Saturday") for line in answer["text"].splitlines())


def test_weekly_rows_start_on_the_first_such_day_after_the_ingest(hand):
    db, _ = hand
    rows = db.execute(
        "SELECT min(start_date), count(*), count(DISTINCT start_date) FROM occurrence o "
        "JOIN item i ON i.id = o.item_id WHERE i.title = 'Harbour Square Market'"
    ).fetchone()
    assert rows == ("2026-11-28", 78, 78)  # the ingest is on Monday 23 November 2026


# The model decides, with proof: town from the list, a weekly rule with no end, two bars.


def _market(**changes) -> dict:
    answer = _load(CASES / "market.json")
    answer["items"][0].update(changes)
    return answer


def test_a_town_that_the_model_marks_as_outside_is_not_stored(hand):
    db, registry = hand
    answer = _market(town={"value": "outside", "quote": "Harbour Square, Hermanus"})
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report == {
        "stored": 0,
        "updated": 0,
        "set_aside": [("Harbour Square Market", "town: outside the place")],
    }


def test_the_model_chooses_a_town_of_the_list_and_the_quote_is_page_text(hand):
    db, registry = hand
    # "Stanford" is not in the quote: the choice is the model's, the quote is the proof.
    answer = _market(
        title={"value": "Harbour Square", "quote": "Harbour Square Market"},
        town={"value": "Stanford", "quote": "Harbour Square, Hermanus"},
    )
    assert ingest_answer(db, registry, "hand", _page("market"), answer)["stored"] == 1
    town = db.execute("SELECT town FROM item WHERE title = 'Harbour Square'").fetchone()[0]
    assert town == "Stanford"


def test_a_weekly_rule_that_is_not_marked_as_ongoing_is_not_stored(hand):
    db, registry = hand
    answer = _market()
    answer["items"][0]["when"][0]["ongoing"] = False
    report = ingest_answer(db, registry, "hand", _page("market"), answer)
    assert report["stored"] == 0
    assert "not marked as a rule with no end" in report["set_aside"][0][1]
    del answer["items"][0]["when"][0]["ongoing"]
    assert ingest_answer(db, registry, "hand", _page("market"), answer)["stored"] == 0


@pytest.mark.parametrize(
    "quote",
    [
        "Every Wednesday in December 2026 from 17:00",
        "Saturday 5 December 2026 at 19:00",
        "Every Saturday until 12 March",
        "Saturdays in 2027",
        "Saturdays 5 & 12 from 09:00",
        "Saturday 05/12/2026",
        # date forms that a list of patterns missed (blind review, round 2)
        "Saturday 05.12.2026",
        "Saturday 5/12",
        "Saturday 5/12/26",
        "Every Saturday until 12/03",
        "Saturday 5: carols",
        "Saturday 5th:",
        "Saturday #5",
        "Saturday 5.12",
        "Every Saturday in December",
        # accepted loss: a clock time with no minutes looks like a day number
        "Saturday 9 - 1pm",
    ],
)
def test_a_weekly_quote_that_holds_a_date_fails_the_check(quote):
    from feed.verify import check_when

    weekday = "wednesday" if "Wednesday" in quote else "saturday"
    when = {"kind": "weekly", "start": ZERO, "end": ZERO, "weekday": weekday, "quotes": [quote]}
    assert check_when(when) == ["weekly quote holds a date or a number"]


@pytest.mark.parametrize(
    "quote",
    [
        "Every Saturday from 09:00 – 14:00",
        "Join us every Saturday morning at 8:00am",
        "Saturdays: ParkRun at 8:00",
        "at 08:00 every Saturday",
        "Saterdae 14h00 tot 17h30",
    ],
)
def test_a_weekly_quote_with_a_clock_time_passes_the_check(quote):
    from feed.verify import check_when

    when = {"kind": "weekly", "start": ZERO, "end": ZERO, "weekday": "saturday", "quotes": [quote]}
    assert check_when(when) == []


@pytest.mark.parametrize("town", [[], 0, False, {}, "Hermanus", {"value": "  ", "quote": "x"}])
def test_a_town_of_a_wrong_type_does_not_get_the_default_town(hand, town):
    db, registry = hand
    before = _counts(db)
    report = ingest_answer(db, registry, "hand", _page("market"), _market(town=town))
    assert report["stored"] == 0
    assert report["set_aside"][0][1].startswith("town: ")
    assert _counts(db) == before


def test_a_date_from_a_weekly_rule_is_shown_as_a_rule_with_its_quote(hand):
    db, registry = hand
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 12), date(2027, 6, 12))
    cards = {card["title"]: card for card in answer["data"]["groups"][0]["cards"]}
    assert cards["Harbour Square Market"]["rule"] == "Every Saturday from 09:00 to 13:00"
    assert cards["The Whale Song: a musical"]["rule"] is None
    assert "The Whale Song: a musical · Sat 12 June 2027 (confirmed) · Hermanus" in answer["text"]


def test_the_traveller_bar_is_soft_the_item_is_shown_in_its_own_group(hand):
    db, registry = hand
    title = {"value": "Harbour Square", "quote": "Harbour Square Market"}
    below = _market(title=title, traveller={"value": "no", "quote": "Harbour Square Market"})
    assert ingest_answer(db, registry, "hand", _page("market"), below)["stored"] == 1
    answer = what_is_on(db, registry, "hermanus", date(2027, 6, 12), date(2027, 6, 12))
    groups = {
        group["name"]: [c["title"] for c in group["cards"]] for group in answer["data"]["groups"]
    }
    assert groups["below the traveller bar"] == ["Harbour Square"]
    assert "Harbour Square" not in groups["dated"]
    counts = answer["data"]["counts"]
    assert counts["items"] == sum(len(titles) for titles in groups.values()) == 3
    assert counts["groups"]["below the traveller bar"] == 1
    assert "3 items: 2 dated" in answer["text"] and "1 below the traveller bar" in answer["text"]
    row = db.execute(
        "SELECT e.value, e.quote FROM evidence e JOIN item i ON i.id = e.item_id "
        "WHERE i.title = 'Harbour Square' AND e.field = 'traveller'"
    ).fetchone()
    assert row == ("no", "Harbour Square Market")


def test_a_traveller_no_with_a_quote_that_is_not_on_the_page_does_not_count(hand):
    db, registry = hand
    title = {"value": "Harbour Square", "quote": "Harbour Square Market"}
    answer = _market(title=title, traveller={"value": "no", "quote": "a quiz night"})
    assert ingest_answer(db, registry, "hand", _page("market"), answer)["stored"] == 1
    below = db.execute("SELECT below_bar FROM item WHERE title = 'Harbour Square'").fetchone()[0]
    assert below == 0


def test_a_range_card_says_that_each_day_is_not_stated(hand):
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
            "ongoing": False,
            "quotes": ["Tue 8 June 2027 19:30", "Thu 10 June 2027 19:30"],
        }
    ]
    assert ingest_answer(db, registry, "hand", _page("show"), answer)["stored"] == 1
    text = what_is_on(db, registry, "hermanus", date(2027, 6, 9), date(2027, 6, 9))["text"]
    lines = [line for line in text.splitlines() if "The Whale Song" in line]
    assert lines == [
        (
            "[event · other] The Whale Song · Tue 8 June 2027 - Thu 10 June 2027 "
            "(confirmed; a range, each day is not stated) · Hermanus"
        ),
        "[event · other] The Whale Song: a musical · Wed 9 June 2027 (confirmed) · Hermanus",
    ]


def test_trap_page_with_the_real_model_answer_gives_no_invented_weekly_dates():
    """The model answer of T13 for evals/cases/weekly_traps.txt, a page made to mislead."""
    registry = _load(CASES / "registry.json")
    db = open_db(":memory:", registry)
    answer = _load(ANSWERS / "weekly_traps.claude-haiku-5-5.json")
    ingest_answer(db, registry, "hand", _page("weekly_traps"), answer)
    weekly = db.execute(
        "SELECT i.title, count(*) FROM item i JOIN occurrence o ON o.item_id = i.id "
        "GROUP BY i.id HAVING count(*) > 1"
    ).fetchall()
    assert weekly == [("Fish Market", 78)]
    # the Wednesday rule is for December 2026 only, and the museum is closed on Sunday
    wednesday = what_is_on(db, registry, "hermanus", date(2027, 6, 9), date(2027, 6, 9))
    sunday = what_is_on(db, registry, "hermanus", date(2027, 6, 13), date(2027, 6, 13))
    saturday = what_is_on(db, registry, "hermanus", date(2027, 6, 12), date(2027, 6, 12))
    assert _titles(wednesday) == _titles(sunday) == _titles(saturday) == []
    carols = what_is_on(db, registry, "hermanus", date(2026, 12, 5), date(2026, 12, 5))
    assert _titles(carols) == ["Carols by Candlelight"]


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
    assert cards["Akwaaba Market"]["town"] == "Hermanus"
    # The page says "Hemel-en-Aarde village"; the model chose the town of the list.
    market = cards["Hermanuspietersfontein Food and Wine Market"]
    assert (market["town"], market["when"]) == ("Hemel-en-Aarde", "Sat 12 June 2027")
    week = what_is_on(db, registry, "hermanus", date(2027, 6, 7), date(2027, 6, 10))
    assert "Akwaaba Market" not in _titles(week)


def test_real_single_date_item(real):
    db, registry, reports = real
    answer = what_is_on(db, registry, "hermanus", date(2026, 11, 18), date(2026, 11, 18))
    cards = {c["title"]: c for g in answer["data"]["groups"] for c in g["cards"]}
    assert cards["Book Launch: Treasured Islands"]["when"] == "Wed 18 November 2026"
    assert cards["5-Course Dinner Fundraiser"]["town"] == "Stanford"
    assert "Bring & Braai" not in cards  # Pringle Bay is not a town of the place
    set_aside = reports["overstrand_weekend"]["set_aside"]
    assert ("Bring & Braai", "town: outside the place") in set_aside
    assert ("Beach Clean-up", "town: outside the place") in set_aside
    assert answer["data"]["counts"]["items"] == len(cards)


def test_real_report_counts_each_item_one_time(real):
    _, _, reports = real
    for page_id, report in reports.items():
        answer = _load(ANSWERS / f"{page_id}.claude-haiku-5-5.json")
        counted = report["stored"] + report["updated"] + len(report["set_aside"])
        assert counted == len(answer["items"])
