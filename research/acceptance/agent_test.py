"""Acceptance A7 and A8: a new Claude with only the four tools of the feed answers 7 questions.

Run: ./.venv/Scripts/python research/acceptance/agent_test.py     (costs money: about 0.5 US dollars)
The agent is feed/agent.py: the same tools, tool descriptions and server instructions as the
MCP server, and no other prompt. Code checks each answer against the text that the tools
returned. The transcript and the checks go to research/acceptance/agent_test.md.
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

OUT = Path("research/acceptance/agent_test.md")
MODEL = "claude-opus-5-5"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

# (session, question, the tool that must be among the calls or None, the checks that apply)
QUESTIONS = [
    ("trip", "What is on in Hermanus for my clients from 20 to 27 June 2027?", "what_is_on", "count gaps"),
    ("trip", "The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?", None, "count"),
    ("trip", "The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?", None, "count"),
    ("nodates", "My clients have no dates yet. When is the best time to go to Hermanus?", "when_to_go", "gaps"),
    ("proof", "Tell me more about the FynArts Festival in June 2027. How sure is the date?", "tell_me_more", ""),
    ("changed", "I last looked on 1 November 2026. What changed in Hermanus?", "what_changed", ""),
    ("whale", "Is the Hermanus Whale Festival on in October 2027?", None, "notconfirmed"),
]  # fmt: skip


def dates_in(text: str) -> set[str]:
    """Each "day month" of a text, also from an ISO date (2026-11-23 is 23 November)."""
    names = MONTHS.split("|")
    words = re.findall(rf"\b(\d{{1,2}})(?:st|nd|rd|th)? ({MONTHS})\b", text)
    iso = re.findall(r"\b\d{4}-(\d{2})-(\d{2})\b", text)
    return {f"{int(day)} {month}" for day, month in words} | {
        f"{int(day)} {names[int(month) - 1]}" for month, day in iso if 1 <= int(month) <= 12
    }


def links_in(text: str) -> set[str]:
    """Each link of a text, with or without its scheme, so that a short form still counts."""
    found = re.findall(r"(?:https?://)?(?:[\w-]+\.)+[a-z]{2,}/[^\s)>\]]*", text)
    return {re.sub(r"^(https?://)?(www\.)?", "", link).rstrip(".,;:)*/") for link in found}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    load_env()
    client = anthropic.Anthropic()
    registry = json.loads(Path("registry.json").read_text(encoding="utf-8"))
    db = sqlite3.connect(f"{Path('feed.db').resolve().as_uri()}?mode=ro", uri=True)
    window = read.what_is_on(db, registry, "hermanus", date(2027, 6, 20), date(2027, 6, 27))["data"]
    total = window["counts"]["items"]
    titles = [card["title"] for group in window["groups"] for card in group["cards"]]

    sessions: dict[str, list] = {}
    seen: dict[
        str, str
    ] = {}  # for each session: the text that the tools returned, and the questions
    picks, rows, parts, cost = {}, [], [], 0.0
    for number, (session, question, tool, checks) in enumerate(QUESTIONS, start=1):
        history = sessions.setdefault(session, [])
        history.append({"role": "user", "content": question})
        result = agent.answer(client, MODEL, history)
        cost += result["cost_usd"]
        outputs = "\n".join(agent.run_tool(call["name"], call["input"]) for call in result["calls"])
        seen[session] = seen.get(session, "") + "\n" + question + "\n" + outputs
        text, names = result["text"], [call["name"] for call in result["calls"]]

        verdicts = {}
        if tool:
            verdicts[f"calls {tool}"] = tool in names
        new_links = links_in(text) - links_in(seen[session])
        verdicts["each link is from the feed"] = not new_links
        verdicts["gives a source link"] = bool(links_in(text))
        new_dates = dates_in(text) - dates_in(seen[session])
        verdicts["each date is from the feed or the question"] = not new_dates
        if "count" in checks:
            verdicts[f"says how many the feed has ({total})"] = bool(
                re.search(rf"\b{total}\b", text)
            )
        if "gaps" in checks:
            verdicts["says that the list can be incomplete"] = bool(
                re.search(r"Quicket|incomplete", text, re.IGNORECASE)
            )
        if "notconfirmed" in checks:
            verdicts["says not confirmed"] = bool(
                re.search(
                    r"not confirmed|no confirmed|not yet confirmed|unconfirmed", text, re.IGNORECASE
                )
            )
            # a day in October 2027 that is not an edge of the window that the agent asked for
            days = re.findall(r"\b(\d{1,2})(?:\s*[-–]\s*\d{1,2})?\s+October\s+2027", text)
            verdicts["gives no day in October 2027"] = not (set(days) - {"1", "31"})
        picks[number] = {title for title in titles if title.lower() in text.lower()}

        failed = [name for name, ok in verdicts.items() if not ok]
        notes = "; ".join(failed + ([f"dates not in the feed: {sorted(new_dates)}"] if new_dates else [])
                          + ([f"links not in the feed: {sorted(new_links)}"] if new_links else []))  # fmt: skip
        rows.append(
            f"| {number} | {question[:70]} | {', '.join(names) or 'none'} | {'PASS' if not failed else 'FAIL'} | {notes} | {result['cost_usd']:.4f} |"
        )
        parts += [
            f"## Question {number}", "", f"> {question}", "",
            "Tools called: " + (", ".join(f"`{c['name']}({json.dumps(c['input'])})`" for c in result["calls"]) or "none"), "",
            "Checks: " + "; ".join(f"{name}: {'pass' if ok else 'FAIL'}" for name, ok in verdicts.items()), "",
            text, "",
        ]  # fmt: skip
        print(
            f"Q{number} {'PASS' if not failed else 'FAIL'} calls={names} cost={result['cost_usd']:.4f} {notes}"
        )

    differ = picks[2] != picks[3]
    print(
        f"guest 2 picks: {sorted(picks[2])}\nguest 3 picks: {sorted(picks[3])}\ndiffer: {differ}\ntotal cost: {cost:.6f}"
    )
    head = [
        "# Agent test: a new Claude with only the four tools of the feed",
        "",
        f"Written by `research/acceptance/agent_test.py` on {date.today().isoformat()}. Model: `{MODEL}`.",
        "The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.",
        "Questions 1 to 3 are one conversation. Each other question is a new conversation.",
        "Code made the checks below against the text that the tools returned. Joshua's judgment is the last check.",
        "",
        "| # | Question | Tools called | Checks by code | What failed | Cost (USD) |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
        f"- The selections for guest 2 and guest 3 differ: **{'yes' if differ else 'NO'}**.",
        f"  - Guest 2 (wine and art, no crowds): {', '.join(sorted(picks[2])) or 'none named'}",
        f"  - Guest 3 (family, children 8 and 11): {', '.join(sorted(picks[3])) or 'none named'}",
        f"- Measured cost of the 7 answers: {cost:.6f} US dollars.",
        "",
    ]
    OUT.write_text("\n".join(head + parts) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
