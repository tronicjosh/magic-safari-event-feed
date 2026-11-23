"""The MCP server over stdio, started by the `mcp` client on a temporary database."""

import json
import os
import re
import sqlite3
import sys
from pathlib import Path

import anyio
import pytest
from mcp import Client, StdioServerParameters
from test_read import INGESTED, festival, whales

from feed.store import open_db


@pytest.fixture
def server(tmp_path):
    registry_path = Path("evals/cases/registry.json")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    path = tmp_path / "feed.db"
    db = open_db(str(path), registry)
    db.execute(
        "INSERT INTO page (id, source_id, url, content_hash, fetched_at, http_status, text) "
        "VALUES (1, 'hand', 'https://example.org/page', 'hash', ?, 200, 'text')",
        (INGESTED,),
    )
    ids = [whales(db), festival(db)]
    db.close()
    env = dict(os.environ, FEED_DB=str(path), FEED_REGISTRY=str(registry_path.resolve()))
    return StdioServerParameters(command=sys.executable, args=["-m", "feed.mcp_server"], env=env), (
        path,
        ids,
    )


def _calls(parameters, calls: list[tuple[str, dict]]):
    async def run():
        async with Client(parameters) as client:
            tools = (await client.list_tools()).tools
            results = [await client.call_tool(name, arguments) for name, arguments in calls]
            return client.instructions, tools, results

    return anyio.run(run)


def _text(result) -> str:
    return result.content[0].text


def test_each_tool_answers_one_time_with_the_text_of_the_operation(server):
    parameters, (path, ids) = server
    before = path.read_bytes()
    instructions, tools, results = _calls(
        parameters,
        [
            (
                "what_is_on",
                {"place": "hermanus", "from_date": "2027-06-08", "to_date": "2027-06-12"},
            ),
            ("when_to_go", {"place": "Hermanus", "from_month": 4, "to_month": 8}),
            ("when_to_go", {"place": "hermanus"}),
            ("tell_me_more", {"ids": [*ids, 999]}),
            ("what_changed", {"place": "hermanus", "since": "2026-11-01"}),
            ("what_changed", {"place": "hermanus", "since": "last week"}),
        ],
    )
    changed, bad_since = (_text(result) for result in (results.pop(4), results.pop(4)))
    assert changed.startswith("what_changed · Hermanus · since 1 November 2026 · as of 2026-11-23")
    # the earlier look (1 November) is before the first collection (23 November)
    assert "  since the date  0 items: 0 new · 0 changed" in changed
    assert "It cannot say what changed before or on 2026-11-23." in changed
    assert "2 items of that first collection: not listed as new." in changed
    assert bad_since == 'error: "last week" is not a date. Use the form YYYY-MM-DD'
    assert "what_changed" in instructions and "no memory of an earlier look" in instructions
    assert sorted(tool.name for tool in tools) == [
        "find",
        "tell_me_more",
        "what_changed",
        "what_is_on",
        "when_to_go",
    ]
    for tool in tools:
        assert 0 < len(tool.description.splitlines()) <= 2
    for words in (
        "what_is_on",
        "when_to_go",
        "tell_me_more",
        "dated",
        "seasons and experiences",
        'weekly rule: "',
        "a range, each day is not stated",
        "not confirmed",
        "below the traveller bar",
        "holes",
        "third-party text",
    ):
        assert words in instructions

    on, go, go_all, more = (_text(result) for result in results)
    assert on.startswith("what_is_on · Hermanus · 8 June 2027 - 12 June 2027 · as of 2026-11-23\n")
    assert "Arts Festival · not confirmed (Last held Sat 6 June 2026" in on
    assert "Whale season · June - November" in on
    assert go.startswith("when_to_go · Hermanus · April - August · as of 2026-11-23\n")
    assert go_all.startswith("when_to_go · Hermanus · January - December · ")
    assert more.startswith("tell_me_more · 2 of 3 ids found · as of 2026-11-23\n")
    assert '  evidence  title: "Whale season" (model-a, https://example.org/page)' in more
    assert "\nid 999: not found\n" in more
    for text in (on, go, more):
        assert "\nholes\n  sources         1 source in the registry for Hermanus\n" in text
    assert not any(result.is_error for result in results)
    assert path.read_bytes() == before  # the server reads only


