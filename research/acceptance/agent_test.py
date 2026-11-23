"""Acceptance A7 and A8: a new Claude with only the four tools of the feed answers 7 questions.

Run:      ./.venv/Scripts/python research/acceptance/agent_test.py [name]
          It costs money: about 0.4 US dollars for the 7 answers.
Re-check: ./.venv/Scripts/python research/acceptance/agent_test.py [name] --recheck
          It applies the checks to the saved answers of <name>.md. No model call.

The agent is feed/agent.py: the same tools, tool descriptions and server instructions as the
MCP server, and no other prompt. Code checks each answer against the text that the tools
returned, and against the shape that Joshua agreed (research/acceptance/expected.md).
The transcript and the checks go to research/acceptance/<name>.md (default: agent_test).
Joshua's judgment of the answers is the last check; this file is the evidence for it.
"""

import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

import anthropic

from feed import agent, read
from feed.env import load_env

MODEL = "claude-opus-5-5"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
WORDS = 150  # the agreed aim is 120 words; this is the limit of the check
TAGS = r"Confirmed|weekly rule|rule of the page|Season|Not confirmed"

# (conversation, question, the tool that must be among the calls or None, the checks that apply)
QUESTIONS = [
    ("trip", "What is on in Hermanus for my clients from 20 to 27 June 2027?", "what_is_on", "count tags gaps sources"),
    ("trip", "The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?", None, "count tags sources"),
    ("trip", "The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?", None, "count tags sources"),
    ("nodates", "My clients have no dates yet. When is the best time to go to Hermanus?", "when_to_go", "tags gaps sources"),
    ("proof", "Tell me more about the FynArts Festival in June 2027. How sure is the date?", "tell_me_more", "proof sources"),
    ("changed", "I last looked on 1 November 2026. What changed in Hermanus?", "what_changed", ""),
    ("whale", "Is the Hermanus Whale Festival on in October 2027?", None, "tags notconfirmed sources"),
]  # fmt: skip


def dates_in(text: str) -> set[str]:
    """Each "day month" of a text, also from an ISO date (2026-11-23 is 23 November)."""
    names = MONTHS.split("|")
    words = re.findall(rf"\b(\d{{1,2}})(?:st|nd|rd|th)? ({MONTHS})\b", text)
    iso = re.findall(r"\b\d{4}-(\d{2})-(\d{2})\b", text)
    return {f"{int(day)} {month}" for day, month in words} | {
        f"{int(day)} {names[int(month) - 1]}" for month, day in iso if 1 <= int(month) <= 12
    }


def hosts_in(text: str) -> set[str]:
    """Each site name of a text, from a full link or a short name."""
    found = re.findall(r"\b((?:[\w-]+\.)+(?:co\.za|gov\.za|org\.za|com|info|org|net))\b", text)
    return {host.lower().removeprefix("www.") for host in found}


def quotes_in(text: str) -> list[str]:
    """Each quoted span of 3 words or more: a quote of a page, not a word in quote marks."""
    spans = re.findall(r'[“"]([^”"\n]{8,})[”"]', text)
    return [span for span in spans if len(span.split()) >= 3]


def check(text: str, names: list[str], tool, checks: str, seen: str, total: int) -> dict:
    verdicts = {}
    if tool:
        verdicts[f"calls {tool}"] = tool in names
    verdicts["each site is from the feed"] = not (hosts_in(text) - hosts_in(seen))
    verdicts["each date is from the feed or the question"] = not (dates_in(text) - dates_in(seen))
    verdicts[f"{WORDS} words or less"] = len(text.split()) <= WORDS
    limit = 2 if "proof" in checks else 0
    verdicts[f"quotes of a page: {limit} or less"] = len(quotes_in(text)) <= limit
    if "sources" in checks:
        verdicts["names a source"] = bool(hosts_in(text))
    if "count" in checks:
        said = re.search(rf"\b\d+ of {total}\b|\b{total}\b", text[:300])
        verdicts[f"starts with how many of {total}"] = bool(said)
    if "tags" in checks:
        verdicts["gives a tag for how sure"] = bool(re.search(TAGS, text))
    if "gaps" in checks:
        verdicts["names what the feed does not cover"] = bool(re.search(r"Quicket", text))
    if "notconfirmed" in checks:
        verdicts["says not confirmed"] = bool(re.search(r"not confirmed", text, re.IGNORECASE))
        # a day in October 2027 that is not an edge of the window that the agent asked for
        days = re.findall(r"\b(\d{1,2})(?:\s*[-–]\s*\d{1,2})?\s+October\s+2027", text)
        verdicts["gives no day in October 2027"] = not (set(days) - {"1", "31"})
    return verdicts


