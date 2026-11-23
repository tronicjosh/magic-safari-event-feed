"""A demo with no agent: the text that an agent gets for one test trip, from the real database.

Run: python -m feed.demo            (the database is FEED_DB, default feed.db; read-only)
It prints the answers of the four operations for a trip to the first place of the registry,
20 to 27 June 2027. It makes no model call and no request to a source.
"""

import json
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

from feed import read

FROM, TO = date(2027, 6, 20), date(2027, 6, 27)
SINCE = date(2026, 11, 1)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    path = Path(os.environ.get("FEED_DB", "feed.db")).resolve()
    if not path.exists():
        print(f"No database at {path}. Run: python -m feed.ingest")
        return 1
    registry_path = os.environ.get("FEED_REGISTRY", "registry.json")
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    place = next(iter(registry["places"]))
    db = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)

    on = read.what_is_on(db, registry, place, FROM, TO)
    cards = [card for group in on["data"]["groups"] for card in group["cards"]]
    steps = [
        ('1. "What is on for my clients from 20 to 27 June 2027?"  ->  what_is_on', on),
        ('2. "When is the best time to go?" (June to August)  ->  when_to_go',
         read.when_to_go(db, registry, place, 6, 8)),
        ('3. "Tell me more about the first two items."  ->  tell_me_more',
         read.tell_me_more(db, registry, [card["id"] for card in cards[:2]])),
        ('4. "I last looked on 1 November 2026. What changed?"  ->  what_changed (first 40 lines)',
         read.what_changed(db, registry, place, SINCE)),
    ]  # fmt: skip
    for number, (question, answer) in enumerate(steps, start=1):
        text = answer["text"]
        if number == 4:
            text = "\n".join(text.splitlines()[:40]) + "\n..."
        print("=" * 100, question, "=" * 100, text, sep="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