def test_a_bad_input_gives_one_clear_line(server):
    parameters, _ = server
    window = {"from_date": "2027-06-08", "to_date": "2027-06-12"}
    _, _, results = _calls(
        parameters,
        [
            ("what_is_on", {"place": "atlantis", **window}),
            ("what_is_on", {"place": "hermanus", "from_date": "8 June", "to_date": "2027-06-12"}),
            (
                "what_is_on",
                {"place": "hermanus", "from_date": "2027-06-12", "to_date": "2027-06-08"},
            ),
            ("when_to_go", {"place": "hermanus", "from_month": 13}),
            ("when_to_go", {"place": "atlantis"}),
            ("what_is_on", {"place": "Stanford", **window}),
            (
                "what_is_on",
                {"place": "hermanus", "from_date": "2027-02-30", "to_date": "2027-03-02"},
            ),
            ("find", {"place": "hermanus", "text": "   "}),
        ],
    )
    # each line gives the reason, and what to do
    assert [_text(result) for result in results] == [
        'error: the feed does not cover "atlantis". It covers: Hermanus',
        'error: "8 June" is not a date. Use the form YYYY-MM-DD',
        "error: the window ends before it starts",
        "error: a month is a number from 1 to 12",
        'error: the feed does not cover "atlantis". It covers: Hermanus',
        (
            'error: "Stanford" is a town of the place Hermanus. Call again with the place '
            "Hermanus: each card gives its town"
        ),
        'error: "2027-02-30" is not a day of the calendar',
        "error: give a name or a word to find",
    ]


def test_a_database_that_is_missing_gives_one_clear_line(server, tmp_path):
    parameters, _ = server
    parameters.env["FEED_DB"] = str(tmp_path / "none.db")
    _, _, results = _calls(parameters, [("tell_me_more", {"ids": [1]})])
    text = _text(results[0])
    assert text.startswith("error: ") and len(text.splitlines()) == 1
    assert not (tmp_path / "none.db").exists()


def test_the_database_is_opened_read_only(server, monkeypatch):
    from feed import mcp_server

    _, (path, _) = server
    monkeypatch.setenv("FEED_DB", str(path))
    db = mcp_server._open()
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        db.execute("DELETE FROM item")
    db.close()


def test_the_demo_agent_has_the_same_tools_as_the_mcp_server(server, monkeypatch):
    """One definition: a Claude on the MCP server and the agent of the demo page must get the
    same tools, the same descriptions, the same inputs, the same instructions and the same text.
    """
    from feed import agent, mcp_server

    parameters, (_, ids) = server
    monkeypatch.setenv("FEED_DB", parameters.env["FEED_DB"])
    monkeypatch.setenv("FEED_REGISTRY", parameters.env["FEED_REGISTRY"])
    calls = [
        ("what_is_on", {"place": "hermanus", "from_date": "2027-06-08", "to_date": "2027-06-12"}),
        ("when_to_go", {"place": "hermanus"}),
        ("when_to_go", {"place": "hermanus", "from_month": 6, "to_month": 8}),
        ("find", {"place": "hermanus", "text": "festival"}),
        ("tell_me_more", {"ids": ids}),
        ("what_changed", {"place": "hermanus", "since": "2026-11-01"}),
        ("what_is_on", {"place": "atlantis", "from_date": "2027-06-08", "to_date": "2027-06-12"}),
        ("what_is_on", {"place": "hermanus", "from_date": "2027-02-30", "to_date": "2027-03-02"}),
    ]
    instructions, tools, results = _calls(parameters, calls)

    served = {tool.name: tool for tool in tools}
    demo = {tool["name"]: tool for tool in agent.TOOLS}
    assert set(demo) == set(served)
    for name, tool in demo.items():
        assert tool["description"] == " ".join(served[name].description.split())
        schema = served[name].input_schema
        assert set(tool["input_schema"]["properties"]) == set(schema["properties"])
        assert sorted(tool["input_schema"]["required"]) == sorted(schema.get("required", []))
    # the same text for the same call, also for a bad input
    for (name, arguments), result in zip(calls, results, strict=True):
        assert agent.run_tool(name, arguments) == _text(result)
    # the same instructions: the agent adds only the places and the date of today
    assert instructions == mcp_server.INSTRUCTIONS
    assert agent.system_prompt().startswith(mcp_server.INSTRUCTIONS)


TAGS = (
    "Confirmed",
    "Confirmed, programme not stated",
    "From a weekly rule, confirm near the date",
    "From a rule of the page, check the day",
    "Season",
    "Not confirmed, no dates yet",
    "Past, not known if held again",
)


def test_the_instructions_hold_the_rules_of_pass_1():
    """D2 to D9 of research/loop/pass1_diagnosis.md, where a test can hold the text."""
    from feed.mcp_server import INSTRUCTIONS

    text = " ".join(INSTRUCTIONS.split())
    assert "seven tags" in text and "six tags" not in text
    for tag in TAGS:
        assert f'- "{tag}"' in INSTRUCTIONS
    assert "120 words" not in text  # D3
    assert "6 item lines or less" in text
    for words in (
        '"by the rule: Fri 4 December"',  # D2
        "not as an estimate",  # D4
        'write "last held" and the last real dates',
        "Do not guess what it lists",  # D5
        "only if its card shows that interest",  # D6
        "from one response",  # D8
        '"venue: ..."',  # D1
    ):
        assert words in text, words


