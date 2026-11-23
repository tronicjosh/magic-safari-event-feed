"""The three read operations on rows that SQL writes, in the form of feed/schema.sql.

Hand cases 4, 5, 6, 10, 12, 18, 19 and 24 of docs/design.md, with the dates of the design.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from feed.read import GROUPS, tell_me_more, what_changed, what_is_on, when_to_go
from feed.store import open_db

INGESTED = "2026-11-23T12:00:00+00:00"
SEASON = 'season, no year stated: "quote of the date"'


@pytest.fixture
def feed():
    registry = json.loads(Path("evals/cases/registry.json").read_text(encoding="utf-8"))
    registry["not_collected"] = [
        {"name": "Tickets", "reason": "the API needs a key", "declares": "136 events"},
        {"name": "Other tickets", "reason": "the search needs a browser", "declares": None},
    ]
    db = open_db(":memory:", registry)
    db.execute(
        "INSERT INTO page (id, source_id, url, content_hash, fetched_at, http_status, text) "
        "VALUES (1, 'hand', 'https://example.org/page', 'hash', ?, 200, 'text')",
        (INGESTED,),
    )
    return db, registry


def add(db, title, occurrences, kind="event", category="other", yearly=0, below=0, **fields):
    """One live item with a title Evidence row. An occurrence: (start, end, precision, rule)."""
    item_id = db.execute(
        "INSERT INTO item (kind, title, town, time_shape, repeats_yearly, below_bar, category, "
        "venue, price_text, source_link, first_seen, last_seen_at, last_verified, status) "
        "VALUES (?, ?, 'Hermanus', 'x', ?, ?, ?, ?, ?, 'https://example.org/page', ?, ?, ?, ?)",
        (
            kind,
            title,
            yearly,
            below,
            category,
            fields.get("venue"),
            fields.get("price"),
            INGESTED,
            INGESTED,
            INGESTED,
            fields.get("status", "live"),
        ),
    ).lastrowid
    db.execute(
        "INSERT INTO evidence (item_id, field, value, quote, page_id, model) "
        "VALUES (?, 'title', ?, ?, 1, 'model-a')",
        (item_id, title, title),
    )
    for start, end, precision, rule in occurrences:
        db.execute(
            "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text, rule) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (item_id, start, end, precision, fields.get("time_text", "quote of the date"), rule),
        )
    db.commit()
    return item_id


def season(first_month: int, last_month: int, years=(2026, 2027, 2028)) -> list[tuple]:
    """A standing season with no year: one month row for each year, as the ingest writes it."""
    last_day = {4: 30, 11: 30}[last_month]
    return [
        (
            f"{year}-{first_month:02d}-01",
            f"{year + (last_month < first_month)}-{last_month:02d}-{last_day}",
            "month",
            "season",
        )
        for year in years
    ]


def whales(db, **fields) -> int:
    return add(db, "Whale season", season(6, 11), kind="season", category="nature", **fields)


def festival(db, **fields) -> int:
    rows = [("2026-06-06", "2026-06-15", "day", None)]
    return add(db, "Arts Festival", rows, category="festival", yearly=1, **fields)


def on(db, registry, first: str, last: str) -> dict:
    return what_is_on(db, registry, "hermanus", date.fromisoformat(first), date.fromisoformat(last))


def groups(answer: dict) -> dict:
    return {g["name"]: [card["title"] for card in g["cards"]] for g in answer["data"]["groups"]}


def titles(answer: dict) -> list[str]:
    return [title for cards in groups(answer).values() for title in cards]


# Hand case 4: a season.


def test_case_4_whales_june_to_november(feed):
    db, registry = feed
    whales(db)
    august = on(db, registry, "2027-08-20", "2027-08-25")
    assert groups(august) == {
        "dated": [],
        "seasons and experiences": ["Whale season"],
        "not confirmed": [],
        "below the traveller bar": [],
    }
    card = august["data"]["groups"][1]["cards"][0]
    assert card["when"] == "June - November"  # the page states no year, so the card shows none
    assert (
        f"[season · nature] Whale season · June - November ({SEASON}) · Hermanus"
        in (august["text"])
    )
    february = on(db, registry, "2027-02-10", "2027-02-15")
    assert titles(february) == []
    assert february["data"]["counts"]["items"] == 0


def test_a_month_row_matches_when_its_range_overlaps_the_window(feed):
    db, registry = feed
    whales(db)
    hits = [
        bool(titles(on(db, registry, first, last)))
        for first, last in (
            ("2027-05-20", "2027-05-31"),
            ("2027-05-31", "2027-06-01"),
            ("2027-11-30", "2027-12-03"),
            ("2027-12-01", "2027-12-03"),
        )
    ]
    assert hits == [False, True, True, False]


def test_a_window_over_two_years_shows_a_season_one_time(feed):
    db, registry = feed
    whales(db)
    answer = on(db, registry, "2026-11-01", "2027-06-30")
    assert titles(answer) == ["Whale season"]
    assert answer["data"]["groups"][1]["cards"][0]["when"] == "June - November"


def test_a_season_over_the_year_end_in_january_and_in_july(feed):
    db, registry = feed
    add(db, "Summer season", season(11, 4), kind="season")
    january = on(db, registry, "2027-01-10", "2027-01-15")
    assert groups(january)["seasons and experiences"] == ["Summer season"]
    assert january["data"]["groups"][1]["cards"][0]["when"] == "November - April"
    assert titles(on(db, registry, "2027-07-10", "2027-07-15")) == []


def test_a_month_of_an_event_is_dated_and_shows_its_year(feed):
    db, registry = feed
    add(db, "Food month", [("2026-10-01", "2026-10-31", "month", None)])
    add(db, "Flower months", [("2026-08-01", "2026-09-30", "month", None)])
    add(db, "Summer months", [("2026-12-01", "2027-01-31", "month", None)])
    answer = on(db, registry, "2026-10-10", "2026-10-12")
    assert groups(answer)["dated"] == ["Food month"]
    note = "(confirmed; a range, each day is not stated)"  # the days in the month are not
    assert f"Food month · October 2026 {note} · Hermanus" in answer["text"]
    assert titles(on(db, registry, "2026-11-01", "2026-11-05")) == []
    whens = {
        card["title"]: card["when"]
        for card in on(db, registry, "2026-09-30", "2026-12-01")["data"]["groups"][0]["cards"]
    }
    assert whens == {
        "Flower months": "August - September 2026",
        "Food month": "October 2026",
        "Summer months": "December 2026 - January 2027",
    }


# Hand case 5: held each year, and no page states the new dates.


def test_case_5_yearly_festival_is_not_confirmed_with_last_held(feed):
    db, registry = feed
    festival(db)
    answer = on(db, registry, "2027-06-08", "2027-06-12")
    assert groups(answer) == {
        "dated": [],
        "seasons and experiences": [],
        "not confirmed": ["Arts Festival"],
        "below the traveller bar": [],
    }
    card = answer["data"]["groups"][2]["cards"][0]
    assert card["confirmed"] is False
    assert card["when"] == "Last held Sat 6 June 2026 - Mon 15 June 2026"
    line = next(line for line in answer["text"].splitlines() if "Arts Festival" in line)
    assert line == (
        "[event · festival] Arts Festival · not confirmed "
        "(Last held Sat 6 June 2026 - Mon 15 June 2026) · Hermanus"
    )
    # the moved date is never shown: 2027 is only in the header of the answer
    assert "2027" not in json.dumps(card)
    assert [line for line in answer["text"].splitlines() if "2027" in line] == [
        "what_is_on · Hermanus · 8 June 2027 - 12 June 2027 · as of 2026-11-23"
    ]
    assert answer["data"]["counts"]["items"] == 1
    assert answer["data"]["counts"]["groups"]["not confirmed"] == 1


def test_case_5_yearly_festival_is_not_returned_for_august(feed):
    db, registry = feed
    festival(db)
    assert titles(on(db, registry, "2027-08-08", "2027-08-12")) == []


def test_case_5_edges_of_the_moved_dates_and_a_second_year(feed):
    db, registry = feed
    festival(db)
    hits = [
        bool(titles(on(db, registry, first, last)))
        for first, last in (
            ("2027-06-01", "2027-06-05"),
            ("2027-06-05", "2027-06-06"),
            ("2027-06-15", "2027-06-20"),
            ("2027-06-16", "2027-06-20"),
            ("2028-06-08", "2028-06-12"),  # two years on
        )
    ]
    assert hits == [False, True, True, False, True]


def test_an_item_that_is_not_yearly_is_never_projected(feed):
    db, registry = feed
    add(db, "One concert", [("2026-06-06", "2026-06-15", "day", None)])
    assert titles(on(db, registry, "2027-06-08", "2027-06-12")) == []
    assert titles(on(db, registry, "2026-06-08", "2026-06-12")) == ["One concert"]


def test_a_yearly_item_with_a_real_date_in_the_window_is_dated_only(feed):
    db, registry = feed
    item_id = festival(db)
    assert groups(on(db, registry, "2026-06-08", "2026-06-12"))["dated"] == ["Arts Festival"]
    db.execute(
        "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text) "
        "VALUES (?, '2027-06-20', '2027-06-27', 'day', 'q')",
        (item_id,),
    )
    answer = on(db, registry, "2027-06-10", "2027-06-22")
    assert groups(answer)["dated"] == ["Arts Festival"]
    assert groups(answer)["not confirmed"] == []
    # Only the latest dates are moved: 6-15 June is not projected when 2027 has real dates.
    assert titles(on(db, registry, "2027-06-08", "2027-06-12")) == []
    assert groups(on(db, registry, "2028-06-21", "2028-06-22"))["not confirmed"] == [
        "Arts Festival"
    ]
    # A long window with the real dates of 2027 and the moved dates of 2028: the real dates.
    long = on(db, registry, "2027-06-20", "2028-06-25")
    assert groups(long)["dated"] == ["Arts Festival"] and groups(long)["not confirmed"] == []
    assert long["data"]["groups"][0]["cards"][0]["confirmed"] is True


def test_an_item_below_the_bar_is_in_that_group_only(feed):
    db, registry = feed
    festival(db, below=1)
    whales(db, below=1)
    add(db, "Quiz night", [("2027-06-09", "2027-06-09", "day", None)], below=1)
    answer = on(db, registry, "2027-06-08", "2027-06-12")
    assert groups(answer) == {
        "dated": [],
        "seasons and experiences": [],
        "not confirmed": [],
        "below the traveller bar": ["Arts Festival", "Whale season", "Quiz night"],
    }
    assert "Arts Festival · not confirmed (Last held" in answer["text"]
    assert answer["data"]["counts"]["items"] == 3


def test_an_item_that_is_not_live_is_not_returned(feed):
    db, registry = feed
    whales(db, status="needs review")
    festival(db, status="rejected")
    assert titles(on(db, registry, "2027-06-08", "2027-06-12")) == []
    assert when_to_go(db, registry, "hermanus")["data"]["counts"]["items"] == 0


# Hand case 10: all items and counts. Hand case 12: order.


def test_case_10_eleven_items_give_eleven_cards_and_counts(feed):
    db, registry = feed
    for number in range(2):
        rows = [("2027-06-20", "2027-06-27", "day", None)]
        add(db, f"Festival {number}", rows, category="festival")
    for number in range(9):
        add(db, f"Market {number}", [("2027-06-26", "2027-06-26", "day", None)], category="market")
    answer = on(db, registry, "2027-06-20", "2027-06-27")
    assert len(titles(answer)) == 11
    counts = answer["data"]["counts"]
    assert counts["items"] == 11
    assert counts["categories"] == {"festival": 2, "market": 9}
    assert counts["groups"]["dated"] == 11
    assert "  in the window   11 items: 11 dated · 0 seasons and experiences" in answer["text"]
    assert "  by category     festival 2 · market 9" in answer["text"]
    assert sum(line.startswith("[event") for line in answer["text"].splitlines()) == 11


def test_counts_are_the_cards_of_each_group(feed):
    db, registry = feed
    whales(db)
    festival(db)
    add(db, "Concert", [("2027-06-09", "2027-06-09", "day", None)])
    add(db, "Quiz night", [("2027-06-09", "2027-06-09", "day", None)], below=1)
    counts = on(db, registry, "2027-06-08", "2027-06-12")["data"]["counts"]
    assert counts["items"] == 4
    assert counts["groups"] == dict.fromkeys(GROUPS, 1)


def test_case_12_groups_in_the_fixed_order_then_date_then_title(feed):
    db, registry = feed
    add(db, "bravo", [("2027-06-10", "2027-06-10", "day", None)])
    add(db, "Charlie", [("2027-06-09", "2027-06-09", "day", None)])
    add(db, "Alpha", [("2027-06-10", "2027-06-10", "day", None)])
    add(db, "Zulu run", [("2027-06-01", "2027-06-30", "day", None)])
    whales(db)
    add(db, "Autumn season", season(4, 11), kind="season")
    festival(db)
    add(db, "Quiz night", [("2027-06-09", "2027-06-09", "day", None)], below=1)
    answer = on(db, registry, "2027-06-08", "2027-06-12")
    assert [group["name"] for group in answer["data"]["groups"]] == list(GROUPS)
    assert groups(answer) == {
        "dated": ["Zulu run", "Charlie", "Alpha", "bravo"],
        "seasons and experiences": ["Autumn season", "Whale season"],
        "not confirmed": ["Arts Festival"],
        "below the traveller bar": ["Quiz night"],
    }
    heads = [line for line in answer["text"].splitlines() if line in GROUPS]
    assert heads == list(GROUPS)


# Hand case 6: planning with no dates.


def months(answer: dict) -> dict:
    return {m["name"]: [card["title"] for card in m["cards"]] for m in answer["data"]["months"]}


def test_case_6_when_to_go_april_to_august(feed):
    db, registry = feed
    festival(db)
    whales(db)
    add(db, "One concert", [("2027-06-09", "2027-06-09", "day", None)])
    # held each year in October: not in the months of the question, and not in its counts
    add(db, "Spring fair", [("2026-10-03", "2026-10-03", "day", None)], yearly=1)
    answer = when_to_go(db, registry, "hermanus", 4, 8)
    assert months(answer) == {
        "April": [],
        "May": [],
        "June": ["Whale season", "Arts Festival"],
        "July": ["Whale season"],
        "August": ["Whale season"],
    }
    text = answer["text"]
    assert text.startswith("when_to_go · Hermanus · April - August · as of 2026-11-23\n")
    june = text[text.index("\nJune\n") : text.index("\nJuly\n")]
    assert (
        "[event · festival] Arts Festival · not confirmed "
        "(Last held Sat 6 June 2026 - Mon 15 June 2026) · Hermanus"
    ) in june
    assert f"[season · nature] Whale season · June - November ({SEASON}) · Hermanus" in june
    assert "2027" not in text  # no date of the festival is invented
    assert answer["data"]["counts"] == {
        "items": 2,
        "groups": {"seasons and experiences": 1, "yearly with a date": 0, "not confirmed": 1},
        "categories": {"festival": 1, "nature": 1},
    }
    assert "  in the months   2 items: 1 seasons and experiences" in text


def test_when_to_go_shows_the_real_date_of_a_yearly_item_when_a_page_states_it(feed):
    db, registry = feed
    item_id = festival(db)
    db.execute(
        "INSERT INTO occurrence (item_id, start_date, end_date, precision, time_text) "
        "VALUES (?, '2027-06-24', '2027-07-04', 'day', 'q')",
        (item_id,),
    )
    answer = when_to_go(db, registry, "hermanus")
    assert [m["name"] for m in answer["data"]["months"]] == [
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
    listed = {name: cards for name, cards in months(answer).items() if cards}
    assert listed == {"June": ["Arts Festival"], "July": ["Arts Festival"]}  # each month it covers
    assert (
        "Arts Festival · Thu 24 June 2027 - Sun 4 July 2027 (confirmed; a range" in (answer["text"])
    )
    assert "not confirmed (" not in answer["text"]
    assert "Last held" not in answer["text"]
    assert answer["data"]["counts"]["groups"]["yearly with a date"] == 1


def test_when_to_go_season_over_the_year_end_and_a_range_over_the_year_end(feed):
    db, registry = feed
    add(db, "Summer season", season(11, 4), kind="season")
    listed = months(when_to_go(db, registry, "hermanus"))
    assert [name for name, cards in listed.items() if cards] == [
        "January",
        "February",
        "March",
        "April",
        "November",
        "December",
    ]
    assert list(months(when_to_go(db, registry, "hermanus", 11, 2))) == [
        "November",
        "December",
        "January",
        "February",
    ]
    assert list(months(when_to_go(db, registry, "hermanus", 7))) == ["July"]


def test_when_to_go_refuses_a_month_that_is_not_1_to_12(feed):
    db, registry = feed
    with pytest.raises(ValueError, match="month"):
        when_to_go(db, registry, "hermanus", 0, 5)
    with pytest.raises(ValueError, match="month"):
        when_to_go(db, registry, "hermanus", 4, 13)


# Hand cases 19 and 24: the full card.


def test_case_19_tell_me_more_gives_each_fact_with_its_quote_and_source(feed):
    db, registry = feed
    item_id = add(
        db,
        "Harbour Market",
        [
            ("2027-06-05", "2027-06-05", "day", "weekly"),
            ("2027-06-12", "2027-06-12", "day", "weekly"),
        ],
        category="market",
        venue="Harbour Square",
        price="Entry R75",
        time_text="Every Saturday from 09:00",
    )
    db.execute(
        "INSERT INTO evidence (item_id, field, value, quote, page_id, model) "
        "VALUES (?, 'when', 'weekly saturday', 'Every Saturday from 09:00', 1, 'model-a'), "
        "(?, 'price', 'Entry R75', 'Entry R75', 1, 'model-a')",
        (item_id, item_id),
    )
    db.execute(
        "INSERT INTO change (item_id, field, old_value, new_value, found_at, actor) "
        "VALUES (?, 'price', 'Entry R50', 'Entry R75', '2027-03-01T08:00:00+00:00', 'ingest')",
        (item_id,),
    )
    answer = tell_me_more(db, registry, [item_id])
    assert answer["text"].splitlines()[:19] == [
        "tell_me_more · 1 of 1 id found · as of 2026-11-23",
        "",
        f"id {item_id}",
        "  title     Harbour Market",
        "  kind      event",
        "  category  market",
        (
            '  when      weekly rule: "Every Saturday from 09:00" · 2 dates that code wrote from the '
            "rule, Sat 5 June 2027 to Sat 12 June 2027"
        ),
        "  town      Hermanus",
        "  venue     Harbour Square",
        "  price     Entry R75",
        "  yearly    no",
        "  bar       not below the traveller bar",
        "  source    https://example.org/page",
        "  sources   1 source",
        '  evidence  title: "Harbour Market" (model-a, https://example.org/page)',
        '  evidence  when: "Every Saturday from 09:00" (model-a, https://example.org/page)',
        '  evidence  price: "Entry R75" (model-a, https://example.org/page)',
        "  seen      last_seen_at 2026-11-23 · last_verified 2026-11-23",
        '  changes   2027-03-01: price "Entry R50" -> "Entry R75" (ingest)',
    ]
    card = answer["data"]["cards"][0]
    assert card["evidence"][2] == {
        "field": "price",
        "quote": "Entry R75",
        "model": "model-a",
        "page": "https://example.org/page",
    }
    assert card["changes"][0]["old"] == "Entry R50"


def test_case_24_three_ids_give_three_cards_in_the_order_of_the_ids(feed):
    db, registry = feed
    first = whales(db)
    second = festival(db)
    third = add(db, "Concert", [("2027-06-09", "2027-06-09", "day", None)])
    answer = tell_me_more(db, registry, [third, 999, first, second])
    cards = answer["data"]["cards"]
    assert [card["id"] for card in cards] == [third, 999, first, second]
    assert [card.get("title") for card in cards] == [
        "Concert",
        None,
        "Whale season",
        "Arts Festival",
    ]
    text = answer["text"]
    assert text.startswith("tell_me_more · 3 of 4 ids found · as of 2026-11-23\n")
    assert "\nid 999: not found\n" in text
    assert text.index("Concert") < text.index("id 999") < text.index("Whale season")
    assert text.index("Whale season") < text.index("Arts Festival")
    assert "  when      Wed 9 June 2027 (confirmed)" in text
    assert f"  when      June - November ({SEASON})" in text
    assert "  when      Sat 6 June 2026 - Mon 15 June 2026 (confirmed; a range, each day" in text
    assert "  yearly    yes" in text
    assert "  venue     not stated" in text and "  changes   none" in text


# Hand case 18, holes, and the limits of a read.


def test_case_18_the_same_query_two_times_gives_the_same_data_and_text(feed):
    db, registry = feed
    ids = [whales(db), festival(db)]
    add(db, "Concert", [("2027-06-09", "2027-06-09", "day", None)])
    for call in (
        lambda: on(db, registry, "2027-06-08", "2027-06-12"),
        lambda: when_to_go(db, registry, "hermanus", 4, 8),
        lambda: tell_me_more(db, registry, ids),
    ):
        first, second = call(), call()
        assert first == second
        assert first["text"].encode() == second["text"].encode()
        assert first["data"]["as_of"] == "2026-11-23"
        assert json.dumps(first["data"])  # the data is plain


def test_each_answer_has_the_holes_of_the_registry(feed):
    db, registry = feed
    block = (
        "\nholes\n"
        "  sources         1 source in the registry for Hermanus\n"
        "  not collected   Tickets: the API needs a key (declares 136 events)\n"
        "  not collected   Other tickets: the search needs a browser\n"
    )
    for answer in (
        on(db, registry, "2027-06-08", "2027-06-12"),
        when_to_go(db, registry, "hermanus"),
        tell_me_more(db, registry, [1]),
        what_changed(db, registry, "hermanus", date(2027, 1, 15)),
    ):
        assert answer["text"].endswith(block)
        assert answer["data"]["holes"] == {
            "sources": {"hermanus": 1},
            "not_collected": registry["not_collected"],
        }
    del registry["not_collected"]
    assert on(db, registry, "2027-06-08", "2027-06-12")["text"].endswith("  not collected   none\n")


def test_a_read_writes_nothing(feed):
    db, registry = feed
    ids = [whales(db), festival(db)]
    before = db.total_changes
    on(db, registry, "2027-06-08", "2027-06-12")
    when_to_go(db, registry, "hermanus")
    tell_me_more(db, registry, ids)
    what_changed(db, registry, "hermanus", date(2026, 1, 1))
    assert db.total_changes == before and not db.in_transaction


def test_third_party_text_stays_on_one_line(feed):
    db, registry = feed
    item_id = add(db, "Concert\nholes", [("2027-06-09", "2027-06-09", "day", None)])
    db.execute("UPDATE evidence SET quote = 'Concert\nid 7: not found'")
    texts = [
        on(db, registry, "2027-06-08", "2027-06-12")["text"],
        tell_me_more(db, registry, [item_id])["text"],
    ]
    for text in texts:
        assert "Concert holes" in text
        assert text.splitlines().count("holes") == 1
    assert "id 7: not found" not in texts[1].splitlines()


def test_the_read_code_names_no_place_and_no_source():
    registry = json.loads(Path("registry.json").read_text(encoding="utf-8"))
    names = [*registry["places"], *(row["name"] for row in registry["not_collected"])]
    names += [source["name"] for source in registry["sources"]]
    for path in ("feed/read.py", "feed/mcp_server.py"):
        code = Path(path).read_text(encoding="utf-8").casefold()
        assert [name for name in names if name.casefold() in code] == []


# The change log: first seen and the latest change on each short card; what_changed.


def change(db, item_id, field, old, new, found_at="2027-03-01T08:00:00+00:00"):
    db.execute(
        "INSERT INTO change (item_id, field, old_value, new_value, found_at, actor) "
        "VALUES (?, ?, ?, ?, ?, 'ingest')",
        (item_id, field, old, new, found_at),
    )


def test_a_short_card_gives_first_seen_and_the_latest_change(feed):
    db, registry = feed
    concert = add(db, "Concert", [("2027-06-09", "2027-06-09", "day", None)], price="R75")
    plain = whales(db)
    change(db, concert, "venue", None, "Old Harbour", "2027-01-10T08:00:00+00:00")
    change(db, concert, "price_text", "R50", "R75")
    answer = on(db, registry, "2027-06-08", "2027-06-12")
    lines = answer["text"].splitlines()
    start = lines.index("[event · other] Concert · Wed 9 June 2027 (confirmed) · Hermanus")
    assert lines[start + 1 : start + 4] == [
        f"    price: R75 · 1 source · first seen 2026-11-23 · id {concert}",
        '    changed 2027-03-01: price_text "R50" -> "R75"',
        "    source: https://example.org/page",
    ]
    assert f"    price: not stated · 1 source · first seen 2026-11-23 · id {plain}" in lines
    assert sum(line.startswith("    changed ") for line in lines) == 1
    card = answer["data"]["groups"][0]["cards"][0]
    assert card["first_seen"] == "2026-11-23"
    assert card["changed"] == {
        "field": "price_text",
        "old": "R50",
        "new": "R75",
        "found_at": "2027-03-01",
        "actor": "ingest",
    }
    db.execute("DELETE FROM change WHERE field = 'price_text'")
    text = when_to_go(db, registry, "hermanus")["text"]
    assert "first seen 2026-11-23" in text and "    changed " not in text
    assert (
        '    changed 2027-01-10: venue added "Old Harbour"'
        in (on(db, registry, "2027-06-08", "2027-06-12")["text"])
    )


@pytest.fixture
def moved(feed):
    """Hand case 9: a date moves from 18 to 20 September 2027, found on 1 March 2027."""
    db, registry = feed
    db.execute(
        "INSERT INTO page (id, source_id, url, content_hash, fetched_at, http_status, text) "
        "VALUES (2, 'hand', 'https://example.org/page', 'h2', '2027-03-01T08:00:00+00:00', 200, '')"
    )
    rows = [("2027-09-18", "2027-09-18", "day", None), ("2027-09-20", "2027-09-20", "day", None)]
    item_id = add(db, "Harvest concert", rows)
    change(db, item_id, "when", None, "2027-09-20")
    return db, registry, item_id


def test_case_9_a_moved_date_since_15_january_and_since_5_march(moved):
    db, registry, item_id = moved
    answer = what_changed(db, registry, "hermanus", date(2027, 1, 15))
    assert groups(answer) == {"new": [], "changed": ["Harvest concert"]}
    assert answer["text"].splitlines()[:13] == [
        "what_changed · Hermanus · since 15 January 2027 · as of 2027-03-01",
        "",
        "counts",
        "  since the date  1 item: 0 new · 1 changed",
        "  by category     other 1",
        "",
        "new",
        "    none",
        "",
        "changed",
        (
            "[event · other] Harvest concert · Sat 18 September 2027 (confirmed), "
            "Mon 20 September 2027 (confirmed) · Hermanus"
        ),
        f"    price: not stated · 1 source · first seen 2026-11-23 · id {item_id}",
        '    changed 2027-03-01: when added "2027-09-20"',
    ]
    assert answer["data"]["groups"][1]["cards"][0]["changes"] == [
        {
            "field": "when",
            "old": None,
            "new": "2027-09-20",
            "found_at": "2027-03-01",
            "actor": "ingest",
        }
    ]
    later = what_changed(db, registry, "hermanus", date(2027, 3, 5))
    assert groups(later) == {"new": [], "changed": []}
    assert later["data"]["counts"]["items"] == 0
    assert later["text"].count("\n    none\n") == 2
    # the day of the change is in, the next day is out
    assert titles(what_changed(db, registry, "hermanus", date(2027, 3, 1))) == ["Harvest concert"]
    assert titles(what_changed(db, registry, "hermanus", date(2027, 3, 2))) == []
    assert what_changed(db, registry, "hermanus", date(2027, 1, 15)) == answer  # hand case 18


def test_what_changed_gives_each_change_since_the_date_and_no_older_change(moved):
    db, registry, item_id = moved
    change(db, item_id, "price_text", "R50", "R75", "2027-01-10T08:00:00+00:00")
    change(db, item_id, "venue", "Hall", "Old Harbour", "2027-02-10T08:00:00+00:00")
    text = what_changed(db, registry, "hermanus", date(2027, 1, 15))["text"]
    assert [line for line in text.splitlines() if line.startswith("    changed ")] == [
        '    changed 2027-02-10: venue "Hall" -> "Old Harbour"',
        '    changed 2027-03-01: when added "2027-09-20"',
    ]


def test_a_new_item_is_in_new_and_not_also_in_changed(moved):
    db, registry, item_id = moved
    db.execute("UPDATE item SET first_seen = '2027-02-01T08:00:00+00:00' WHERE id = ?", (item_id,))
    old = whales(db)  # first seen 2026-11-23, no change: in no group
    market = add(db, "Market", [("2027-06-05", "2027-06-05", "day", "weekly")], time_text="Sat")
    db.execute("UPDATE item SET first_seen = '2027-01-20T08:00:00+00:00' WHERE id = ?", (market,))
    add(db, "Set aside", [("2027-06-05", "2027-06-05", "day", None)], status="needs review")
    db.execute("UPDATE item SET first_seen = '2027-02-01' WHERE title = 'Set aside'")
    answer = what_changed(db, registry, "hermanus", date(2027, 1, 15))
    assert groups(answer) == {"new": ["Market", "Harvest concert"], "changed": []}
    assert answer["data"]["counts"]["groups"] == {"new": 2, "changed": 0}
    assert f"id {old}\n" not in answer["text"]
    assert '[event · other] Market · weekly rule: "Sat" · 1 date that code wrote' in answer["text"]
    # the card of a new item still shows its latest change
    assert '    changed 2027-03-01: when added "2027-09-20"' in answer["text"]
    on_the_day = what_changed(db, registry, "hermanus", date(2027, 2, 1))
    assert groups(on_the_day) == {"new": ["Harvest concert"], "changed": []}
    day_after = what_changed(db, registry, "hermanus", date(2027, 2, 2))
    assert groups(day_after) == {"new": [], "changed": ["Harvest concert"]}


def test_what_changed_after_as_of_is_empty(moved):
    db, registry, _ = moved
    answer = what_changed(db, registry, "hermanus", date(2027, 3, 2))
    assert answer["data"]["as_of"] == "2027-03-01"
    assert titles(answer) == [] and answer["text"].count("\n    none\n") == 2


def test_dates_that_are_not_past_are_not_called_last_held(feed):
    """Dates stated for June 2027, and a window in June 2028: nothing was "held" yet."""
    db, registry = feed
    add(db, "Arts Festival", [("2027-06-05", "2027-06-13", "day", None)], yearly=1)
    answer = on(db, registry, "2028-06-06", "2028-06-10")
    card = answer["data"]["groups"][2]["cards"][0]
    assert card["when"] == "Last stated dates Sat 5 June 2027 - Sun 13 June 2027"
    assert "Last held" not in answer["text"] and "not confirmed" in answer["text"]


# Faults that the blind review of the joined code found.


def test_a_year_that_code_wrote_is_never_shown_as_last_stated_or_last_held(feed):
    db, registry = feed
    add(db, "Whale season", season(6, 11), kind="season", yearly=1)
    weekly = [
        ("2027-06-05", "2027-06-05", "day", "weekly"),
        ("2028-05-20", "2028-05-20", "day", "weekly"),
    ]
    add(db, "Yearly market", weekly, yearly=1)
    answer = on(db, registry, "2029-07-01", "2029-07-31")
    assert titles(answer) == []
    assert "Last stated" not in answer["text"] and "Last held" not in answer["text"]
    months = when_to_go(db, registry, "hermanus", 5, 5)
    # its dates from the weekly rule are shown as a rule, never as "last held"
    assert "Last" not in months["text"] and '(weekly rule: "quote of the date")' in months["text"]


def test_a_card_with_a_weekly_date_and_a_range_keeps_the_range_note(feed):
    db, registry = feed
    rows = [
        ("2026-12-12", "2026-12-12", "day", "weekly"),
        ("2026-12-14", "2026-12-20", "day", None),
    ]
    add(db, "Night market", rows, time_text="Every Saturday")
    text = on(db, registry, "2026-12-10", "2026-12-21")["text"]
    assert '(weekly rule: "Every Saturday"; a range, each day is not stated)' in text


def test_as_of_is_the_last_time_that_an_item_was_seen(feed):
    db, registry = feed
    festival(db)
    db.execute("UPDATE item SET last_seen_at = '2027-05-24T12:00:00+00:00'")
    assert on(db, registry, "2027-06-08", "2027-06-12")["data"]["as_of"] == "2027-05-24"


def test_when_to_go_does_not_call_a_past_rule_date_last_held(feed):
    db, registry = feed
    add(db, "Old market", [("2026-06-06", "2026-06-06", "day", "weekly")], yearly=1)
    text = when_to_go(db, registry, "hermanus", 6, 6)["text"]
    assert "Old market" not in text and "Last" not in text
