"""Write a check sheet of 20 stored items for Joshua: each fact, its quote, and the page text.

Run: ./.venv/Scripts/python research/sample/make_sample.py
Reads feed.db (read-only) and writes evals/sample_check.md. No model call, no request.
The sample: 3 key items of acceptance A7, then 17 items chosen with a fixed random seed.
"""

import random
import sqlite3
from pathlib import Path

DB = Path("feed.db").resolve()
OUT = Path("evals/sample_check.md")
KEY = ("FynArts Festival", "Southern Right Whales", "Hermanus Whale Festival%")
SEED, SIZE, AROUND = 20261123, 20, 140


def excerpt(page: str, quote: str) -> str:
    """The page text around the first part of the quote, on one line."""
    flat = " ".join(page.split())
    part = " ".join(quote.split(" | ")[0].split())
    at = flat.find(part)
    if at < 0:
        return "(the quote is not in the stored page text)"
    start, end = max(0, at - AROUND), min(len(flat), at + len(part) + AROUND)
    return (
        ("..." if start else "")
        + flat[start:at]
        + "**"
        + part
        + "**"
        + flat[at + len(part) : end]
        + "..."
    )


def main() -> None:
    db = sqlite3.connect(f"{DB.as_uri()}?mode=ro", uri=True)
    ids = []
    for title in KEY:
        row = db.execute("SELECT id FROM item WHERE title LIKE ? ORDER BY id", (title,)).fetchone()
        if row:
            ids.append(row[0])
    rest = [row[0] for row in db.execute("SELECT id FROM item ORDER BY id") if row[0] not in ids]
    ids += sorted(random.Random(SEED).sample(rest, SIZE - len(ids)))

    lines = [
        "# Sample check: 20 stored items against their pages",
        "",
        "Made by `research/sample/make_sample.py` from `feed.db` (the real run of 2026-11-23).",
        "For each item: open the source link, and mark each fact. A fact is **false** when the",
        "page does not say it. Write `x` in one box of each line. The count of false facts is",
        "acceptance line A1 (target 0).",
        "",
        "| Result | Count |",
        "|---|---|",
        "| Items checked | |",
        "| False facts | |",
        "",
    ]
    for number, item_id in enumerate(ids, start=1):
        title, kind, category, town, venue, price, yearly, below, link = db.execute(
            "SELECT title, kind, category, town, venue, price_text, repeats_yearly, below_bar, "
            "source_link FROM item WHERE id = ?",
            (item_id,),
        ).fetchone()
        whens = db.execute(
            "SELECT min(start_date), max(end_date), precision, rule, time_text, count(*) "
            "FROM occurrence WHERE item_id = ? GROUP BY precision, rule, time_text ORDER BY 1",
            (item_id,),
        ).fetchall()
        evidence = db.execute(
            "SELECT e.field, e.value, e.quote, e.model, p.text FROM evidence e "
            "JOIN page p ON p.id = e.page_id WHERE e.item_id = ? ORDER BY e.id",
            (item_id,),
        ).fetchall()
        lines += [f"## {number}. {title} (id {item_id})", "", f"Source: {link}", ""]
        facts = (
            f"- kind `{kind}` · category `{category}` · town `{town}` · "
            f"venue `{venue or 'not stated'}` · price `{price or 'not stated'}` · "
            f"held each year `{'yes' if yearly else 'no'}` · "
            f"below the traveller bar `{'yes' if below else 'no'}`"
        )
        lines.append(facts)
        for first, last, precision, rule, _, count in whens:
            how = {None: "stated on the page", "weekly": "written by code from a weekly rule"}
            how = how.get(rule, "written by code from a season with no year")
            lines.append(f"- when: `{first}` to `{last}` ({precision}; {count} rows; {how})")
        lines += [
            "",
            "| Fact | Value | Quote, in the page text | True | False |",
            "|---|---|---|---|---|",
        ]
        for field, value, quote, model, page in evidence:
            shown = excerpt(page, quote) if quote else f"(no quote: {model})"
            shown = shown.replace("|", "\\|")
            lines.append(f"| {field} | {value} | {shown} | [ ] | [ ] |")
        lines += [
            f"| category | {category} | (the model's choice from the list; no quote) | [ ] | [ ] |",
            "",
        ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT}: {len(ids)} items")


if __name__ == "__main__":
    main()
