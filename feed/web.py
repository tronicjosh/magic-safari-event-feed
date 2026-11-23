"""A demo page on localhost: ask an agent, or call the four read operations directly.

Run: python -m uvicorn feed.web:app --port 8000      then open http://localhost:8000
The database is FEED_DB (default feed.db), opened read-only. No request to a source.
"Ask the agent" calls a Claude model with only the four tools of the feed (feed/agent.py);
each answer costs money, and the page shows the measured cost. The other tabs use no model.
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


def _run(operation, *values) -> dict:
    registry_path = Path(os.environ.get("FEED_REGISTRY", "registry.json"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    place = next(iter(registry["places"]))
    path = Path(os.environ.get("FEED_DB", "feed.db")).resolve()
    try:
        db = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
        try:
            arguments = (place, *values) if operation is not read.tell_me_more else values
            return {"text": operation(db, registry, *arguments)["text"]}
        finally:
            db.close()
    except (ValueError, OverflowError, sqlite3.Error) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"not a date: {text}") from error


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
        raise HTTPException(
            status_code=400, detail="ids are numbers, for example: 151 11"
        ) from error
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
        raise HTTPException(
            status_code=502, detail=f"no connection to the model: {error}"
        ) from error
    _spent["usd"] += result["cost_usd"]
    return result | {"spent_usd": round(_spent["usd"], 6)}


@app.post("/api/reset")
def reset(question: Question) -> dict:
    _sessions.pop(question.session, None)
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hermanus event feed</title>
<style>
  :root { --bg:#EAECEE; --card:#F7F8F8; --line:#D5D9DD; --ink:#292827; --soft:#5C5954;
          --sage:#7A8274; --moss:#5A6353; --deep:#2C3628; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:16px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 980px; margin: 0 auto; padding: 40px 16px 64px; }
  .eyebrow { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--sage); }
  h1 { font:500 34px/1.15 Georgia, "Times New Roman", serif; color:var(--deep); margin:6px 0 8px; }
  p.lead { color:var(--soft); margin:0 0 28px; max-width: 62ch; }
  .tabs { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px; }
  .tabs button { border:1px solid var(--line); background:transparent; color:var(--moss);
                 padding:8px 14px; border-radius:999px; font:inherit; font-size:14px; cursor:pointer; }
  .tabs button[aria-selected="true"] { background:var(--deep); border-color:var(--deep); color:#fff; }
  form { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px;
         display:flex; flex-wrap:wrap; gap:12px; align-items:flex-end; }
  label { display:flex; flex-direction:column; gap:4px; font-size:11px; letter-spacing:.08em;
          text-transform:uppercase; color:var(--sage); }
  input, select { font:inherit; font-size:15px; padding:8px 10px; border:1px solid var(--line);
                  border-radius:8px; background:#fff; color:var(--ink); min-width: 150px; }
  form > button { background:var(--moss); color:#fff; border:0; border-radius:8px; padding:10px 18px;
                  font:inherit; cursor:pointer; }
  form > button:hover { background:var(--deep); }
  .hint { color:var(--soft); font-size:13px; margin:10px 2px 18px; }
  pre { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px;
        margin:0; overflow-x:auto; white-space:pre-wrap; word-break:break-word;
        font:13px/1.55 ui-monospace, "Cascadia Mono", Consolas, monospace; color:var(--ink); }
  pre a { color:var(--moss); }
  pre .id { background:#E6E9E2; color:var(--deep); border-radius:4px; padding:0 4px; cursor:pointer; }
  .error { color:#8a2f2f; }
  [hidden] { display:none !important; }
  #chat { display:block; }
  #chat textarea { width:100%; min-height:64px; font:inherit; padding:10px; border:1px solid var(--line);
                   border-radius:8px; resize:vertical; }
  #chat .row { display:flex; flex-wrap:wrap; gap:12px; align-items:flex-end; margin-top:10px; }
  #chat button { background:var(--moss); color:#fff; border:0; border-radius:8px; padding:10px 18px;
                 font:inherit; cursor:pointer; }
  #chat button.plain { background:transparent; color:var(--moss); border:1px solid var(--line); }
  #chat button:disabled { opacity:.5; cursor:wait; }
  .examples { display:flex; flex-wrap:wrap; gap:6px; margin:10px 0 0; }
  .examples button { border:1px solid var(--line); background:#fff; color:var(--soft); border-radius:999px;
                     padding:4px 10px; font:inherit; font-size:12px; cursor:pointer; }
  #talk { display:flex; flex-direction:column; gap:12px; }
  .turn { border:1px solid var(--line); border-radius:14px; padding:14px 16px; background:var(--card);
          white-space:pre-wrap; word-break:break-word; }
  .turn.you { background:#E6E9E2; align-self:flex-end; max-width:85%; }
  .turn a { color:var(--moss); }
  .meta { margin-top:10px; padding-top:8px; border-top:1px solid var(--line); font-size:12px; color:var(--soft);
          white-space:normal; }
  .meta code { background:#E6E9E2; border-radius:4px; padding:1px 5px; margin-right:4px;
               font:12px ui-monospace, Consolas, monospace; color:var(--deep); }
</style>
</head>
<body>
<main>
  <div class="eyebrow">Demo &middot; Hermanus &middot; read-only</div>
  <h1>What is on, and how sure are we?</h1>
  <p class="lead">Ask the agent as a travel designer does. The agent is a Claude model with only
     the four tools of the feed. The other tabs call each tool directly and show the answer of the
     feed with no change.</p>

  <div class="tabs" role="tablist">
    <button data-tab="chat" aria-selected="true">Ask the agent</button>
    <button data-tab="on" aria-selected="false">What is on</button>
    <button data-tab="go" aria-selected="false">When to go</button>
    <button data-tab="more" aria-selected="false">Tell me more</button>
    <button data-tab="changed" aria-selected="false">What changed</button>
  </div>

  <form id="chat">
    <textarea name="message" placeholder="What is on in Hermanus for my clients from 20 to 27 June 2027?" required></textarea>
    <div class="examples">
      <button type="button">What is on in Hermanus for my clients from 20 to 27 June 2027?</button>
      <button type="button">Same dates: a couple in their 60s who love wine and art, and do not like crowds.</button>
      <button type="button">Same dates: a family with two children of 8 and 11.</button>
      <button type="button">My clients have no dates yet. When is the best time to go to Hermanus?</button>
      <button type="button">Tell me more about the FynArts Festival. How sure is the date?</button>
      <button type="button">I last looked on 1 November 2026. What changed?</button>
    </div>
    <div class="row">
      <label>Model <select name="model">
        <option value="claude-opus-5-5">Claude Opus 5.5 (about 6 cents for each answer)</option>
        <option value="claude-sonnet-5-5">Claude Sonnet 5.5</option>
        <option value="claude-haiku-5-5">Claude Haiku 5.5 (under 1 cent for each answer)</option>
      </select></label>
      <button id="send">Ask</button>
      <button type="button" class="plain" id="new">New chat</button>
    </div>
  </form>
  <form id="on" hidden>
    <label>From <input type="date" name="start" value="2027-06-20" required></label>
    <label>To <input type="date" name="end" value="2027-06-27" required></label>
    <button>Show</button>
  </form>
  <form id="go" hidden>
    <label>From month <select name="from_month"></select></label>
    <label>To month <select name="to_month"></select></label>
    <button>Show</button>
  </form>
  <form id="more" hidden>
    <label>Item ids <input name="ids" placeholder="151 11" required></label>
    <button>Show</button>
  </form>
  <form id="changed" hidden>
    <label>Since <input type="date" name="since" value="2026-11-01" required></label>
    <button>Show</button>
  </form>
  <p class="hint" id="hint"></p>
  <div id="talk"></div>
  <pre id="out" hidden>Choose dates and select Show.</pre>
</main>
<script>
const paths = {on: "what_is_on", go: "when_to_go", more: "tell_me_more", changed: "what_changed"};
const hints = {
  chat: "Each answer is a real model call. The line under an answer shows the tools that the agent called, and the measured cost.",
  on: "The trip has dates. Each item in the window, in four groups. Select an id to see its proof.",
  go: "The trip has no dates yet. Seasons and yearly items, by month.",
  more: "The full card of one or more items: each fact with its quote from the page.",
  changed: "The designer says when they last looked. New items and changes since that date."
};
const months = ["January","February","March","April","May","June","July","August","September",
                "October","November","December"];
for (const select of document.querySelectorAll("#go select")) {
  months.forEach((name, index) => select.add(new Option(name, index + 1)));
  select.value = select.name === "from_month" ? 1 : 12;
}
const out = document.getElementById("out"), hint = document.getElementById("hint");
const talk = document.getElementById("talk"), chat = document.getElementById("chat");
let session = crypto.randomUUID();
function rich(text) {
  return escapeHtml(text)
    .replace(/(https?:\\/\\/[^\\s)<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    .replace(/[*][*]([^*]+)[*][*]/g, "<strong>$1</strong>")
    .replace(/^#{1,4} (.*)$/gm, "<strong>$1</strong>");
}
function turn(html, who) {
  const box = document.createElement("div");
  box.className = "turn " + who;
  box.innerHTML = html;
  talk.append(box);
  box.scrollIntoView({behavior: "smooth", block: "nearest"});
  return box;
}
async function send() {
  const message = chat.message.value.trim();
  if (!message) return;
  turn(escapeHtml(message), "you");
  chat.message.value = "";
  const wait = turn("The agent is working ...", "agent");
  document.getElementById("send").disabled = true;
  try {
    const response = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({session, model: chat.model.value, message})
    });
    const body = await response.json();
    if (!response.ok) { wait.innerHTML = `<span class="error">${escapeHtml(String(body.detail))}</span>`; return; }
    const calls = body.calls.map(call =>
      `<code>${escapeHtml(call.name)}(${escapeHtml(Object.values(call.input).map(v => JSON.stringify(v)).join(", "))})</code>`
    ).join("") || "no tool call";
    wait.innerHTML = rich(body.text) + `<div class="meta">Tools: ${calls}<br>` +
      `${escapeHtml(body.model)} &middot; ${body.input_tokens.toLocaleString()} tokens in, ` +
      `${body.output_tokens.toLocaleString()} out &middot; this answer ${body.cost_usd.toFixed(4)} USD ` +
      `&middot; this page since start ${body.spent_usd.toFixed(4)} USD</div>`;
  } catch (error) {
    wait.innerHTML = `<span class="error">${escapeHtml(String(error))}</span>`;
  } finally {
    document.getElementById("send").disabled = false;
  }
}
function escapeHtml(text) {
  return text.replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
}
function show(tab) {
  for (const form of document.querySelectorAll("form")) form.hidden = form.id !== tab;
  for (const button of document.querySelectorAll(".tabs button"))
    button.setAttribute("aria-selected", button.dataset.tab === tab);
  hint.textContent = hints[tab];
  talk.hidden = tab !== "chat";
  out.hidden = tab === "chat";
}
async function ask(tab) {
  const query = new URLSearchParams(new FormData(document.getElementById(tab)));
  out.textContent = "...";
  const response = await fetch(`/api/${paths[tab]}?${query}`);
  const body = await response.json();
  if (!response.ok) { out.innerHTML = `<span class="error">${escapeHtml(String(body.detail))}</span>`; return; }
  out.innerHTML = escapeHtml(body.text)
    .replace(/(https?:\\/\\/[^\\s)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    .replace(/\\bid (\\d+)\\b/g, 'id <span class="id" data-id="$1">$1</span>');
}
document.querySelector(".tabs").addEventListener("click", event => {
  if (event.target.dataset.tab) show(event.target.dataset.tab);
});
for (const form of document.querySelectorAll("form"))
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (form.id === "chat") send(); else ask(form.id);
  });
chat.message.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); }
});
document.querySelector(".examples").addEventListener("click", event => {
  if (event.target.tagName === "BUTTON") { chat.message.value = event.target.textContent; chat.message.focus(); }
});
document.getElementById("new").addEventListener("click", () => {
  fetch("/api/reset", {method: "POST", headers: {"Content-Type": "application/json"},
                       body: JSON.stringify({session, model: chat.model.value, message: ""})});
  session = crypto.randomUUID();
  talk.innerHTML = "";
});
out.addEventListener("click", event => {
  const id = event.target.dataset.id;
  if (!id) return;
  document.querySelector("#more input").value = id;
  show("more"); ask("more");
});
show("chat");
</script>
</body>
</html>
"""
