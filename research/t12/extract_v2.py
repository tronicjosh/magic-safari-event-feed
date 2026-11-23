"""T12: the model chooses the town from the list and marks a weekly rule as ongoing.

Run: ./.venv/Scripts/python research/t12/extract_v2.py
One call to feed.extract for each page below. Answers go to research/t12/out/.
A page that has an answer file is not sent again.
"""

import json
import sys
from pathlib import Path

import anthropic

from feed.env import load_env
from feed.extract import extract

OUT = Path("research/t12/out")
MODEL = "claude-haiku-5-5"
PAGES = {
    "ht_festivals": "evals/pages",
    "overstrand_weekend": "evals/pages",
    "ot_monthly_pdf": "evals/pages",
    "ot_yearly_pdf": "evals/pages",
    "weekly_traps": "evals/cases",
}


def main() -> int:
    load_env()
    client = anthropic.Anthropic()
    OUT.mkdir(parents=True, exist_ok=True)
    registry = json.loads(Path("registry.json").read_text(encoding="utf-8"))
    towns = registry["places"]["hermanus"]["towns"]
    for page_id, folder in PAGES.items():
        out_path = OUT / f"{page_id}.{MODEL}.json"
        if out_path.exists():
            print(f"skip  {page_id} (answer saved)")
            continue
        text = Path(folder, f"{page_id}.txt").read_text(encoding="utf-8")
        try:
            record = extract(client, MODEL, page_id, text, towns)
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
