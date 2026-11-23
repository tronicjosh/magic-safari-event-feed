# Hermanus event feed

A homework project for Magic Safari: a feed of events and seasons near Hermanus that a travel designer's AI agent can use. Each fact in the feed has a word-for-word quote from its source page, and code checks the quote.

## Read this, in this order

1. `docs/design.md`: the design write-up.
2. `docs/assumptions.md`: each belief that I tested, and what the test showed.
3. `docs/model.md`: the findings that changed the design, in order.
4. `docs/acceptance.md`: what "done" is, and the status of each line.
5. `Notes/`: my pen and paper notes. `docs/handover.md`: what the prototype taught.
6. `CLAUDE.md`: how I work with Claude on this project. `runs/runs.md`: the measured cost of each run.

## Run it

```bash
python -m venv .venv && ./.venv/Scripts/python -m pip install -e ".[dev]"
./.venv/Scripts/python -m pytest && ./.venv/Scripts/python -m ruff check .   # 229 tests
./.venv/Scripts/python -m feed.ingest        # needs ANTHROPIC_API_KEY in .env; about 0.07 US dollars; writes feed.db
./.venv/Scripts/python -m feed.demo          # the text that an agent gets for 20 to 27 June 2027; no model
./.venv/Scripts/python -m feed.mcp_server    # the MCP server over stdio, for Claude
./.venv/Scripts/python -m uvicorn feed.web:app --port 8000   # a demo page; "Ask the agent" calls a model
```

## The path

```text
registry.json -> fetch -> render -> hash -> extract (model) | verify (code) -> update -> SQLite -> read -> MCP
```

| File | What it does |
|---|---|
| `registry.json` | The town as data: sources, towns, categories, the bar wording |
| `feed/extract.py` | The only model step: the prompt and the answer format |
| `feed/verify.py` | The gate: quote on page, value in quote, real date |
| `feed/update.py` | Stores an item or updates the same item; change rows; never deletes |
| `feed/read.py` | The five read operations and the fixed text |
| `feed/mcp_server.py` | The tools and the server instructions for an agent |
| `evals/`, `research/` | Saved pages, saved model answers, hand cases, the sample check |
