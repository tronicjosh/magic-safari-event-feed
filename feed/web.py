"""A demo page on localhost: the four read operations, with the text exactly as an agent gets it.

Run: python -m uvicorn feed.web:app --port 8000      then open http://localhost:8000
The database is FEED_DB (default feed.db), opened read-only. No model, no request to a source.
"""

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from feed import read

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
</style>
</head>
<body>
<main>
  <div class="eyebrow">Demo &middot; Hermanus &middot; read-only</div>
  <h1>What is on, and how sure are we?</h1>
  <p class="lead">This page calls the same four operations that a travel designer's agent calls.
     The text below is the answer of the feed, with no change and no model.</p>

  <div class="tabs" role="tablist">
    <button data-tab="on" aria-selected="true">What is on</button>
    <button data-tab="go" aria-selected="false">When to go</button>
    <button data-tab="more" aria-selected="false">Tell me more</button>
    <button data-tab="changed" aria-selected="false">What changed</button>
  </div>

  <form id="on">
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
  <pre id="out">Choose dates and select Show.</pre>
</main>
<script>
const paths = {on: "what_is_on", go: "when_to_go", more: "tell_me_more", changed: "what_changed"};
const hints = {
  on: "The trip has dates. Each item in the window, in four groups. Select an id to see its proof.",
  go: "The trip has no dates yet. Seasons and yearly items, by month.",
  more: "The full card of one or more items: each fact with its quote from the page.",
  changed: "The designer says when they last looked. New items and changes since that date."
};
const months = ["January","February","March","April","May","June","July","August","September",
                "October","November","December"];
for (const select of document.querySelectorAll("select")) {
  months.forEach((name, index) => select.add(new Option(name, index + 1)));
  select.value = select.name === "from_month" ? 1 : 12;
}
const out = document.getElementById("out"), hint = document.getElementById("hint");
function escapeHtml(text) {
  return text.replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
}
function show(tab) {
  for (const form of document.querySelectorAll("form")) form.hidden = form.id !== tab;
  for (const button of document.querySelectorAll(".tabs button"))
    button.setAttribute("aria-selected", button.dataset.tab === tab);
  hint.textContent = hints[tab];
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
  form.addEventListener("submit", event => { event.preventDefault(); ask(form.id); });
out.addEventListener("click", event => {
  const id = event.target.dataset.id;
  if (!id) return;
  document.querySelector("#more input").value = id;
  show("more"); ask("more");
});
show("on"); ask("on");
</script>
</body>
</html>
"""
