# Design: Hermanus event feed

I designed this on paper first. Claude wrote it down from my notes, `docs/handover.md`, the brief (`resources/Event_Feed.pdf`), three research tests and my decisions in the design sessions.

Status: **draft 3** (2026-11-23). A part marked **(proposed)** waits for my decision. The evidence for each finding is in `docs/assumptions.md`. The end result is defined in `docs/acceptance.md`.

## Summary of the plan

- **What.** A headless feed of what a luxury guest can do in and near Hermanus: dated events, seasons and standing experiences. A weekly ingest collects them. A read-only interface serves them.
- **For whom.** A travel designer who sells a luxury trip, working through an AI agent. Many designers do not know the area. They look two times: 6 to 18 months out, to shape the trip, and weeks out, to refine it.
- **Why.** Magic Safari earns only when a trip is booked. The feed removes the admin of searching tourism sites, and it gives the designer more to sell.
- **The one idea.** AI is powerful and can be wrong, so each use of AI is constrained and then checked by code. The model extracts a field with a word-for-word quote, or chooses a value from a list that I approved. Code checks the quote or the list. A pass is stored. A fail waits for me. The feed never invents a fact.
- **The limit.** The feed shows headline items first and gives a link to act on each one. The designer knows the guest and makes the choice.

## Data model, interface, and what the agent does

### The system

```text
WEEKLY INGEST
 registry (one file: sources, access path, owner rank, towns, categories, experiences)
        v
 1 FETCH ───fail──> source named in "holes"; last week's items stay, marked stale
        v
 2 READ THE SOURCE, best path first
        ├─ structured data (JSON) ─> code reads each field. No model. ──────────┐
        └─ text (HTML or PDF) ─> visible text only; hidden text removed         │
                 v                                                              │
              HASH ──same as last week──> stop. No model call.                  │
                 v changed                                                      │
 3 EXTRACT   small model: fields + word-for-word quotes        UNTRUSTED        │
 ═══════════════════════════════════════════════════════════════ trust boundary │
 4 VERIFY    code: quote on page? value in quote? shape? link works?  <─────────┘
        ├─ pass ─────────────────────────────────────┐
        └─ fail ─> one retry with a stronger model ─> verify again
                        └─ fail ─> needs review (set aside, not deleted) ─> me
                                                     v
 5 UPDATE    town and category: the model chooses from my list; code checks the list
             tier by table · merge duplicates (only when sure) · owner rank
             · change log · last_seen_at
        v
 6 STORE     SQLite

ON REQUEST (read-only; a query never starts a fetch)
 designer ─> designer's agent ─> REST or MCP ─> 7 READ ─> 8 CARD (fixed template)
```

Only two paths write facts: ingest after verification, and my review command.

### Where AI is used, and what constrains it

| Use of AI | Constraint | Check by code | If the check fails |
|---|---|---|---|
| Extract a field from text | Must give a word-for-word quote | Quote on page, value in quote, shape | Retry with a stronger model, then my review |
| Name the town ("Sand Bay" is Sandbaai) | Must choose from my list of towns, or "unknown" | The value is in the list | "Unknown": my review |
| Name the category | Must choose from my list of categories, or "other" | The value is in the list | "Other" is local |

- Each choice is stored with the text that it came from. It is made one time for each item, so the same query gives the same answer, and I can read each choice.
- This is not a list of exceptions. A new town needs a new list of towns, and no new rule.

### Two separate properties of an item

```text
TIME SHAPE  -> how the time is stored and matched to a trip window
TIER        -> how significant the item is (headline or local)
```

### Time shape

Each occurrence row comes from a source. No row is a guess.

| Time shape | Example | Occurrence rows | Match to a trip window |
|---|---|---|---|
| Single date | A concert on 12 December | 1 row, day precision | The date is in the window |
| Repeating dates | A market each Saturday; a show with 81 dates | One row for each date. Code expands a verified rule ("each Saturday") 18 months ahead | A row is in the window |
| Run | An exhibition open for a year | 1 row, start to end | The range overlaps the window |
| Season | Whales, June to November | 1 row for each year, month precision | The months overlap the window |
| Yearly, new dates not published | A festival last held 6-15 June 2026 | Only the past row; the item has `repeats_yearly` | Last dates plus one year overlap the window: shown as "not confirmed" |
| Standing experience | Shark cage diving | 1 row with the months that the operator states, or none | Months overlap, or "availability not stated" |