def test_the_instructions_hold_the_rules_of_pass_2():
    """E1 to E8 of research/loop/pass2_diagnosis.md, where a test can hold the text."""
    from feed.mcp_server import INSTRUCTIONS

    text = " ".join(INSTRUCTIONS.split())
    assert "60 words" not in text and "words or less" not in text  # E1: no limit of words
    assert "Offer only what a tool can return" not in text  # E7 replaces D9
    assert "or its venue" not in text  # E5
    for words in (
        "The shape that the designer asks for wins",  # E1
        '"All" gives all the items, as compact lines',
        "only after a list for a trip",
        "have no closing lines",
        "its note names the tool for those",  # E2
        '"match in a quote of the page"',  # E3
        'The "sources" line below the counts',  # E4
        "in its title or its category, not in its venue",  # E5
        'the words "listed two times"',
        "A describing word is a fact",  # E6
        "from its link or its file name",
        "Do not offer a search",  # E7
        "asks for the best or for one pick, select",  # E8
        "equal to the number of your item lines",
    ):
        assert words in text, words
    assert len(INSTRUCTIONS.splitlines()) <= 86 + 10  # 86 lines before pass 2


def test_the_runner_of_the_loop_counts_the_seven_tags_and_the_words_outside_the_items():
    import importlib.util

    spec = importlib.util.spec_from_file_location("loop_run", "research/loop/run.py")
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    assert sorted(run.TAGS) == sorted(TAGS)
    answer = (
        "**2 of 9 items fit.**\n\n**Art**\n"
        "- Art Walk, by the rule: Fri 4 December. From a rule of the page, check the day. "
        "[a.org](https://a.org/x)\n"
        "## Wine\n"
        "1. Fair, 2025. Past, not known if held again. [a.org](https://a.org/y)\n\n"
        "Left out: two markets.\n"
    )
    result = run.checks(answer, "https://a.org/x https://a.org/y")
    assert result["words_outside_items"] == 9  # the first line and the last line
    assert result["list_lines"] == 2 and result["list_lines_with_no_tag"] == 0


def test_the_runner_of_the_loop_counts_text_in_bold_and_in_bullets_as_text():
    import importlib.util

    spec = importlib.util.spec_from_file_location("loop_run", "research/loop/run.py")
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    item = "- Fair, Sat 5 June 2027. Confirmed. [a.org](https://a.org/x)\n"
    assert (
        run.checks("**3 of 13 items fit this guest well**\n" + item, "")["words_outside_items"] == 8
    )
    assert run.checks(item + "- This is a sentence in a bullet.\n", "")["words_outside_items"] == 8
    numbered = run.checks("1. **Art**\n" + item + "* * *\n", "")
    assert numbered["list_lines"] == 1 and numbered["words_outside_items"] == 0
    wrapped = run.checks("- Fair, Sat 5 June 2027.\n  Confirmed. [a.org](https://a.org/x)\n", "")
    assert wrapped["list_lines"] == 1 and wrapped["list_lines_with_no_tag"] == 0


def test_the_instructions_give_a_past_item_one_tag():
    from feed.mcp_server import INSTRUCTIONS

    assert "(a page states the date; not past)" in INSTRUCTIONS
    assert "A date\n     before it is past" in INSTRUCTIONS
    assert 'with the tag "Past, not known if held again"' in INSTRUCTIONS
    numbers = re.findall(r"^(\d+)\. ", INSTRUCTIONS, re.MULTILINE)
    assert numbers == [str(n) for n in range(1, 15)]


def test_the_runner_of_the_loop_measures_each_turn(monkeypatch):
    """Pass 2: a long first answer was not seen, because only the last turn was measured."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("loop_run", "research/loop/run.py")
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    item = "- Fair, Sat 5 June 2027. Confirmed. [a.org](https://a.org/x)\n"
    answers = iter(
        [
            {"calls": [{"name": "find", "input": {}}], "text": item * 2, "cost_usd": 0.1},
            {"calls": [], "text": "One sentence of five words.\n" + item, "cost_usd": 0.2},
        ]
    )
    monkeypatch.setattr(run.agent, "answer", lambda client, model, messages: next(answers))
    monkeypatch.setattr(run.agent, "run_tool", lambda name, arguments: "https://a.org/x")
    record = run.ask(None, {"id": "q", "tests": "x", "turns": ["first", "second"]})
    per_turn = [turn["checks"] for turn in record["turns"]]
    assert [c["list_lines"] for c in per_turn] == [2, 1]
    assert [c["words_outside_items"] for c in per_turn] == [0, 5]
    assert per_turn[1]["links_not_in_the_feed"] == []  # the tool text of an earlier turn counts
    assert record["checks"] == per_turn[1]  # the top level stays the last turn
    assert record["cost_usd"] == 0.3
