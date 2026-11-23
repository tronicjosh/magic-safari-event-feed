"""The runner of the improvement loop: it asks the demo agent each question of one file.

Run: ./.venv/Scripts/python research/loop/run.py research/loop/pass1_questions.json
The file is a list of {"id", "tests", "turns": [...]}. Each question is one conversation with
`claude-opus-5-5`, which has only the five tools and the server instructions of the feed.
The result goes to <name>_answers.json after each question, so that no answer is lost.
Each answer costs money. The measured spend is kept in research/loop/spend.json, and the
runner stops before the limit.
"""

import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic

from feed import agent
from feed.env import load_env

MODEL = "claude-opus-5-5"
SPEND = Path("research/loop/spend.json")
STOP_AT = 9.70  # US dollars; the limit of the project is 10
TAGS = (
    "Confirmed, programme not stated",
    "Confirmed",
    "From a weekly rule, confirm near the date",
    "From a rule of the page, check the day",
    "Season",
    "Not confirmed, no dates yet",
    "Past, not known if held again",
)
lock = threading.Lock()


def checks(answer: str, tool_text: str) -> dict:
    """Facts that code can check. The judgment of the answer is not here.

    An item line is a bullet or a numbered line that holds a link. A heading is a line of 6
    words or less with no link and no end mark ("**Art**", "## Wine", "Art:"). Each other
    line is text outside the items, also when it is written as a bullet or in bold.
    """
    links = re.findall(r"https?://[^\s)\]>\"]+", answer)
    items, outside = [], 0
    # an item line that goes on a second, indented line is one line
    joined = re.sub(r"\n[ \t]+(?![-*•–]\s|\d+[.)]\s)", " ", answer)
    for line in joined.splitlines():
        text = line.strip()
        if not text or not re.search(r"\w", text):
            continue
        if re.match(r"([-*•–]|\d+[.)])\s", text) and "](http" in text:
            items.append(text)
        elif (
            len(text.split()) <= 6 and "](http" not in text and text.strip("*_# ")[-1:] not in ".!?"
        ):
            continue  # a heading
        else:
            outside += len(text.split())
    return {
        "words": len(answer.split()),
        "words_outside_items": outside,
        "links_not_in_the_feed": sorted({x for x in links if x.rstrip(".,") not in tool_text}),
        "list_lines": len(items),
        "list_lines_with_no_tag": sum(not any(tag in item for tag in TAGS) for item in items),
        "quotes": len(re.findall(r"[\"“][^\"”]{12,}[\"”]", answer)),
    }


def ask(client, question: dict) -> dict:
    messages, turns, cost, tool_text = [], [], 0.0, ""
    for turn in question["turns"]:
        messages.append({"role": "user", "content": turn})
        result = agent.answer(client, MODEL, messages)
        calls = []
        for call in result["calls"]:
            text = agent.run_tool(call["name"], call["input"])  # the same bytes; no model
            tool_text += text
            calls.append({**call, "first_lines": text.splitlines()[:12]})
        cost += result["cost_usd"]
        # each turn is measured, against the tool text of the conversation up to that turn
        measured = checks(result["text"], tool_text)
        turns.append(
            {"designer": turn, "calls": calls, "answer": result["text"], "checks": measured}
        )
    return {
        **question,
        "turns": turns,
        "cost_usd": round(cost, 6),
        "checks": turns[-1]["checks"],  # the last turn, as before
    }


def main() -> int:
    load_env()
    path = Path(sys.argv[1])
    out = path.with_name(path.name.replace("_questions.json", "_answers.json"))
    questions = json.loads(path.read_text(encoding="utf-8"))
    done = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    seen = {record["id"] for record in done}
    client = anthropic.Anthropic()

    def one(question):
        with lock:
            spent = json.loads(SPEND.read_text())["total_usd"]
        if spent >= STOP_AT:
            print(f"STOP  {question['id']}: spend {spent} has reached {STOP_AT}")
            return
        try:
            record = ask(client, question)
        except anthropic.APIError as error:
            print(f"FAIL  {question['id']}  {type(error).__name__}: {error}")
            return
        with lock:
            ledger = json.loads(SPEND.read_text())
            ledger["total_usd"] = round(ledger["total_usd"] + record["cost_usd"], 6)
            SPEND.write_text(json.dumps(ledger, indent=1))
            done.append(record)
            out.write_text(json.dumps(done, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"ok    {record['id']}  {record['cost_usd']}")
        for number, turn in enumerate(record["turns"], 1):
            print(f"      turn {number}  {turn['checks']}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, [q for q in questions if q["id"] not in seen]))
    total = round(sum(record["cost_usd"] for record in done), 6)
    print(
        f"{len(done)} answers in {out}. Cost of this file: {total}. "
        f"Total spend: {json.loads(SPEND.read_text())['total_usd']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