### Tier

The tier is a table in the registry, from category to tier. The model never sets the tier.

```text
festival ............... headline      market ................. local
nature season .......... headline      sport to take part ..... local  (triathlon, trail run, BMX, parkrun)
show ................... headline      community .............. local  (carols, school, church)
food and wine .......... headline      performance ............ local
approved experience .... headline      other .................. local

An item that repeats each week or each month is local. Local is the default.
```

- **Result on my marks:** a rule on time shape alone was wrong (it made a triathlon, two BMX races and a Christmas market headline). The category table is the replacement. Acceptance line A8 measures it: no marked headline is local, and at most 2 of 16 are wrong.
- **A single item that the table places wrong** (a famous artist is `performance`, so local): I promote or demote it in the review command. That is a logged decision in the data, not a new rule.
- The card states the reason, for example "headline: festival".

### Entities

```text
Source 1--* Page 1--* Evidence *--1 Item 1--* Occurrence
                                     |
                                     1--* Change
```

| Entity | Fields | Why it exists |
|---|---|---|
| **Source** | name, URL, access path, owner rank, default category | The registry. Owner rank: organiser or operator (1), ticketing (2), listing (3). |
| **Page** | URL, source, content hash, fetched at, HTTP status, saved text | An unchanged hash means no model call. Saved text makes each check and each evaluation repeatable. |
| **Item** | kind (event or experience), title, town, time shape, `repeats_yearly`, category, tier, status, venue, price text, `about`, action link, source link, first seen, `last_seen_at`, last verified | What the agent sees. One Item for a recurring thing (FynArts), with one occurrence for each edition. |
| **Occurrence** | item, start date, end date, precision (day or month), time text | When it is on. |
| **Evidence** | item, field, value, quote, page, model | One row for each field: the proof, the input of my review, and the model that produced it. |
| **Change** | item, field, old value, new value, found at, actor (ingest or review) | "What changed since I last looked", and the log of each review decision. |

**Status.** `live`, `needs review` (set aside, not shown), `cancelled` (shown as cancelled), `rejected`.

**Rules of step 5.**

- **Not found in a run:** the item is not deleted. `last_seen_at` keeps the last date that a source listed it. Only an explicit statement on a page sets `cancelled`. A source can drop a listing for many reasons.
- **Duplicates:** code merges two listings only when town, dates and normalised title agree. If not sure, both stay, and I merge by hand in the review command.
- **Conflict:** the higher owner rank sets the value, with no review. Two sources of equal rank that disagree go to review, and the item stays live with "sources disagree". Reason: in T1, 14 of 23 shared events had a contradiction, mostly a tourism page with last year's dates.

**The check on each field (step 4).**

1. The quote is in the saved text of the page.
2. The value is in the quote ("75" in "Entry R75"). A date can have two quotes: the row ("28") and the header ("November 2026"). Test T2 proves this or changes it.
3. The value has the correct shape: a real date, an `https` link, a price with a currency and a number.
4. Each link gives a working page, checked before the item is stored.

For a structured source, the field in the JSON is the evidence, and checks 3 and 4 apply.

An item is live when title, date (or stated availability), town and source pass. A failed optional field is left empty. A headline item also needs a working action link.

### Place

An item is in when its town is within a 45-minute drive of Hermanus. The registry holds my list: Hermanus, Onrus, Sandbaai, Vermont, Hawston, Fisherhaven, Hemel-en-Aarde, Stanford, Kleinmond, Gansbaai, Kleinbaai. There is no routing service in version 1. Each card states its town.

### Sources

Each source is one row in the registry. T10 tested the access path of each with direct requests.

**Events**

