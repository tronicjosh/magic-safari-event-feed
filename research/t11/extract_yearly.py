"""T11: can the model decide "this item is held each year", with a quote as proof?

Run: ./.venv/Scripts/python research/t11/extract_yearly.py
It is the T2 extraction with one more field, `yearly`. Answers go to research/t11/out/.
A page that has an answer file is not sent again.
"""

import copy
import json
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, "research/t2")
import extract as t2

from feed.env import load_env

OUT = Path("research/t11/out")
MODEL = "claude-haiku-5-5"
PAGE_IDS = [
    "ht_festivals",
    "whale_festival",
    "kalfiefees",
    "xplorio_events",
    "ot_yearly_pdf",
    "x_ht_southern_right_whales",
    "wesgro_events_p1",
]

YEARLY = """\
- yearly: does the page state that this item is held or takes place each year? Give value \
"yes" and, as the quote, the span of the page that states it for this item (for example \
"annual", "every year", "each September", "since 1991", "23rd"). Give "" for value and quote \
if the page does not state it. A date alone is not proof. Do not use your own knowledge of \
the item.
"""

SCHEMA = copy.deepcopy(t2.SCHEMA)
_item = SCHEMA["properties"]["items"]["items"]
_item["properties"]["yearly"] = t2._FIELD
_item["required"].append("yearly")


def main() -> int:
    load_env()
    client = anthropic.Anthropic()
    OUT.mkdir(parents=True, exist_ok=True)
    t2.SYSTEM = t2.SYSTEM.replace("- when: a list", YEARLY + "- when: a list")
    t2.SCHEMA = SCHEMA
    for page_id in PAGE_IDS:
        out_path = OUT / f"{page_id}.{MODEL}.json"
        if out_path.exists():
            print(f"skip  {page_id} (answer saved)")
            continue
        text = (t2.PAGES / f"{page_id}.txt").read_text(encoding="utf-8")
        try:
            record = t2.extract(client, MODEL, page_id, text)
        except anthropic.APIError as error:
            print(f"FAIL  {page_id}  {type(error).__name__}: {error}")
            return 1
        out_path.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        count = "none" if record["items"] is None else len(record["items"])
        print(
            f"ok    {page_id}  items={count}  in={record['input_tokens']} "
            f"out={record['output_tokens']}  ${record['cost_usd']}  stop={record['stop_reason']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