def saved(path: Path) -> list[dict]:
    """The answers of an earlier run, from its transcript: the calls, the text and the cost."""
    document = path.read_text(encoding="utf-8")
    costs = re.findall(r"\| (\d+\.\d{4}) \|\n", document)
    answers = []
    for number, body in enumerate(document.split("\n## Question ")[1:]):
        chunks = body.split("\n\n", 4)
        calls = [
            {"name": name, "input": json.loads(arguments)}
            for name, arguments in re.findall(r"`(\w+)\((\{.*?\})\)`", chunks[2])
        ]
        answers.append(
            {"text": chunks[4].strip(), "calls": calls, "cost_usd": float(costs[number])}
        )
    return answers


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    arguments = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
    out = Path("research/acceptance", (arguments[0] if arguments else "agent_test") + ".md")
    old = saved(out) if "--recheck" in sys.argv else None
    registry = json.loads(Path("registry.json").read_text(encoding="utf-8"))
    db = sqlite3.connect(f"{Path('feed.db').resolve().as_uri()}?mode=ro", uri=True)
    window = read.what_is_on(db, registry, "hermanus", date(2027, 6, 20), date(2027, 6, 27))["data"]
    total = window["counts"]["items"]
    titles = [card["title"] for group in window["groups"] for card in group["cards"]]
    if old is None:
        load_env()
        client = anthropic.Anthropic()

    sessions: dict[str, list] = {}
    seen: dict[str, str] = {}  # for each conversation: the questions and the text of the tools
    picks, rows, parts, cost = {}, [], [], 0.0
    for number, (session, question, tool, checks) in enumerate(QUESTIONS, start=1):
        if old is None:
            history = sessions.setdefault(session, [])
            history.append({"role": "user", "content": question})
            result = agent.answer(client, MODEL, history)
        else:
            result = old[number - 1]
        cost += result["cost_usd"]
        outputs = "\n".join(agent.run_tool(call["name"], call["input"]) for call in result["calls"])
        seen[session] = seen.get(session, "") + "\n" + question + "\n" + outputs
        text, names = result["text"], [call["name"] for call in result["calls"]]
        verdicts = check(text, names, tool, checks, seen[session], total)
        picks[number] = {title for title in titles if title.lower() in text.lower()}

        failed = [name for name, ok in verdicts.items() if not ok]
        size = f"{len(text.split())} words, {len(quotes_in(text))} quotes"
        rows.append(
            f"| {number} | {question[:60]} | {', '.join(names) or 'none'} | {size} "
            f"| {'PASS' if not failed else 'FAIL'} | {'; '.join(failed)} | {result['cost_usd']:.4f} |"
        )
        calls = ", ".join(f"`{c['name']}({json.dumps(c['input'])})`" for c in result["calls"])
        marks = "; ".join(f"{name}: {'pass' if ok else 'FAIL'}" for name, ok in verdicts.items())
        parts += [
            f"## Question {number}",
            "",
            f"> {question}",
            "",
            f"Tools called: {calls or 'none'}",
            "",
        ]
        parts += [f"Checks: {marks}", "", text, ""]
        state = "PASS" if not failed else "FAIL"
        print(f"Q{number} {state} {size} calls={names} cost={result['cost_usd']:.4f} {failed}")

    differ = picks[2] != picks[3]
    print(
        f"guest 2: {sorted(picks[2])}\nguest 3: {sorted(picks[3])}\ndiffer: {differ}\ncost: {cost:.6f}"
    )
    head = [
        "# Agent test: a new Claude with only the four tools of the feed",
        "",
        f"Written by `research/acceptance/agent_test.py` on {date.today().isoformat()}. Model: `{MODEL}`.",
        "The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.",
        "Questions 1 to 3 are one conversation. Each other question is a new conversation.",
        "Code made the checks below against the text that the tools returned and against the agreed shape (`expected.md`).",
        "",
        "| # | Question | Tools called | Size | Checks by code | What failed | Cost (USD) |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"- The selections for guest 2 and guest 3 differ: **{'yes' if differ else 'NO'}**.",
        f"  - Guest 2 (wine and art, no crowds): {', '.join(sorted(picks[2])) or 'none named'}",
        f"  - Guest 3 (family, children 8 and 11): {', '.join(sorted(picks[3])) or 'none named'}",
        f"- Measured cost of the 7 answers: {cost:.6f} US dollars.",
        "",
    ]
    out.write_text("\n".join(head + parts) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
