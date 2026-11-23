# State of the build

Last change: 2026-11-23. Read this file first in a new session. It says where the work is. The design is in `docs/design.md` (start with "Built, and not built"); the end result is in `docs/acceptance.md` (each line has its status).

## Where we are

```text
design (draft 5 + scope cut) ......................... done
slice 0a   direction test T2 ......................... done
slice 0b.1 schema, verify, update, what_is_on ........ done, 2 blind reviews
builders   A ingest | B season, yearly, second run | C read + MCP ... done, integrated one at a time
repairs    season proof, all year, running season, category, reasons ... done, each with a break test
real run   10 live pages, 151 items, 0.064780 USD; second run 0 model calls ... done
review     one blind review of the joined code ....... done, 7 findings, repaired with a test each
write-up   design.md draft 6: shortened, true to the code; acceptance.md and CLAUDE.md refined ... done; my read is open
agent test 7 questions to a new Claude with only the tools ... done: research/acceptance/agent_test.md
answers    expected answers agreed (option B), instructions tuned in 3 rounds ... done: research/acceptance/comparison.md
scenarios  39 conversations; a plan of 8 repairs (find, weekly items, horizon, one card for two sources) ... done: research/acceptance/scenarios*.md
handover   README proved from a clean clone; feed.db in the repository; one definition of the tools ... done
mine       mark the sample of 20 items; judge the agent's answers; read the design ... OPEN
```

## What exists

```text
registry.json -> feed/fetch.py -> feed/render.py -> hash -> feed/extract.py (model)
     -> feed/verify.py (code) -> feed/update.py -> SQLite (feed/schema.sql, feed.db)
     -> feed/read.py -> feed/mcp_server.py (five tools, stdio)
feed/ingest.py runs the left side: python -m feed.ingest
```

- Branches `build` and `main` are equal and pushed to `origin` on 2026-11-23, with Joshua's approval. A later push needs his approval again.
- Check: `./.venv/Scripts/python -m pytest && ./.venv/Scripts/python -m ruff check . && ./.venv/Scripts/python -m ruff format --check .` (230 tests).
- `feed.db` is the database of the real run of 2026-11-23. It is in the repository, so the feed runs from a clone with no key. `python -m feed.ingest` updates it; a run on unchanged pages costs nothing.
- Spend: 4.790660 of 5 US dollars. No more model calls are planned. An answer of the agent on the demo page costs about 0.02 to 0.08 US dollars.

## What the model decides, and what code checks

| The model decides | Code checks | If the check fails |
|---|---|---|
| Fields with quotes (title, venue, price, dates) | Quote on page, value in quote, shape | Title or date: item not stored. Venue or price: left empty, reason in the report |
| Town, from the list of the place, or "outside" | Value in the list, quote on page | Item not stored |
| Category, from the list of the registry | Value in the list | Stored as "other" |
| A weekly rule has no end (`ongoing`) | No digit in the quote, except a clock time with minutes | Item not stored |
| Held each year (`yearly`) | Quote on page | Not marked; a season with no year is then not stored |
| "All year" (January to December, no year) | Quote on page | Item not stored |
| Below the traveller bar (soft) | Quote on page | Shown in its normal group |

A person is not a step. An item that is not stored is in the run report with its reason.

## Demo and checks that are ready

| What | Where | How |
|---|---|---|
| Demo page with an agent | `feed/web.py`, `feed/agent.py` | `./.venv/Scripts/python -m uvicorn feed.web:app --port 8000`, then http://localhost:8000. "Ask the agent" is a Claude model with only the five tools and the server instructions; each answer is a paid model call and the page shows its measured cost. The other tabs call each tool with no model |
| Demo with no agent | `feed/demo.py` | `./.venv/Scripts/python -m feed.demo` prints the text of the four operations for a trip of 20 to 27 June 2027, from `feed.db` |
| Test with a new Claude (A8, A14) | `C:/Users/joshj/Desktop/Magic Safari/feed-demo/` (outside the repository, so no `CLAUDE.md` is read) | Start Claude Code in that folder, approve the server `event-feed`, and ask the questions in `questions.md` |
| Sample of 20 stored items (A1) | `evals/sample_check.md` | Open each source link and mark each fact true or false. `research/sample/make_sample.py` makes the sheet again |

The MCP server: `python -m feed.mcp_server`, with `FEED_DB` and `FEED_REGISTRY` for the paths; the database is opened read-only. Tools: `what_is_on`, `when_to_go`, `find`, `tell_me_more`, `what_changed`. The rules are in the server instructions, one time.

## Open

- **Mine:** check a sample of 20 stored items against their pages; check the town choices (the model uses its knowledge: "Old Harbour" gives Hermanus); correct the wording of the traveller bar and the list of categories in `registry.json` (both are Claude's first draft); run the test with a new Claude (acceptance A8 and A14).
- **Known gaps, by decision (in the design as "next"):** the same event from two sources is two items; a moved date shows as an added date, the old date stays; no `cancelled`; a rule by month ("first Friday") is shown as "All year" with its quote, not as dates; text hidden by a stylesheet class passes render; judgments of the model differ between runs (item count, bar, a weekly rule).
- **Not measured:** false facts against a confirmed set (the set does not exist); a run one week later (the second run was on the same day).

## History of this session (2026-11-23)

Decisions by Joshua, each recorded in `docs/model.md`: the model decides with proof and a person is the last resort; town, weekly rule, yearly and category are choices of the model; a soft traveller bar (the hard visitor bar was built, measured at 0 of 180 items, and removed); a basic change log with `first seen` on each card and `what_changed`; the scope cut to one path; three builders in parallel.