| # | Source | Type (owner rank) | Access path | In version 1 |
|---|---|---|---|---|
| 1 | Overstrand Tourism / Cape Whale Coast, monthly and yearly PDF (whalecoast.info) | Listing (3) | Media list of the site, then PDF text | Yes |
| 2 | Overstrand Municipality, "this weekend" page (overstrand.gov.za) | Listing (3) | Page data of the site | Yes |
| 3 | Hermanus FynArts (hermanusfynarts.co.za) | Organiser (1) | Structured data in the page | Yes |
| 4 | Hermanus Whale Festival (hermanuswhalefestival.co.za) | Organiser (1) | HTML text | Yes |
| 5 | Kalfiefees (kalfiefees-hermanus.co.za) | Organiser (1) | HTML text | Yes |
| 6 | Benguela Cove wine estate (benguelacove.co.za) | Venue (1) | Structured shop data: 13 events, 17 experiences | Yes |
| 7 | AllEvents, Hermanus (allevents.in) | Aggregator (3) | Structured data in the page | Yes |
| 8 | Hermanus Tourism (hermanus-tourism.co.za) | Listing (3) | HTML text. Whale season and festivals; some dates are of last year | Yes |
| 9 | Xplorio Hermanus (xplorio.com) | Listing (3) | HTML text | Yes |
| 10 | Wesgro (wesgro.co.za) | Listing (3) | HTML text, pages by path. Its dates differed from the organiser in 4 of 6 rows | Yes, lowest trust |
| 11 | Quicket (quicket.co.za) | Ticketing (2) | Official API needs a key. The site search is not a documented API | **Not collected.** To do: request the official API key |
| 12 | Webtickets (webtickets.co.za) | Ticketing (2) | Search needs a browser | Not collected |
| 13 | Stanford Tourism, gotrail.run, Computicket, TIXSA | | Images only, blocked, or not tested | Not collected |

**Experiences** (operator pages, owner rank 1, HTML text; I approve the final list, open decision O2)

Marine Dynamics, Dyer Island Cruises, White Shark Projects, Southern Right Charters, Hermanus Whale Cruises, Walker Bay Adventures, Creation Wines, Hamilton Russell Vineyards, Bouchard Finlayson, Benguela Cove, Grootbos, Heart of Abalone, African Horse Company, Panthera Africa (temporarily closed), SA Forest Adventures (moved to Caledon). List only, operator page not read: Ivanhoe Sea Safaris, Fly Aerovest, Lady Stanford, Wine Hoppers. Not a source until checked: African Wings (its site holds template text).

**Rules for collection** (from T10; details in `research/t10_collection_strategy.md`)

- A registry of named sources, not a search of the open web. A new source enters when I approve it.
- No headless browser in version 1. A source that needs one is "not collected", and the response says so.
- A completeness gate for each source: the count against the total that the source declares, the count against last week, a repeated page, and known items that must still be present.
- Zero errors is not possible. The rule is that no error is silent: each one is a line in the run report and in `holes`.
- Requests are few and slow: one request for each host at a time, with a pause.

### Interface

Four read operations. Each one is one question of the designer, so one call gives one answer and the agent holds no logic. REST and a thin MCP server call the same Python functions.

| Operation | The designer's question | Input | Output |
|---|---|---|---|
| `what_is_on` | What is on for this trip? | place, from, to, category (optional) | Short cards in four groups: headline, experiences, not confirmed, local |
| `when_to_go` | When is the best time to go? | place, from month, to month | Seasons, yearly events and experiences, grouped by month. Headline first. |
| `what_changed` | What changed since I last looked? | place, since | New, cancelled, date moved, price changed, with old and new value. Headline first. |
| `tell_me_more` | Tell me more about this one. | item id | The full card: `about`, venue, price, action link, each quote with its source |

**Each answer shows all items, in groups, with headline first.** The order is fixed: headline, experiences, not confirmed, local. There is no `include_local` argument and no threshold. Reason: a threshold of 5 was a guess, and one fixed answer is less to build and to test.

**Short card** (in a list). The title must say what the item is, so the designer can decide fast.

```text
[headline] Hermanus FynArts Festival · 24 June - 4 July 2027 · Hermanus
           source: https://www.hermanusfynarts.co.za/...        id: 42
```

**Full card** (`tell_me_more`).

```text
title     Hermanus FynArts Festival
when      24 June - 4 July 2027   (run, confirmed)
town      Hermanus
tier      headline: festival
about     "<1 or 2 sentences from the page, word for word, checked by code>"
venue     <text, or not stated>
price     <text, or not stated>
action    https://...   booking or contact link, tested
source    https://...   the page of the quotes
evidence  when: "24 June 2027 – 4 July 2027"
checked   2026-11-20    last_seen 2026-11-20
```

