"""The MCP server over stdio, started by the `mcp` client on a temporary database."""

import json
import os
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
