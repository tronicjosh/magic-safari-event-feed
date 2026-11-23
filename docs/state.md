# State of the build

Last change: 2026-11-23. Read this file first in a new session. It says where the work is. The design is in `docs/design.md`; the end result is in `docs/acceptance.md`.

## Where we are

```text
design (draft 5) ── done
slice 0a  direction test T2 ............ PASSED (my review of the failures is open)
slice 0b.1 schema, single date, repeating  BUILT, blind review done (2 design questions open)
slice 0b.2 season, yearly not confirmed ... NEXT (new session)
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

## Slice 0a: PASSED on 2026-11-23

The quote check and the date check work on real pages. Result and gaps: `docs/assumptions.md` row T2, `research/t2_results.md`, `docs/model.md`. Spend: 0.048414 of 5 US dollars (one more small call was not recorded).

What exists now: `evals/pages/` (11 saved sources), `feed/render.py`, `feed/verify.py`, `feed/env.py`, `tests/test_verify.py` (30 tests), `research/t2/` (fetch, extract, check), `runs/runs.md`.

To repeat with no cost (answers are saved): `./.venv/Scripts/python research/t2/check.py`.

After my review of T2 (same day): design draft 4 (facts, not judgments; weekly source discovery; Hermanus as the pilot). T2b measured 15 experience and season pages: the checks pass, but 40 of 49 items have no time and 2 sites need a browser (`docs/assumptions.md`, row T2b). `evals/pages/` now has 23 sources.

Design draft 5 (same day): six read operations (`places`, `what_is_on`, `when_to_go`, `find`, `what_changed`, `tell_me_more`), short card, `counts`, server instructions. `docs/acceptance.md` (A3, A7, A8, A12, A14), the hand cases (now 24) and `CLAUDE.md` principle 2 agree with it.

## Slice 0b.1: BUILT on 2026-11-23

A saved model answer goes through `verify_item` into SQLite, and `what_is_on` reads it. Hand cases 1 to 3 pass. 56 tests pass; lint is clean.

- New: `feed/schema.sql` (six tables), `feed/store.py`, `feed/update.py` (core), `feed/read.py` (core), `registry.json`, `evals/cases/` (fixtures for hand cases 1 to 3), `tests/test_tracer.py`.
- Check: `./.venv/Scripts/python -m pytest && ./.venv/Scripts/python -m ruff check . && ./.venv/Scripts/python -m ruff format --check .`
- Real pages (2, 56 items): 37 stored, 19 not stored. The reasons are in `docs/model.md`.
- Decisions of Joshua in this session: the model decides with proof and a person is the last resort (principles 1 and 2 changed in `CLAUDE.md` and the design); the model marks "held each year" with a quote (T11); no town on the page gives the default town of the source; hand-case fixtures are in `evals/cases/`.
- Open for Joshua (from the blind review): (1) the weekly rule is expanded on the weekday word alone; (2) a range with closed days. See `docs/model.md`.
- Not tested: the rollback of an item that fails after its first row is written (no input reaches it). Not built: a set-aside table (the report only), merge of the same item from two pages, `holes`, category.
- Spend: 0.082276 of 5 US dollars.

## Slice 0b.2: NEXT (start in a new session)

Season and "yearly, no new dates": hand cases 4 and 5.

- Kind `months` becomes occurrence rows with month precision (one row for each year). The groups "seasons and experiences" and "not confirmed" get cards.
- The `yearly` field of T11 goes into the extraction format and `verify_item`. Saved answers with the field: `research/t11/out/` (7 pages).
- Real items: Southern Right Whales (June to November), Hermanus Whale Festival (2 to 4 October 2026, yearly with proof). FynArts has no proof of "yearly" on the saved pages.
- Measure first: the item count of the Xplorio page differed between two runs (8 and 5).

Blind review of `feed/verify.py`: done, 6 false-pass faults repaired, 30 tests pass, T2 numbers unchanged.

Open for slice 1 (render): hidden text by a stylesheet class, off-screen text, and `textarea` or `iframe` content pass `html_to_text`; an inline tag splits text over two lines (`R75<sup>1</sup>` becomes two lines). A change to render changes the saved page texts, so T2 must then run again (about 0.05 US dollars).

Open for slice 2 (verify): the price check takes any number in the quote and no currency; "Jan" or "Julie" in a name counts as a month; dates such as `2026-12-04` and `04.12.2026` fail (safe, but they go to review).

Not done in 0a: my review of the failures (step 5), a test for hidden text in `feed/render.py`, a commit.

## Open decisions (mine)

- O1 in the design: what the Vercel site does. Proposed: one connect page with a "try it" box, no model of its own.
- O2: which experience operators are approved.
- Hosting: test that the MCP server runs as a Vercel function; if not, one small machine.
- Quicket: request the official API key. Not collected in version 1.

## Changes after draft 3 that the design already holds

- No `include_local`, no threshold and no tier: each answer gives all items, in a neutral order, with `counts`.
- `holes` measures survivorship bias: sources collected against sources known, and the declared count of each source that is not collected.
- A Vercel site for connecting an agent to the MCP URL. The local version is identical and comes first.
