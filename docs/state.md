# State of the build

Last change: 2026-11-23. Read this file first in a new session. It says where the work is. The design is in `docs/design.md`; the end result is in `docs/acceptance.md`.

## Where we are

```text
design (draft 3) ── done
slice 0a  direction test T2 ............ NEXT   (not started; nothing is built)
slice 0b  schema + tracer bullet ....... after 0a passes
slices 1-3  collect | verify | read .... three builders in parallel worktrees, then a blind reviewer each
slice 4   first real run + my review
slice 5   fresh-Claude test, site, write-up
```

Way of work for each slice: plan, my review of the plan, build, report with one diagram. Then go to the next slice without a new instruction.

## What exists

- Branch `build` (local commits; `origin` is the private GitHub repository; a push needs my approval).
- `pyproject.toml` with the dependencies. A virtual environment in `.venv` (git ignores it). Installed and imported without error: anthropic 2.12.0, beautifulsoup4, pypdf, httpx, fastapi, mcp, pytest, ruff.
- Empty folders: `feed/`, `evals/pages/`, `runs/`, `tests/`.
- No pipeline code. No model call was made. Spend: 0 of 5 US dollars.
- The key is `ANTHROPIC_API_KEY` in `.env`. Code loads it into the environment. Never print it.

Run Python as `./.venv/Scripts/python` (Windows, Git Bash).

## Slice 0a: the direction test T2

**Question:** do the quote check and the date check work on real Hermanus pages? If not, stop and change the design before any builder starts.

**Plan (not yet reviewed by me):**

1. Save about 10 real text sources into `evals/pages/` as visible text, with the raw file beside it:
   - the newest Overstrand monthly PDF and the yearly PDF (find the file through `whalecoast.info/wp-json/wp/v2/media`);
   - the Overstrand "this weekend" page (page data; text comes before the JSON and must be removed);
   - Hermanus Tourism: festivals page and whale-watching page;
   - Hermanus Whale Festival and Kalfiefees home pages;
   - Xplorio events, Wesgro events page 1;
   - two operator pages: Southern Right Charters and White Shark Projects.
2. For each page, one call to `claude-haiku-5-5` with a JSON schema: items, and for each field a value and a word-for-word quote. A date has a list of quotes (the row and the header).
3. Code checks, with no model: quote on page; value in quote; date parts (day, month, year) in the date quotes; shape.
4. Report in `research/t2_results.md` and one row in `docs/assumptions.md`: for each page, items found, fields passed, fields failed and why. Also tokens and cost in `runs/`.
5. I review the failures in short form: page extract, quote, entry.

**Pass:** most fields pass, and each failure has a cause that a rule or the stronger-model retry can fix. **Fail:** dates in list rows (day only, year in a header) cannot be checked. Then the date check in the design must change.

**Access paths and odd results:** `research/t10_collection_strategy.md`, section 2.

## Open decisions (mine)

- O1 in the design: what the Vercel site does. Proposed: one connect page with a "try it" box, no model of its own.
- O2: which experience operators are approved.
- Hosting: test that the MCP server runs as a Vercel function; if not, one small machine.
- Quicket: request the official API key. Not collected in version 1.

## Changes after draft 3 that the design already holds

- No `include_local` and no threshold: each answer shows all groups, headline first.
- `holes` measures survivorship bias: sources collected against sources known, and the declared count of each source that is not collected.
- A Vercel site for connecting an agent to the MCP URL. The local version is identical and comes first.
