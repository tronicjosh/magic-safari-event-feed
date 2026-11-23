# State of the build

Last change: 2026-11-23. Read this file first in a new session. It says where the work is. The design is in `docs/design.md` (start with "Scope of the build"); the end result is in `docs/acceptance.md` (see "Status on 2026-11-23").

## Where we are

```text
design (draft 5 + scope cut) ......................... done
slice 0a   direction test T2 ......................... done
slice 0b.1 schema, verify, update, what_is_on ........ done, 2 blind reviews
builders   A ingest | B season, yearly, second run | C read + MCP ... done, integrated one at a time
repairs    season proof, all year, running season, category, reasons ... done, each with a break test
real run   10 live pages, 151 items, 0.064780 USD; second run 0 model calls ... done
review     one blind review of the joined code ....... RUNNING when this file was written
write-up   design.md true to the code ................ partly (scope table, cost); my read is open
mine       check 20 stored items and the bar wording; the test with a new Claude ... OPEN
```

## What exists

```text
registry.json -> feed/fetch.py -> feed/render.py -> hash -> feed/extract.py (model)
     -> feed/verify.py (code) -> feed/update.py -> SQLite (feed/schema.sql, feed.db)
     -> feed/read.py -> feed/mcp_server.py (four tools, stdio)
feed/ingest.py runs the left side: python -m feed.ingest
```

- Branch `build`, local commits only. A push needs my approval.
- Check: `./.venv/Scripts/python -m pytest && ./.venv/Scripts/python -m ruff check . && ./.venv/Scripts/python -m ruff format --check .` (207 tests).
- `feed.db` is the database of the real run (git ignores it). `python -m feed.ingest` makes it again; a run on unchanged pages costs nothing.
- Spend: 0.240788 of 5 US dollars (tests 0.176008, real run 0.064780).

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

## The MCP server, for the test with a new Claude

```bash
# from the repository root; the database is opened read-only
FEED_DB=feed.db ./.venv/Scripts/python -m feed.mcp_server
# add it to Claude Code for a test session in an EMPTY folder (so that no CLAUDE.md is read):
claude mcp add hermanus-feed --scope user --env FEED_DB="<repo>/feed.db" --env FEED_REGISTRY="<repo>/registry.json" -- "<repo>/.venv/Scripts/python" -m feed.mcp_server
```

Tools: `what_is_on`, `when_to_go`, `tell_me_more`, `what_changed`. The rules are in the server instructions, one time.

## Open

- **Mine:** check a sample of 20 stored items against their pages; check the town choices (the model uses its knowledge: "Old Harbour" gives Hermanus); correct the wording of the traveller bar and the list of categories in `registry.json` (both are Claude's first draft); run the test with a new Claude (acceptance A8 and A14).
- **Known gaps, by decision (in the design as "next"):** the same event from two sources is two items; a moved date shows as an added date, the old date stays; no `cancelled`; a rule by month ("first Friday") is shown as "All year" with its quote, not as dates; text hidden by a stylesheet class passes render; judgments of the model differ between runs (item count, bar, a weekly rule).
- **Not measured:** false facts against a confirmed set (the set does not exist); a run one week later (the second run was on the same day).

## History of this session (2026-11-23)

Decisions by Joshua, each recorded in `docs/model.md`: the model decides with proof and a person is the last resort; town, weekly rule, yearly and category are choices of the model; a soft traveller bar (the hard visitor bar was built, measured at 0 of 180 items, and removed); a basic change log with `first seen` on each card and `what_changed`; the scope cut to one path; three builders in parallel.
