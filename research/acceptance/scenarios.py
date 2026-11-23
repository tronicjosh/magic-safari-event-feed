"""A wide set of scenarios for the agent: what a travel designer can ask, well or badly.

Run:      ./.venv/Scripts/python research/acceptance/scenarios.py [name] [--only id,id]
          It costs money: about 1 US dollar for all scenarios on claude-opus-5-5.
Re-check: ./.venv/Scripts/python research/acceptance/scenarios.py [name] --recheck   (no model call)

Each scenario is one conversation. `must` and `must_not` are patterns for the last answer; they
state what a good answer does for this scenario. The generic checks are those of agent_test.py.
The transcript goes to research/acceptance/<name>.md (default: scenarios). A person reads it:
the patterns find the clear faults, not each fault.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import anthropic
from agent_test import MODEL, dates_in, hosts_in, quotes_in

from feed import agent
from feed.env import load_env

JUNE = "What is on in Hermanus for my clients from 20 to 27 June 2027?"
# id, the turns of the designer, the tool that must be called (or None), patterns that the last
# answer must match, patterns that it must not match, the word limit, and free dates (the agent
# works out dates from "next weekend", so a date that is not in the feed is not a fault).
SCENARIOS = [
    # the trip has dates
    ("dated_one_day", ["Is anything on in Hermanus on Saturday 5 December 2026?"], "what_is_on", [r"5 Dec"], [], 150, False),
    ("dated_month", ["What is on in Hermanus in December 2026?"], "what_is_on", [r"\d+ of \d+"], [], 170, False),
    ("dated_long", ["My clients are in Hermanus from 1 June to 31 August 2027. What is on?"], "what_is_on", [r"\d+ of \d+", r"FynArts"], [], 170, False),
    ("dated_quiet_day", ["Is anything on in Hermanus on Tuesday 9 March 2027?"], "what_is_on", [], [], 150, False),
    ("dated_past", ["What was on in Hermanus from 1 to 31 March 2026?"], "what_is_on", [], [], 150, False),
    ("dated_june_2028", ["What is on in Hermanus from 3 to 10 June 2028?"], "what_is_on", [r"market|Saturday"], [r"no (weekly|recurring|regular|markets)"], 150, False),
    ("dated_2029", ["What is on in Hermanus from 10 to 17 June 2029?"], "what_is_on", [r"too far|does not (reach|go|cover)|only (reaches|covers|goes)|horizon|as far as|beyond"], [r"nothing (is )?on\b(?!.*(too far|beyond))"], 150, False),
    ("dated_tonight", ["My clients are in Hermanus now. Is anything on tonight or tomorrow?"], "what_is_on", [], [], 150, True),
    ("dated_next_weekend", ["What is on in Hermanus next weekend?"], "what_is_on", [r"2[89] Nov"], [], 150, True),
    # no dates yet
    ("nodates_recurring", ["What recurring or regular events does Hermanus have?"], None, [r"[Ss]aturday", r"[Mm]arket"], [r"no (recurring|regular|weekly)"], 170, False),
    ("nodates_weekly_market", ["Is there a weekly market in Hermanus?"], None, [r"[Ss]aturday"], [r"\bno weekly market|there (is|are) no\b"], 150, False),
    ("nodates_wine", ["My guests love wine. No dates yet. What does Hermanus have for them?"], None, [r"[Ww]ine"], [], 150, False),
    ("nodates_september", ["They are thinking of September 2027. What is on then?"], None, [r"September"], [], 150, False),
    ("nodates_compare", ["Which is better for whales in Hermanus: July or October?"], None, [r"June|November|season"], [], 150, False),
    # a named item
    ("named_brief_market", ["Is the Hermanus Country Market on on a Saturday?"], None, [r"not (state|say|give)|does ?n[o']t (state|say|give)|no day"], [], 150, False),
    ("named_missing", ["Is there a J. Cole concert in Hermanus in December 2026?"], "what_is_on", [r"not in the feed|no .*(J\. ?Cole|such|concert).*feed|feed (has|does|lists|shows) no|does ?n[o']t (list|have|show)|isn't in|not listed", r"Quicket"], [], 150, False),
    ("named_experience", ["Can my clients do shark cage diving near Hermanus in July 2027?"], None, [r"feed (has|does|lists|shows) no|not in the feed|does ?n[o']t (list|have|cover|show|include)|isn't in|not listed"], [], 150, False),
    ("named_kalfiefees", ["When is Kalfiefees?"], None, [r"August 2026|Aug 2026"], [r"August 2027"], 150, False),
    ("named_price", ["How much does the FynArts Festival cost?"], None, [r"not (stated|given)|does ?n[o']t (state|give|say)|no price"], [r"R ?\d"], 150, False),
    # bad or hard input
    ("bad_other_city", ["What is on in Cape Town from 1 to 5 January 2027?"], None, [r"Hermanus", r"only|does ?n[o']t cover|not cover|doesn't have|no data"], [], 120, False),
    ("bad_town_inside", ["What is on in Stanford in the first week of December 2026?"], "what_is_on", [r"Stanford"], [r"does ?n[o']t cover Stanford|no data for Stanford"], 150, False),
    ("bad_impossible_date", ["What is on in Hermanus from 30 February to 2 March 2027?"], None, [r"30 February|does ?n[o']t exist|not a (real|valid) date|no 30"], [], 150, False),
    ("bad_reversed", ["What is on in Hermanus from 27 June to 20 June 2027?"], "what_is_on", [r"20.{1,12}27 June|swap|other way|reversed|before"], [], 170, False),
    ("bad_no_place", ["What is on from 1 to 7 December 2026?"], None, [r"Hermanus"], [], 150, False),
    ("bad_gibberish", ["asdf qwer zxcv"], None, [r"\?"], [], 80, False),
    ("bad_weather", ["What is the weather like in Hermanus in June?"], None, [r"does ?n[o']t (have|cover|include|hold)|no weather|not (in|part of) the feed|can't|cannot"], [r"\d+ ?°|degrees"], 100, False),
    ("bad_booking", ["Book two tickets for the FynArts Festival on 25 June 2027."], None, [r"can't|cannot|not able|unable|read-only", r"hermanusfynarts"], [], 120, False),
    # a second question in the same conversation
    ("follow_rest", [JUNE, "Show me the ones you left out."], None, [r"[Pp]arkrun|Park Run", r"Art ?walk|Artwalk"], [], 220, False),
    ("follow_proof", [JUNE, "How sure is the date of the wine market?"], "tell_me_more", [r"[Ss]aturdays are busy market days", r"rule"], [], 150, False),
    ("follow_link", [JUNE, "Send me the link for the FynArts Festival."], None, [r"https://www\.hermanusfynarts\.co\.za"], [], 80, False),
    # what changed
    ("changed_same_day", ["I last looked on 23 November 2026. What changed in Hermanus?"], "what_changed", [r"nothing|no (changes|new)|cannot|can't|not (changed|able)"], [r"151 (new|items are new)"], 150, False),
    ("changed_future", ["What changed in Hermanus since 1 January 2027?"], "what_changed", [r"23 November|future|has ?n[o']t|not yet|after"], [], 120, False),
    # a different language
    ("afrikaans", ["Wat is aan in Hermanus van 20 tot 27 Junie 2027?"], "what_is_on", [r"FynArts", r"13"], [], 170, False),
]  # fmt: skip


def saved(path: Path) -> dict:
    """The answers of an earlier run, from its transcript: for each id, its turns."""
    runs = {}
    for body in path.read_text(encoding="utf-8").split("\n## ")[1:]:
        name = body.split("\n", 1)[0].strip()
        turns = []
        for chunk in body.split("\n### Turn ")[1:]:
            calls_line = re.search(r"^Tools called: (.*)$", chunk, re.MULTILINE).group(1)
            cost = float(re.search(r"^Cost: ([\d.]+)", chunk, re.MULTILINE).group(1))
            calls = [
                {"name": tool, "input": json.loads(arguments)}
                for tool, arguments in re.findall(r"`(\w+)\((\{.*?\})\)`", calls_line)
            ]
            text = re.search(r"<!-- answer -->\n(.*?)\n<!-- end -->", chunk, re.DOTALL).group(1)
            turns.append({"text": text, "calls": calls, "cost_usd": cost})
        runs[name] = turns
    return runs


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    names = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
    out = Path("research/acceptance", (names[0] if names else "scenarios") + ".md")
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    old = saved(out) if "--recheck" in sys.argv else None
    if old is None:
        load_env()
        client = anthropic.Anthropic()

    rows, parts, cost, passed = [], [], 0.0, 0
    for name, turns, tool, must, must_not, limit, free_dates in SCENARIOS:
        if only and name not in only:
            continue
        history, seen, names_called, answers = [], "", [], []
        for index, question in enumerate(turns):
            if old is None:
                history.append({"role": "user", "content": question})
                result = agent.answer(client, MODEL, history)
            else:
                result = old[name][index]
            cost += result["cost_usd"]
            outputs = "\n".join(agent.run_tool(c["name"], c["input"]) for c in result["calls"])
            seen += "\n" + question + "\n" + outputs
            names_called += [call["name"] for call in result["calls"]]
            answers.append(result)
        text = answers[-1]["text"]

        failed = []
        if tool and tool not in names_called:
            failed.append(f"does not call {tool}")
        if hosts_in(text) - hosts_in(seen):
            failed.append(
                f"a site that is not in the feed: {sorted(hosts_in(text) - hosts_in(seen))}"
            )
        if not free_dates and dates_in(text) - dates_in(seen):
            failed.append(
                f"a date that is not in the feed: {sorted(dates_in(text) - dates_in(seen))}"
            )
        if len(text.split()) > limit:
            failed.append(f"{len(text.split())} words (limit {limit})")
        if len(quotes_in(text)) > (2 if name == "follow_proof" else 0):
            failed.append(f"{len(quotes_in(text))} quotes of a page")
        failed += [f"lacks /{pattern}/" for pattern in must if not re.search(pattern, text)]
        failed += [f"has /{pattern}/" for pattern in must_not if re.search(pattern, text)]
        passed += not failed

        spent = sum(answer["cost_usd"] for answer in answers)
        state = "PASS" if not failed else "FAIL"
        rows.append(
            f"| {name} | {turns[-1][:58]} | {', '.join(names_called) or 'none'} "
            f"| {len(text.split())} | {state} | {'; '.join(failed)} | {spent:.4f} |"
        )
        parts += [f"## {name}", ""]
        for index, (question, result) in enumerate(zip(turns, answers, strict=True), start=1):
            calls = ", ".join(f"`{c['name']}({json.dumps(c['input'])})`" for c in result["calls"])
            parts += [
                f"### Turn {index}",
                "",
                f"> {question}",
                "",
                f"Tools called: {calls or 'none'}",
            ]
            # the answer is between two marks, so that a re-check reads it back exactly
            parts += [f"Cost: {result['cost_usd']:.4f}", "", "<!-- answer -->"]
            parts += [result["text"].strip(), "<!-- end -->", ""]
        print(f"{state} {name:22} {len(text.split()):4} words  {names_called}  {failed}")

    total = len(rows)
    print(f"{passed} of {total} pass the checks by code. Cost {cost:.6f}")
    head = [
        "# Scenarios: what a designer can ask, well or badly",
        "",
        f"Written by `research/acceptance/scenarios.py` on {date.today().isoformat()}. Model: `{MODEL}`.",
        "The agent has only the four tools and the server instructions of the feed.",
        f"**{passed} of {total} scenarios pass the checks by code.** Measured cost: {cost:.6f} US dollars.",
        "",
        "| Scenario | Last question | Tools called | Words | Checks | What failed | Cost (USD) |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    if not only:
        out.write_text("\n".join(head + parts) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
