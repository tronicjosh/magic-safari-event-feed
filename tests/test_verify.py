"""The code checks of step 4 (verify). No model is used here.

Pages are short extracts of the real saved pages in evals/pages/ (2026-11-23).
"""

from feed.verify import check_when, quote_on_page, value_in_quote, verify_item

MONTHLY_PDF = """[page 1]
Tourism November
Events 2026
Events November Dates Time Venue Town
Bring & Braai 18 17:30 Hangklip Hotel Pringle Bay
Ceramic Exhibition Rooted from Earth to Art 14 - 22 10:00 - 16:00 Harold Porter Betty’s Bay
Bingo Night 18 19:00 Pearly Beach Hengel Klub Gansbaai
* Saturdays: ParkRun at 8:00; Markets from 9:00
"""

KALFIEFEES = "Kalfiefees\nHermanus\nKunstefees\n2026\n5-10\nAUGUSTUS\n2026\nSien Feesgids (PDF)"


def part(day=0, month=0, year=0):
    return {"day": day, "month": month, "year": year}


def when(kind, quotes, start=None, end=None, weekday=""):
    return {
        "kind": kind,
        "start": start or part(),
        "end": end or part(),
        "weekday": weekday,
        "quotes": quotes,
    }


# --- check 1: the quote is on the page ---------------------------------------------------


def test_quote_on_page_exact():
    assert quote_on_page("Bring & Braai 18 17:30", MONTHLY_PDF) == "exact"


def test_quote_across_line_breaks_passes_as_whitespace():
    assert quote_on_page("5-10 AUGUSTUS 2026", KALFIEFEES) == "whitespace"


def test_quote_with_straight_apostrophe_passes_as_punctuation():
    assert quote_on_page("Harold Porter Betty's Bay", MONTHLY_PDF) == "punctuation"


def test_invented_quote_fails():  # hand case 8
    assert quote_on_page("Bring & Braai 19 17:30", MONTHLY_PDF) is None


def test_empty_quote_fails():
    assert quote_on_page("  ", MONTHLY_PDF) is None


def test_quote_is_case_sensitive():
    assert quote_on_page("bring & braai", MONTHLY_PDF) is None


# --- check 2: the value is in the quote ---------------------------------------------------


def test_value_in_quote():
    assert value_in_quote("Pringle Bay", "Bring & Braai 18 17:30 Hangklip Hotel Pringle Bay")
    assert not value_in_quote("Hermanus", "Bring & Braai 18 17:30 Hangklip Hotel Pringle Bay")


def test_price_wrong_value_fails():  # hand case 7: the page says R75, the model says 750
    item = {"title": {"value": "Market", "quote": "Market"}, "when": []}
    page = "Market\nEntry R75"
    good = verify_item({**item, "price": {"value": "R75", "quote": "Entry R75"}}, page)
    bad = verify_item({**item, "price": {"value": "R750", "quote": "Entry R75"}}, page)
    assert [r["ok"] for r in good if r["field"] == "price"] == [True]
    assert [r["ok"] for r in bad if r["field"] == "price"] == [False]


# --- the date check ----------------------------------------------------------------------


def test_day_in_row_month_and_year_in_headers():
    w = when(
        "date",
        ["Bring & Braai 18 17:30 Hangklip Hotel Pringle Bay", "Tourism November", "Events 2026"],
        start=part(18, 11, 2026),
    )
    assert check_when(w) == []


def test_day_that_is_only_a_time_fails():
    # "18" is in the quote only as the hour of 18:00, not as a day.
    w = when("date", ["Dinner 19 18:00 La Trattoria", "November", "2026"], start=part(18, 11, 2026))
    assert check_when(w) == ["start day 18 not in quotes"]


def test_wrong_month_fails():
    w = when("date", ["Bring & Braai 18 17:30", "Events 2026"], start=part(18, 11, 2026))
    assert check_when(w) == ["start month 11 not in quotes"]