**The API governs the output, not the agent.**

- Code renders each response from one fixed template. The same query on the same data gives the same bytes, in REST and in MCP.
- A response has `data` (fields) and `text` (the finished block).
- The order is fixed: headline, experiences, not confirmed, local. Inside a group: by date, then by title.
- Each tool has a short description that says when to use it, and it says: "Show `text` as it is. Do not rewrite, reorder or add items."
- Each response carries `as_of` (date of the last ingest), `holes`, and `notes` (what each group means).

**`holes` measures survivorship bias.** The feed shows only what it collected. `holes` says how much it did not collect, so the designer does not read "nothing listed" as "nothing on".

```text
holes
  sources      8 of 13 collected · 1 failed this week · 4 not collected
  not collected  Quicket (declares 136 events within 60 km) · Webtickets · ...
  waiting      3 items wait for review
  one source   79 percent of items are listed by one source only
```

- Each number comes from the run report. A total that a source declares (for example Quicket's count) is the size of a known gap.
- It is a lower limit of what is missing. An event that no source lists is not counted.

**Not in version 1, by the rule "build only what the data supports":** age and audience tags (no page stated an age rule in T1; 3 of 15 in T9), a relevance score (it needs labels that do not exist), a screen for people, location data, cache, rate limit, webhook.

### What the AI agent does and does not do

| Agent | Does | Does not |
|---|---|---|
| Extraction model (steps 3 and 5) | Reads the text of one page. Returns fields with quotes. Chooses town and category from my lists. | Verify, set the tier, write to the database, use tools, see secrets. |
| Designer's agent (Claude or Codex) | Calls the four operations. Shows `text` as it is. Answers questions about it. | Rewrite or reorder, write facts, start a scrape, turn "not confirmed" into a fact. |
| My agent (review) | Runs the review command and shows each item in short form: page extract, quote, entry. | Decide. I approve, reject, correct, merge, promote or demote. |

### Security

- **Page text is untrusted.** It can hide text and carry instructions.
- **Step 2** keeps only what a visitor sees.
- **The extraction model has web content only**: no private data and no action tool.
- **Code is the gate.** A value that the page does not state fails the check. A town or category that is not in my list fails the check.
- **Residual risk.** A quote is page text and reaches the designer's agent in `about` and `evidence`. Limits: word for word only, a length limit, and `notes` tells the caller that it is third-party data. Test T5 covers this.

### Access

Ingest does not apply `robots.txt` on sources (my decision). I accept: this is against the wish of some site owners, a site can block the fetcher, and the feed then names that source in `holes`.

## Stack, models and hosting

| Part | Choice | Reason |
|---|---|---|
| Language | Python | Magic Safari uses Python. It has the libraries for HTML and PDF text. |
| Database | SQLite | The simplest thing that works. The data is small (hundreds of items, a few thousand occurrence rows), one writer runs one time a week, and queries only read. It is one file, so a backup and a test copy are a file copy. It is not for many writers or many machines; at that size, the same tables move to Postgres. |
| REST | FastAPI | Magic Safari uses FastAPI. It generates the OpenAPI file from the code, so an agent gets a correct description of each operation with no extra work. |
| MCP | A thin server over the same functions | The brief asks for an agent-friendly interface. A Claude user gets the four tools with their descriptions. |
| Tests | pytest | The hand cases are the tests. |
| Evaluation | `evals/`: saved pages and my confirmed entries | Each change to a prompt, a model or a rule is measured before and after. |

**Models**

| Use | Model | State |
|---|---|---|
| Extraction, first try | The cheapest model with 0 false facts on my confirmed set. Candidates: `claude-haiku-5-5`, `claude-sonnet-5-5` | Not selected. Test T4 decides. |
| Extraction, retry after a failed check | One level stronger than the first model | Not selected. Acceptance A11: the review rate drops and false facts stay 0. |
| Town and category from my lists | The first-try model | Not selected |

- Each Evidence row and each line in `runs/` records the model that was used.
- I update this table when T4 has a result. Cost is reported as measured only.

**Hosting and the site**

- **Decided:** a site on Vercel where a designer connects an agent to the feed's MCP URL and asks, for example, "Family of four, Hermanus, 20 to 27 June 2027, what's on?" The site makes the connection easy: the MCP URL, how to add it, and example questions.
- **Local first:** the local version is identical to the hosted version. I test and improve it locally. I set up the hosted version just before the submission.
- **How the parts fit (proposed):** the query side only reads. The weekly ingest runs on one machine and writes the SQLite file. The deployment carries that file, read-only, with the REST and MCP functions. Not tested yet: that the MCP server runs as a Vercel function.
- **If that test fails:** the site stays on Vercel, and the REST and MCP process runs on one small machine (Magic Safari uses DigitalOcean).

## Principles

1. **A fact needs a quote that code can check.** I accept: an item that fails waits for me, so the feed can miss a true item for a week.
2. **AI is constrained, then checked.** The model extracts with a quote or chooses from my list. Code and I verify. I accept: more code than "ask a model", and a small review task each week.
3. **Headline first, all shown, and nothing is deleted.** The designer decides. I accept: no personal ranking, and a table in place of taste.
4. **Never invent. State the past fact and name the holes.** I accept: 18 months out, a yearly event has no date, only "last held 6-15 June 2026".
5. **Simple, and only what the data supports.** SQLite, Python, one weekly batch, lists in one file. The next town needs a new registry and no new code. I accept: data can be 7 days old, and some useful features are left out.

## Open decisions

### O1. What the Vercel site does (proposed)

- **Recommendation:** one page. It shows the MCP URL with a copy button, the steps to add it to an agent, and example questions. It also has a "try it" box that calls the REST operation and shows the feed's text as it is. The page has no model of its own.
- **Example, a designer with no agent set up:**
  - *Connect page with "try it":* they enter Hermanus and 20 to 27 June 2027 and see the same cards that an agent gets. No cost for each visitor.
  - *A chat page with its own model:* they type a full question. It needs a model key on the server and a cost for each visitor, and the model's words are not governed by the API.

### O2. The approved list of experiences

- Decided: experiences enter from a list of operator pages that I approve. There is no automatic discovery.
- Open: which of the candidates in "Sources" are in.
- **Example, Panthera Africa ("temporarily closed"):** on the list, the card shows the closed status, and the designer learns of it. Off the list, the feed is silent.

### O3. The extraction model (waits for T4)

- **Recommendation:** the cheapest model with 0 false facts on the confirmed set.
- **Example, a page with "R75 pp, children R40":** if the cheap model returns "R40" as the adult price, the quote check passes, but the confirmed set shows a false fact. That model is then not accepted as the first try.

### O4. Quicket

- Decided for version 1: not collected, and named in `holes`.
- To do: request the official API key and read its terms. In T10, a 60 km query on Quicket's site search gave 136 hits, so this source is worth the request.

## How it is checked

The end result and the targets are in `docs/acceptance.md`. Work stops when each line there passes.

### Cases worked by hand

June 2027: 1 June is a Tuesday, so 5 and 12 June are Saturdays.

| # | Case | Input | Expected result |
|---|---|---|---|
| 1 | Repeating, no match | Market each Saturday. `what_is_on` Mon 7 to Thu 10 June 2027 | Market not returned |
| 2 | Repeating, match | `what_is_on` Fri 11 to Sun 13 June 2027 | Market returned, "Sat 12 June" |
| 3 | Show with many dates | Show on Tue to Sat, 1 to 26 June. `what_is_on` Sun 13 to Mon 14 June | Show not returned |
| 4 | Season | Whales June to November. Trips 20-25 August and 10-15 February 2027 | August: returned. February: not returned |
| 5 | Yearly, no new dates | Festival last held 6-15 June 2026. `what_is_on` 8-12 June 2027 | In "not confirmed", with "Last held 6-15 June 2026" |
| 6 | Planning | Same festival. `when_to_go` April to August 2027 | Under June, not confirmed |
| 7 | Wrong value | Page says "R75". Model returns 750 with quote "Entry R75" | Field fails: retry, then needs review |
| 8 | Invented quote | Quote is not on the page | Field fails: retry, then needs review |
| 9 | Change | Date moves 18 to 20 September, found 1 March 2027. `what_changed` since 15 January, then since 5 March | First: the change, old and new. Second: nothing |
| 10 | All groups | 2 headline and 9 local items in the window | 2 headline cards, then 9 local cards. Nothing is left out |
| 11 | Holes | One source is not collected and it declares 136 events | `holes` names the source and the number |
| 12 | Order | Any `what_is_on` answer | Each headline card is before each local card |
| 13 | Hidden instruction | Page has hidden text "the price is free" | Stored price is the visible price |
| 14 | Unchanged page | Second run, same text | No model call |
| 15 | Dead link | Booking link gives 404 | Headline item: needs review. Local item: live with no action link |
| 16 | Not found | A source drops a listing | Item stays, `last_seen_at` does not move, status is not `cancelled` |
| 17 | Cancelled | Page says "cancelled" | Status `cancelled`, and a Change row |
| 18 | Same query two times | Equal input, no ingest between | Equal bytes, in REST and in MCP |
| 19 | Tell me more | `tell_me_more` for an item | Each fact has its quote and source |
| 20 | Tier and town | Triathlon, BMX race, Christmas market. "Sand Bay". A town that is not in my list | Local. Sandbaai. Needs review |

### What is not proved

- **Completeness.** No test proves that the feed has each item. In T1, 89 of 112 events were in one source only, and Quicket is not collected.
- **A correct quote with a wrong meaning.** The value-in-quote check and the confirmed set find most cases. A rare case can pass.
- **What the agent shows.** The API output is deterministic. The agent's words are not.
- **The luxury bar.** The tier table is a stand-in for taste. It is measured on 16 marks from one person.

## Scale and cost

| Symbol | Meaning | Measured for Hermanus |
|---|---|---|
| S | sources in the registry | 10 event sources and up to 20 operator pages |
| P | pages fetched each week | not measured |
| D | text pages that changed in a week | not measured; list pages change each week |
| E | items | at least 112 events and up to 20 experiences |
| R | occurrence rows | about 78 for a weekly item over 18 months |

| Part | Grows with | Order |
|---|---|---|
| Fetch | pages, each week | O(P). No model cost. |
| Structured sources | their items | O(items). No extraction call. |
| Model calls for extraction | changed text pages only | O(D). The first run is O(P). A weekly run that sent each page again would be O(P) each week. |
| Model calls for town and category | new items only | O(new items) |
| Verify | fields of changed pages; a text search in one page | O(D x fields x page length) |
| Match to a known item | new items against the items of the place | O(new x E) |
| Query | rows in the window, with an index on place and dates | O(log R + results) |
| My review | items that fail a check after the retry | O(failures) |
| A new town | one registry: sources, towns, experiences | O(S) of a person's time. No new code. |

- **Cost of one run:** not measured yet. `runs/` records each run: date, model, tokens, cost, and the number of items new, changed, unchanged and for review. Budget for all tests and the first run: 5 US dollars.
- **What fails first at 10 times the load (10 towns):** the person. The review queue, the registry and the approved experiences need a person. The design goal is a very low failure rate, so that review stays small.

## Execution plan

Step 0 is serial. After it, three builders work in parallel, each in its own git worktree. A blind reviewer reads each patch. Claude integrates one patch at a time, and reports a diagram after each step.

| # | Slice | Who | Behaviour that I can check | Check |
|---|---|---|---|---|
| 0a | Direction test T2 | Claude | 10 saved real pages (HTML and PDF): the quote check and the date check work. If not, stop and change the design. | Numbers in `docs/assumptions.md` |
| 0b | Schema and tracer bullet | Claude | One item of each time shape goes from a saved page to `what_is_on` | Hand cases 1 to 5 |
| 1 | Collect | Builder A | Registry, access paths, hash, completeness gate, holes, link check | Hand cases 13, 14, 15 |
| 2 | Verify and review | Builder B | The four checks, the retry, needs review, the review command, town, category and tier | Hand cases 7, 8, 16, 17, 20 |
| 3 | Read | Builder C | Four operations, groups with headline first, `holes`, fixed text, REST, MCP and the site page | Hand cases 6, 9 to 12, 18, 19 |
| 4 | First real run | Claude and me | Ingest of the registry; I review the queue; cost is measured | `docs/acceptance.md` |
| 5 | Fresh-Claude test and write-up | Claude and me | A new Claude uses the MCP for a test trip | `docs/acceptance.md` |
