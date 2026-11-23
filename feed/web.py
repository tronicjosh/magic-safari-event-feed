"""A demo page on localhost: ask an agent, or browse the four read operations of the feed.

Run: python -m uvicorn feed.web:app --port 8000      then open http://localhost:8000
The database is FEED_DB (default feed.db), opened read-only. No request to a source.
"Ask the agent" calls a Claude model with only the four tools of the feed (feed/agent.py);
each answer costs money, and the page shows the measured cost. "Browse the feed" uses no model.
The page is feed/demo_page.html.
"""

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from feed import agent, read
from feed.env import load_env

app = FastAPI(title="Event feed demo", docs_url=None, redoc_url=None)
PAGE = Path(__file__).with_name("demo_page.html")


def _registry() -> dict:
    path = Path(os.environ.get("FEED_REGISTRY", "registry.json"))
    return json.loads(path.read_text(encoding="utf-8"))


def _open() -> sqlite3.Connection:
    path = Path(os.environ.get("FEED_DB", "feed.db")).resolve()
    return sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)


def _run(operation, *values) -> dict:
    """The data and the text of one read operation, for the first place of the registry."""
    registry = _registry()
    place = next(iter(registry["places"]))
    try:
        db = _open()
        try:
            arguments = (place, *values) if operation is not read.tell_me_more else values
            answer = operation(db, registry, *arguments)
        finally:
            db.close()
    except (ValueError, OverflowError, sqlite3.Error) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"text": answer["text"], "data": answer["data"]}


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"not a date: {text}") from error


@app.get("/api/stats")
def stats() -> dict:
    """The numbers in the header of the page."""
    registry = _registry()
    place = next(iter(registry["places"].values()))
    try:
        db = _open()
        try:
            items, below = db.execute("SELECT count(*), sum(below_bar) FROM item").fetchone()
            as_of = db.execute("SELECT max(last_seen_at) FROM item").fetchone()[0] or ""
        finally:
            db.close()
    except sqlite3.Error as error:
        raise HTTPException(status_code=400, detail=f"no database: {error}") from error
    return {
        "place": place["name"],
        "towns": len(place["towns"]),
        "items": items,
        "below_bar": below or 0,
        "sources": len(registry["sources"]),
        "not_collected": [source["name"] for source in registry.get("not_collected", [])],
        "as_of": as_of[:10],
    }


@app.get("/api/what_is_on")
def what_is_on(start: str, end: str) -> dict:
    return _run(read.what_is_on, _date(start), _date(end))


@app.get("/api/when_to_go")
def when_to_go(from_month: int = 1, to_month: int = 12) -> dict:
    return _run(read.when_to_go, from_month, to_month)


@app.get("/api/tell_me_more")
def tell_me_more(ids: str) -> dict:
    try:
        numbers = [int(part) for part in ids.replace(",", " ").split()]
    except ValueError as error:
        detail = "ids are numbers, for example: 151 11"
        raise HTTPException(status_code=400, detail=detail) from error
    return _run(read.tell_me_more, numbers)


@app.get("/api/what_changed")
def what_changed(since: str) -> dict:
    return _run(read.what_changed, _date(since))


class Question(BaseModel):
    session: str
    model: str
    message: str


_sessions: dict[str, list] = {}  # the history of each chat, in memory only: this is a demo
_spent = {"usd": 0.0}


@app.post("/api/chat")
def chat(question: Question) -> dict:
    if question.model not in agent.PRICE:
        raise HTTPException(status_code=400, detail="unknown model")
    if not question.message.strip():
        raise HTTPException(status_code=400, detail="the question is empty")
    load_env()
    history = _sessions.setdefault(question.session, [])
    kept = len(history)
    history.append({"role": "user", "content": question.message})
    try:
        result = agent.answer(anthropic.Anthropic(), question.model, history)
    except anthropic.RateLimitError as error:
        del history[kept:]
        raise HTTPException(status_code=429, detail=f"rate limit: {error.message}") from error
    except anthropic.APIStatusError as error:
        del history[kept:]
        detail = f"the model call failed ({error.status_code}): {error.message}"
        raise HTTPException(status_code=502, detail=detail) from error
    except anthropic.APIConnectionError as error:
        del history[kept:]
        detail = f"no connection to the model: {error}"
        raise HTTPException(status_code=502, detail=detail) from error
    _spent["usd"] += result["cost_usd"]
    return result | {"spent_usd": round(_spent["usd"], 6)}


@app.post("/api/reset")
def reset(question: Question) -> dict:
    _sessions.pop(question.session, None)
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE.read_text(encoding="utf-8")