def test_missing_year_fails_shape():
    w = when("date", ["Bring & Braai 18 17:30", "Tourism November"], start=part(18, 11, 0))
    assert check_when(w) == ["shape: date needs day, month and year"]


def test_range_with_one_month_and_afrikaans_month_name():
    w = when("range", ["5-10 AUGUSTUS 2026"], start=part(5, 8, 2026), end=part(10, 8, 2026))
    assert check_when(w) == []


def test_range_end_before_start_fails_shape():
    w = when("range", ["5-10 AUGUSTUS 2026"], start=part(10, 8, 2026), end=part(5, 8, 2026))
    assert check_when(w) == ["shape: end is before start"]


def test_numeric_date():
    w = when("date", ["Fri, 04/12/2026, 18H00 - 21H00"], start=part(4, 12, 2026))
    assert check_when(w) == []
    wrong = when("date", ["Fri, 04/12/2026, 18H00 - 21H00"], start=part(12, 4, 2026))
    assert check_when(wrong) != []


def test_abbreviated_month_and_ordinal_day():
    w = when("date", ["Wednesday 18th November 2026"], start=part(18, 11, 2026))
    assert check_when(w) == []
    w = when("range", ["5 - 8 March", "EVENTS 2026"], start=part(5, 3, 2026), end=part(8, 3, 2026))
    assert check_when(w) == []
    w = when("date", ["5 Sept Race 2 the Sea 2026"], start=part(5, 9, 2026))
    assert check_when(w) == []


def test_impossible_date_fails_shape():
    w = when("date", ["31 November 2026"], start=part(31, 11, 2026))
    assert check_when(w) == ["shape: start is not a real date"]


def test_season_in_words():
    w = when("months", ["June to end November"], start=part(month=6), end=part(month=11))
    assert check_when(w) == []
    wrong = when("months", ["June to end November"], start=part(month=6), end=part(month=12))
    assert check_when(wrong) == ["end month 12 not in quotes"]


def test_weekly_in_words():
    w = when("weekly", ["* Saturdays: ParkRun at 8:00"], weekday="saturday")
    assert check_when(w) == []
    wrong = when("weekly", ["* Saturdays: ParkRun at 8:00"], weekday="sunday")
    assert check_when(wrong) == ["weekday sunday not in quotes"]


# --- one item, all checks ----------------------------------------------------------------


def test_verify_item_real_row():
    item = {
        "title": {"value": "Bring & Braai", "quote": "Bring & Braai 18 17:30 Hangklip Hotel"},
        "town": {"value": "Pringle Bay", "quote": "Hangklip Hotel Pringle Bay"},
        "venue": {"value": "", "quote": ""},
        "price": {"value": "", "quote": ""},
        "when": [
            when(
                "date",
                ["Bring & Braai 18 17:30", "Tourism November", "Events 2026"],
                start=part(18, 11, 2026),
            )
        ],
    }
    results = verify_item(item, MONTHLY_PDF)
    assert {r["field"] for r in results} == {"title", "town", "when[0]"}  # empty fields: no row
    assert all(r["ok"] for r in results)


def test_verify_item_date_quote_not_on_page_fails():
    item = {
        "title": {"value": "Bring & Braai", "quote": "Bring & Braai"},
        "when": [when("date", ["Bring & Braai 18 November 2026"], start=part(18, 11, 2026))],
    }
    results = {r["field"]: r for r in verify_item(item, MONTHLY_PDF)}
    assert results["title"]["ok"]
    assert not results["when[0]"]["ok"]
    assert "quote not on page" in results["when[0]"]["reason"]


def test_verify_item_with_no_date_reports_it():
    item = {"title": {"value": "Bingo Night", "quote": "Bingo Night"}, "when": []}
    results = {r["field"]: r for r in verify_item(item, MONTHLY_PDF)}
    assert not results["when"]["ok"]


# --- faults found by the blind review (2026-11-23): a false value must not pass ----------


