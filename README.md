# Hermanus event feed

A homework project for Magic Safari. It is a feed of events and seasons in and near Hermanus that a travel designer's AI agent can use. Each fact in the feed has a word-for-word quote from its source page, and code checks the quote. The feed gives the facts and how sure each one is. The agent selects for the guest.

```text
registry.json -> fetch -> render -> hash -> extract (model) | verify (code) -> update -> SQLite -> read -> MCP
```

## Read this, in this order

1. `docs/design.md`: the design write-up.
2. `docs/assumptions.md`: each belief that I tested, and what the test showed.
3. `docs/model.md`: the findings that changed the design, newest first.
4. `docs/acceptance.md`: what "done" is, and the status of each line.
5. `Notes/`: my pen and paper notes. `docs/handover.md`: what the prototype taught.
6. `CLAUDE.md`: how I work with Claude on this project. `runs/runs.md`: the measured cost of each run.
7. `research/acceptance/`: the tests of the agent's answers (`comparison.md` is the summary).

## Run it in three steps (no key, no cost)

The repository holds the database of the real run of 2026-11-23 (`feed.db`), so you can use the feed at once.

**1. Install** (Python 3.11 or later)

```bash
# macOS or Linux
python3 -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"

# Windows (Git Bash)
python -m venv .venv && ./.venv/Scripts/python -m pip install -e ".[dev]"
```

In the commands below, `PY` is `.venv/bin/python` (macOS, Linux) or `./.venv/Scripts/python` (Windows).

**2. Check** (230 tests and the lint; exit code 0)

```bash
PY -m pytest && PY -m ruff check . && PY -m ruff format --check .
```

**3. See the feed**

```bash
PY -m feed.demo                              # the exact text that an agent gets, for a trip of 20 to 27 June 2027
PY -m uvicorn feed.web:app --port 8000       # a page at http://localhost:8000
```

On the page, "Browse the feed" uses no model and no key. "Ask the agent" calls a Claude model, so it needs the key of the next section, and each answer costs about 0.02 to 0.08 US dollars.

## Connect your own Claude to the feed

The feed is an MCP server with five read-only tools: `what_is_on`, `when_to_go`, `find`, `tell_me_more`, `what_changed`. It needs no key.

**Claude Code.** Run this one time. Use the full paths of your clone. Then start Claude Code in an empty folder, so that it has only the feed.

```bash
claude mcp add event-feed --scope user \
  --env FEED_DB="/full/path/to/repo/feed.db" \
  --env FEED_REGISTRY="/full/path/to/repo/registry.json" \
  -- "/full/path/to/repo/.venv/bin/python" -m feed.mcp_server
```

**Claude Desktop.** Add this block to `claude_desktop_config.json` and start the app again.

```json
{
  "mcpServers": {
    "event-feed": {
      "command": "/full/path/to/repo/.venv/bin/python",
      "args": ["-m", "feed.mcp_server"],
      "env": {
        "FEED_DB": "/full/path/to/repo/feed.db",
        "FEED_REGISTRY": "/full/path/to/repo/registry.json"
      }
    }
  }
}
```

On Windows the command is `C:/full/path/to/repo/.venv/Scripts/python.exe`.

Questions to try: "What is on in Hermanus for my clients from 20 to 27 June 2027?", "When is the best time to go?", "Is there a weekly market?", "How sure is the date of the FynArts Festival?".

## Collect the data again (needs a key; costs money)

```bash
echo "ANTHROPIC_API_KEY=your-key" > .env     # git ignores this file
PY -m feed.ingest
```

- It fetches the 10 pages of the registry, slowly, and calls `claude-haiku-5-5` one time for each page that changed.
- Measured: the first run cost 0.064780 US dollars. A second run on unchanged pages made 0 model calls.
- It updates `feed.db` and adds one line to `runs/runs.md`. An item is updated, not added a second time, and nothing is deleted.
- A page that fails does not stop the run; the report names it.

## Deploy

| Part | State | How |
|---|---|---|
| The feed on one machine | Built | Install, then run the MCP server or the page as above |
| The weekly collection | Built as a command | Schedule `PY -m feed.ingest` one time each week. Example for cron: `0 5 * * 1 cd /path/to/repo && .venv/bin/python -m feed.ingest >> runs/ingest.log 2>&1` |
| The feed at a URL, for an agent that is not on this machine | Not built | The MCP server speaks over stdio only. It needs the HTTP transport of the `mcp` package, a host, and access control. The read code needs no change: it only reads `feed.db` |
| A second town | Not built | Add a place and its sources to `registry.json`. No pipeline code names Hermanus |

Settings: `FEED_DB` (default `feed.db`), `FEED_REGISTRY` (default `registry.json`), and `ANTHROPIC_API_KEY` for the ingest and for "Ask the agent".

## Map of the code

| File | What it does |
|---|---|
| `registry.json` | The town as data: sources and pages, towns, categories, the wording of the traveller bar, sources not collected |
| `feed/fetch.py`, `feed/render.py` | One page of the registry to its visible text (HTML, a WordPress page, the newest PDF) |
| `feed/extract.py` | The only model step: the prompt and the answer format |
| `feed/verify.py` | The gate: quote on page, value in quote, real date |
| `feed/update.py` | Stores an item or updates the same item; change rows; never deletes |
| `feed/ingest.py` | The run: fetch, hash, extract, update; the report and the cost line |
| `feed/schema.sql`, `feed/store.py` | SQLite: six tables |
| `feed/read.py` | The five read operations and the fixed text |
| `feed/mcp_server.py` | The five tools and the server instructions for an agent |
| `feed/web.py`, `feed/demo_page.html`, `feed/agent.py`, `feed/demo.py` | The demo page, the demo agent and the command-line demo |
| `tests/` | 230 tests. The hand cases of the design are tests |
| `evals/` | Saved real pages, hand-case fixtures, and a sample of 20 stored items to check by hand |
| `research/` | Each research test with its saved model answers; `research/acceptance/` has the tests of the agent |

## What is not built

One event with two different titles from two sources is two cards. A moved date shows as an added date. `cancelled`, standing experiences (shark cage diving, wine estates), Quicket, a hosted server and a second town are designed and not built. The list is in `docs/design.md`, "Built, and not built".
