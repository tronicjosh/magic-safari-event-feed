"""T2 step 3 and 4: run the code checks on the saved model answers and write the report.

Run: ./.venv/Scripts/python research/t2/check.py [--model claude-haiku-5-5]
No model call. Writes research/t2_results.md and prints the summary.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from feed.verify import LEVELS, quote_on_page, value_in_quote, verify_item

PAGES = Path("evals/pages")
OUT = Path("research/t2/out")
REPORT = Path("research/t2_results.md")


def field_group(field: str) -> str:
    if field == "when":
        return "no_time"  # the item has no date entry; this is not a failed date check
    return "when" if field.startswith("when[") else field


def check_page(record: dict, page: str) -> dict:
    fields, failures, levels, shapes = Counter(), [], Counter(), Counter()
    live = title_in_date_quote = dated = 0
    for item in record["items"]:
        results = verify_item(item, page)
        by_field = {}
        for result in results:
            group = field_group(result["field"])
            fields[group, result["ok"]] += 1
            by_field.setdefault(group, []).append(result["ok"])
            if result["level"]:
                levels[result["level"]] += 1
            if not result["ok"]:
                failures.append({"title": item["title"]["value"], **result, "item": item})
        # Design: an item is live when title and date pass. Town and source are not in T2.
        if all(by_field.get("title", [False])) and all(by_field.get("when", [False])):
            live += 1
        for when in item["when"]:
            shapes[when["kind"]] += 1
            dated += 1
            title = item["title"]["value"]
            if any(value_in_quote(title, q) and quote_on_page(q, page) for q in when["quotes"]):
                title_in_date_quote += 1
    return {
        "items": len(record["items"]),
        "live": live,
        "fields": fields,
        "failures": failures,
        "levels": levels,
        "shapes": shapes,
        "dated": dated,
        "title_in_date_quote": title_in_date_quote,
    }


def extract_of_page(page: str, quote: str, width: int = 90) -> str:
    """The place on the page that is nearest to the quote, for the review of a failure."""
    words = [word for word in quote.split() if len(word) > 3]
    for size in range(len(words), 0, -1):
        for start in range(len(words) - size + 1):
            probe = " ".join(words[start : start + size])
            at = " ".join(page.split()).find(probe)
            if at >= 0:
                flat = " ".join(page.split())
                return flat[max(0, at - width) : at + len(probe) + width]
    return "(no part of the quote is on the page)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-haiku-5-5")
    args = parser.parse_args()

    rows, all_failures = [], []
    total = Counter()
    for path in sorted(OUT.glob(f"*.{args.model}.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        page_id = record["page_id"]
        total["input_tokens"] += record["input_tokens"]
        total["output_tokens"] += record["output_tokens"]
        total["cost_micro_usd"] += round(record["cost_usd"] * 1_000_000)
        if record["items"] is None:
            rows.append(f"| {page_id} | no answer: {record['stop_reason']} | | | | | | |")
            continue
        page = (PAGES / f"{page_id}.txt").read_text(encoding="utf-8")
        result = check_page(record, page)
        passed = sum(n for (_, ok), n in result["fields"].items() if ok)
        failed = sum(n for (_, ok), n in result["fields"].items() if not ok)
        when_ok, when_bad = result["fields"]["when", True], result["fields"]["when", False]
        levels = " / ".join(str(result["levels"][level]) for level in LEVELS)
        shapes = ", ".join(f"{kind} {n}" for kind, n in sorted(result["shapes"].items()))
        rows.append(
            f"| {page_id} | {result['items']} | {result['live']} | {passed} | {failed} "
            f"| {when_ok} of {when_ok + when_bad} | {levels} | {shapes} |"
        )
        for key in ("items", "live", "dated", "title_in_date_quote"):
            total[key] += result[key]
        total["passed"] += passed
        total["failed"] += failed
        total["when_ok"] += when_ok
        total["when_all"] += when_ok + when_bad
        for failure in result["failures"]:
            total["reason: " + failure["reason"].split(";")[0].split(" not in")[0]] += 1
            all_failures.append((page_id, page, failure))

    if not rows:
        print(f"no answers for {args.model} in {OUT}")
        return 1

    lines = [
        f"# T2 results: quote check and date check on real pages ({args.model})",
        "",
        "Written by `research/t2/check.py` from the saved answers in `research/t2/out/`.",
        "",
        (
            "| Page | Items | Live (title and each date pass) | Fields passed | Fields failed "
            "| Dates passed | Quote match: exact / whitespace / punctuation | Date kinds |"
        ),
        "|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"- Items: {total['items']}. Live: {total['live']}.",
        f"- Fields passed: {total['passed']}. Fields failed: {total['failed']}.",
        f"- Dates passed: {total['when_ok']} of {total['when_all']}.",
        (
            f"- Date entries where a date quote also holds the title: "
            f"{total['title_in_date_quote']} of {total['dated']}."
        ),
        (
            f"- Tokens: {total['input_tokens']} in, {total['output_tokens']} out. "
            f"Cost: {total['cost_micro_usd'] / 1_000_000:.6f} US dollars "
            "(measured tokens times the list price)."
        ),
        "",
        "## Failures by cause",
        "",
    ]
    for key, count in sorted(total.items()):
        if key.startswith("reason: "):
            lines.append(f"- {key[8:]}: {count}")
    lines += ["", "## Each failure, in short form", ""]
    for page_id, page, failure in all_failures:
        item = failure["item"]
        field = failure["field"]
        entry = item["when"][int(field[5:-1])] if field.startswith("when[") else item.get(field)
        quotes = (
            entry["quotes"] if entry and "quotes" in entry else [entry["quote"]] if entry else []
        )
        lines += [
            f"**{page_id}: {failure['title']}** ({field}: {failure['reason']})",
            "",
            f"- entry: `{json.dumps({k: v for k, v in (entry or {}).items() if k not in ('quote', 'quotes')}, ensure_ascii=False)}`",
            *[f"- quote: `{quote}`" for quote in quotes],
            f"- page: `{extract_of_page(page, quotes[0]) if quotes else ''}`",
            "",
        ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[4 : lines.index("## Each failure, in short form")]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