def test_quote_must_not_start_or_end_inside_a_number_or_word():
    assert quote_on_page("8 17:30 Hangklip Hotel Pringle Bay", MONTHLY_PDF) is None  # page: 18
    assert quote_on_page("Entry R75", "Entry R750") is None
    assert quote_on_page("Bring & Bra", MONTHLY_PDF) is None
    assert quote_on_page("Entry R75", "Entry R75.") == "exact"


def test_superscript_is_not_a_digit():
    assert quote_on_page("Entry R751", "Entry R75¹") is None
    assert quote_on_page("12 November 2026", "1² November 2026") is None


def price_ok(value, quote):
    item = {"title": {"value": "Market", "quote": "Market"}, "when": []}
    results = verify_item({**item, "price": {"value": value, "quote": quote}}, "Market\n" + quote)
    return [r["ok"] for r in results if r["field"] == "price"] == [True]


def test_price_numbers_are_not_joined_or_cut():
    assert not price_ok("R1817", "Bring & Braai 18 17:30")
    assert not price_ok("R50", "Entry R75.50")
    assert price_ok("R1500", "Adults R1 500 per person")
    assert price_ok("R1500", "Adults R1,500 per person")
    assert price_ok("R75", "Entry R75.00")


def test_words_that_are_not_months_or_weekdays():
    w = when("months", ["Whales may be seen from June to November"], part(month=5), part(month=11))
    assert check_when(w) == ["start month 5 not in quotes"]
    w = when("months", ["May to November"], part(month=5), part(month=11))
    assert check_when(w) == []
    assert check_when(when("weekly", ["We sat on the terrace"], weekday="saturday")) != []
    assert check_when(when("weekly", ["Sat & Sun from 9:00"], weekday="saturday")) == []


def test_numbers_that_are_not_days():
    for text in ["18.30", "8pm", "18 uur", "18h", "18 :00", "R18", "+18 82", "18km", "[page 18]"]:
        day = 8 if text == "8pm" else 18
        w = when("date", [text, "November 2026"], start=part(day, 11, 2026))
        assert check_when(w) == [f"start day {day} not in quotes"], text
    w = when("date", ["18 November", "R2027"], start=part(18, 11, 2027))
    assert check_when(w) == ["start year 2027 not in quotes"]


def test_days_in_normal_forms_still_pass():
    for text in ["19 -22", "7 & 8 Aug", "18th", "(18)", "18,", "on the 18."]:
        w = when("date", [text, "November 2026"], start=part(18 if "18" in text else 19, 11, 2026))
        w["start"]["day"] = 8 if text == "7 & 8 Aug" else w["start"]["day"]
        assert check_when(w) == [], text


def test_parts_that_the_kind_does_not_use_must_be_zero():
    w = when("weekly", ["Saturdays"], part(5, 3, 2031), part(9, 9, 2035), weekday="saturday")
    assert check_when(w) == ["shape: weekly must have no start and no end"]
    w = when("date", ["18 November 2026"], part(18, 11, 2026), part(31, 2, 1999))
    assert check_when(w) == ["shape: date must have no end"]
    w = when("months", ["June to November"], part(3, 6, 0), part(month=11))
    assert check_when(w) == ["shape: months must have no days"]


def test_malformed_entries_fail_and_do_not_crash():
    page = "Market\nEntry R75"
    bad_items = [
        {"title": {"value": "Market", "quote": "Market"}, "price": {"value": 75, "quote": None}},
        {"title": "Market", "when": {"kind": "date"}},
        {"title": {"value": "Market"}, "when": [{"kind": "date"}]},
        {"title": {"value": "Market", "quote": "Market"}, "when": [None]},
        {
            "title": {"value": "Market", "quote": "Market"},
            "when": [when("date", ["Market"], start=part(1, 1, 10**12))],
        },
        {
            "title": {"value": "Market", "quote": "Market"},
            "when": [when("months", [None], part(month=None), part(month=6))],
        },
    ]
    for item in bad_items:
        results = verify_item(item, page)
        assert any(not r["ok"] for r in results), item
