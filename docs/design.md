# Design: Hermanus event feed

Designed by: Joshua Taylor, on paper first. Written with Claude from those notes, `docs/handover.md`, the brief (`resources/Event_Feed.pdf`), three research tests and the decisions of the design sessions.

Status: **draft 2** (2026-11-23). It replaces draft 1 in full. Each part marked **(proposed)** waits for Joshua's decision. The evidence is in `docs/assumptions.md`.

## Summary of the plan

- **What.** A headless feed of what a luxury guest can do in and near Hermanus: dated events, seasons and standing experiences. A weekly ingest collects them. A read-only interface serves them.
- **For whom.** A travel designer who sells a luxury trip, working through an AI agent. Many designers do not know the area. They look two times: 6 to 18 months out, to shape the trip, and weeks out, to refine it.
- **Why.** Magic Safari earns only when a trip is booked. The feed removes the admin of searching tourism sites, and it gives the designer more to sell.
- **The one idea.** A model only extracts, and it gives a word-for-word quote for each field. Code checks each quote against the page and each value against its quote. A pass is stored. A fail waits for a person. The feed never invents a fact.
- **The limit.** The feed shows the headline items first and gives a link to act on each one. The designer knows the guest and makes the choice.

## Data model, interface, and what the agent does

### The system

```text
WEEKLY INGEST
 source registry (one file: URL, owner rank, default category, town)
        v
 1 FETCH ───fail──> source named in "holes"            (collection strategy: test T10)
        v
 2 RENDER   visible text of HTML, or PDF text. Hidden text is removed.
        v
    HASH ───same as last week──> stop. No model call.
        v changed
 3 EXTRACT  model: fields + word-for-word quotes              UNTRUSTED
 ════════════════════════════════════════════════════════════ trust boundary
 4 VERIFY   code: quote on page? value in quote?              TRUSTED
            shape correct? link works?
        ├─ pass ──────────────────────────────┐
        └─ fail ──> needs review (set aside, not deleted) ──> review command ──> Joshua
                                              v
 5 UPDATE   merge duplicates (only when sure) · owner rank sets the value
            · category and tier by rule · change log · last_seen_at
        v
 6 STORE    SQLite

ON REQUEST (read-only; a query never starts a fetch)
 designer ─> designer's agent ─> REST or MCP ─> 7 READ ─> 8 CARD (fixed template)
```

Only two paths write facts: ingest after verification, and the review command.

### Two separate properties of an item

Joshua's clarification: the time shape and the tier are different things.

```text
TIME SHAPE  -> how the time is stored and matched to a trip window
TIER        -> how significant the item is (headline or local)
```

### Time shape

Each occurrence row comes from a page. No row is a guess.

| Time shape | Example | Occurrence rows | Match to a trip window |
|---|---|---|---|
| Single date | A concert on 12 December | 1 row, day precision | The date is in the window |
| Repeating dates | A market each Saturday; a show with 81 dates | One row for each date. Code expands a verified rule ("each Saturday") 18 months ahead | A row is in the window |
| Run | An exhibition open for a year | 1 row, start to end | The range overlaps the window |
| Season | Whales, June to November | 1 row for each year, month precision | The months overlap the window |
| Yearly, new dates not published | A festival last held 6-15 June 2026 | Only the past row; the item has `repeats_yearly` | Last dates plus one year overlap the window: shown as "not confirmed" |
| Standing experience | Shark cage diving | 1 row with the months that the operator states, or none | Months overlap, or "availability not stated" |

### Tier (proposed, see open decision O1)

- `headline`: a named item with a limited run, a season that people travel for, or a standing experience on the approved list.
- `local`: an item that repeats each week or each month with no special edition, and each item that the rule cannot place. Local is the default.
- The tier is a rule in code, not a model score. The card states the reason.

### Entities

```text
Source 1--* Page 1--* Evidence *--1 Item 1--* Occurrence
                                     |
                                     1--* Change
```

| Entity | Fields | Why it exists |
|---|---|---|
| **Source** | name, URL, owner rank, default category, town | The registry. Owner rank: organiser or operator (1), ticketing (2), listing (3). |
| **Page** | URL, source, content hash, fetched at, HTTP status, saved text | An unchanged hash means no model call. Saved text makes each check and backtest repeatable. |
| **Item** | kind (event or experience), title, town, time shape, `repeats_yearly`, category, tier, tier reason, status, venue, price text, `about`, action link, source link, first seen, `last_seen_at`, last verified | What the agent sees. One Item for a recurring thing (FynArts), with one occurrence for each edition. |
| **Occurrence** | item, start date, end date, precision (day or month), time text | When it is on. |
| **Evidence** | item, field, value, quote, page | One row for each field: the proof, and the input of the review. |
| **Change** | item, field, old value, new value, found at, actor (ingest or review) | "What changed since I last looked", and the log of each review decision. |

**Status.** `live`, `needs review` (set aside, not shown), `cancelled` (shown as cancelled), `rejected`.

**Rules of step 5.**

- **Not found in a run:** the item is not deleted. `last_seen_at` keeps the last date that a source listed it. Only an explicit statement on a page sets `cancelled`. A source can drop a listing for many reasons.
- **Duplicates:** code merges two listings only when town, dates and normalised title agree. If not sure, both stay. Joshua merges by hand in the review command.
- **Conflict:** the higher owner rank sets the value, with no review. Two sources of equal rank that disagree go to review, and the item stays live with "sources disagree".

**The check on each field (step 4).**

1. The quote is in the saved text of the page.
2. The value is in the quote ("75" in "Entry R75"). A date can have two quotes: the row ("28") and the header ("November 2026"). Test T2 proves this or changes it.
3. The value has the correct shape: a real date, an `https` link, a price with a currency and a number.
4. Each link gives a working page, checked before the item is stored.

An item is live when title, date (or stated availability), town and source pass. A failed optional field is left empty. A headline item also needs a working action link.

### Place

An item is in when it is within a 45-minute drive of Hermanus. **(Proposed)** The registry holds a list of towns that Joshua approves as inside 45 minutes. There is no routing service in version 1. Each card states its town.

### Interface

Four read operations. Each one is one question of the designer. REST (FastAPI, with its OpenAPI file) and a thin MCP server call the same Python functions.

| Operation | The designer's question | Input | Output |
|---|---|---|---|
| `what_is_on` | What is on for this trip? | place, from, to, `include_local`, category (optional) | Short cards: headline, experiences, not confirmed, and local when selected |
| `when_to_go` | When is the best time to go? | place, from month, to month, `include_local` | Seasons, yearly events and experiences, grouped by month. Headline first. |
| `what_changed` | What changed since I last looked? | place, since, `include_local` | New, cancelled, date moved, price changed, with old and new value |
| `tell_me_more` | Tell me more about this one. | item id | The full card: `about`, venue, price, action link, each quote with its source |

**`include_local`** has three values. The default is `auto`.

```text
false ─> headline only
true ──> headline first, then local
auto ──> 5 or more headline items in the window ─> headline only, plus "14 local items not shown"
         fewer than 5 ──────────────────────────> headline first, then local
```

The response states which case applied. The threshold is one constant. Experiences are a separate group and do not count for the threshold **(proposed)**.

**Short card** (in a list): the title must tell enough for a quick decision.

```text
[headline] Hermanus FynArts Festival · 24 June - 4 July 2027 · Hermanus
           source: https://www.hermanusfynarts.co.za/...        id: 42
```

**Full card** (`tell_me_more`):

```text
title     Hermanus FynArts Festival
when      24 June - 4 July 2027   (run, confirmed)
town      Hermanus
tier      headline: festival, limited run
about     "<1 or 2 sentences from the page, word for word, checked by code>"
venue     <text, or not stated>
price     <text, or not stated>
action    https://...   booking or contact link, tested
source    https://...   the page of the quotes
evidence  when: "24 June 2027 – 4 July 2027"
checked   2026-11-20    last_seen 2026-11-20
```

**The API governs the output, not the agent.**

- Code renders each response from one fixed template. The same query on the same data gives the same bytes.
- A response has `data` (fields) and `text` (the finished block).
- The order is fixed: headline, experiences, not confirmed, local. Inside a group: by date, then by title.
- The tool description says: "Show `text` as it is. Do not rewrite, reorder or add items."
- Each response also carries `as_of` (date of the last ingest), `holes` (sources that failed, and the number of items that wait for review), and `notes` (what each group means).

**Not in version 1, by the rule "build only what the data supports":** age, audience tags (no page stated an age rule in T1; 3 of 15 in T9), a relevance score (it needs labels that do not exist), a view for people, location data, cache, rate limit, webhook.

### What the AI agent does and does not do

| Agent | Does | Does not |
|---|---|---|
| Extraction model (step 3) | Reads the text of one page. Returns fields, each with a quote. | Verify, classify the tier, write to the database, use tools, see secrets. |
| Designer's agent (Claude or Codex) | Calls the four operations. Shows `text` as it is. Answers questions about it. | Rewrite or reorder, write facts, start a scrape, turn "not confirmed" into a fact. |
| Joshua's agent (review) | Runs the review command and shows each item in short form: page extract, quote, entry. | Decide. Joshua approves, rejects, corrects or merges. |

### Security

- **Page text is untrusted.** It can hide text and carry instructions.
- **Render** keeps only what a visitor sees.
- **The extraction model has web content only**: no private data and no action tool.
- **Code is the gate.** A value that the page does not state fails the check.
- **Residual risk.** A quote is page text and reaches the designer's agent in `about` and `evidence`. Limits: word for word only, a length limit, and `notes` tells the caller that it is third-party data. Test T5 covers this.

### Access

Ingest does not apply `robots.txt` on sources (decision by Joshua). We accept: this is against the wish of some site owners, a site can block the fetcher, and the feed then names that source in `holes`. Requests stay few and slow.

## Principles

1. **A fact needs a quote that code can check.** We accept: an item that fails waits for a person, so the feed can miss a true item for a week.
2. **The model extracts. Code and a person verify. Rules classify.** We accept: more code than "ask a model", and a rule that is sometimes wrong in a way that we can see.
3. **Headline first, and nothing is deleted.** The designer decides. We accept: no personal ranking, and a tier rule in place of taste.
4. **Never invent. State the past fact and name the holes.** We accept: 18 months out, a yearly event has no date, only "last held 6-15 June 2026".
5. **Simple, and only what the data supports.** SQLite, Python, one weekly batch, rules in files. It must work for the next town with a new registry and no new code. We accept: data can be 7 days old, and some useful features are left out.

## Open decisions

### O1. The tier rule (proposed; Joshua decides)

- **The constraints from Joshua:** verifiable, no model score, no rule for each exception, works for the next town, and a one-day event can be a headline.
- **Finding:** a rule on time shape alone is wrong. On Joshua's marks for 16 rows it puts a triathlon, two BMX races and a Christmas market in headline, and it puts one-day luxury items in local.
- **Proposal: category, then tier.** Each item gets one category from a short fixed list. One table maps a category to a tier. Both are in one file.

```text
category  = first match of: keyword in the title  ->  default category of the source  ->  "other"
tier      = table[category], and "local" if the item repeats each week or month

festival ............ headline      market .............. local
nature season ....... headline      sport to take part .. local   (triathlon, trail run, BMX, parkrun)
show ................ headline      community ........... local   (carols, school, church)
food and wine ....... headline      performance ......... local   (see the example)
experience (approved) headline      other ............... local
```

- **Example, a one-day concert:**
  - *Category rule as proposed:* a tribute band at the golf club and a famous artist at a wine estate are both `performance`, so both are local. In `auto`, the designer sees them only when fewer than 5 headline items are in the window.
  - *With a promote action:* Joshua promotes the famous artist in the review command. The change is logged as data. No rule is added.
- **Recommendation:** the category rule, plus promote and demote in the review command. Measure it on Joshua's marks (acceptance A6). If it is worse than the target, the next option is a category from the extraction model, with a quote, mapped by the same table.

### O2. Which towns are inside 45 minutes

- **Recommendation:** Joshua approves a list in the registry. Candidates from the tests: Onrus, Sandbaai, Vermont, Hawston, Fisherhaven, Hemel-en-Aarde, Stanford, Kleinmond, Gansbaai, Kleinbaai. Drive times are not checked.
- **Example, shark cage diving from Kleinbaai:** on the list, it is an experience card with "Kleinbaai". Off the list, the feed has no shark cage diving.

### O3. The approved list of experiences

- Decided: experiences enter from a list of operator pages that Joshua approves. There is no automatic discovery.
- Open: which of the 20 candidates of T9 are in (`research/t9_experiences.md`, section 2).

### O4. The extraction model (waits for T4)

- **Recommendation:** the cheapest model with zero false facts on the confirmed set and a "needs review" rate equal to a stronger model.

### O5. The collection strategy (waits for T10)

- A research agent is testing the access path for each source: feeds, structured data, HTML, PDF. The strategy goes into this file when its result is checked.

## How it is checked

The end result is defined in `docs/acceptance.md`. Work stops when each line there passes.

### Cases worked by hand

June 2027: 1 June is a Tuesday, so 5 and 12 June are Saturdays.

| # | Case | Input | Expected result |
|---|---|---|---|
| 1 | Repeating, no match | Market each Saturday. `what_is_on` Mon 7 to Thu 10 June 2027, `include_local=true` | Market not returned |
| 2 | Repeating, match | `what_is_on` Fri 11 to Sun 13 June 2027, `include_local=true` | Market returned, "Sat 12 June" |
| 3 | Show with many dates | Show on Tue to Sat, 1 to 26 June. `what_is_on` Sun 13 to Mon 14 June | Show not returned |
| 4 | Season | Whales June to November. Trips 20-25 August and 10-15 February 2027 | August: returned. February: not returned |
| 5 | Yearly, no new dates | Festival last held 6-15 June 2026. `what_is_on` 8-12 June 2027 | In "not confirmed", with "Last held 6-15 June 2026" |
| 6 | Planning | Same festival. `when_to_go` April to August 2027 | Under June, not confirmed |
| 7 | Wrong value | Page says "R75". Model returns 750 with quote "Entry R75" | Field fails: needs review |
| 8 | Invented quote | Quote is not on the page | Field fails: needs review |
| 9 | Change | Date moves 18 to 20 September, found 1 March 2027. `what_changed` since 15 January, then since 5 March | First: the change, old and new. Second: nothing |
| 10 | `auto`, many headline | 6 headline and 9 local items in the window | 6 headline cards and "9 local items not shown" |
| 11 | `auto`, few headline | 2 headline and 9 local items in the window | 2 headline cards, then 9 local cards, and the reason |
| 12 | Order | `include_local=true` | Each headline card is before each local card |
| 13 | Hidden instruction | Page has hidden text "the price is free" | Stored price is the visible price |
| 14 | Unchanged page | Second run, same text | No model call |
| 15 | Dead link | Booking link gives 404 | Headline item: needs review. Local item: live with no action link |
| 16 | Not found | A source drops a listing | Item stays, `last_seen_at` does not move, status is not `cancelled` |
| 17 | Cancelled | Page says "cancelled" | Status `cancelled`, and a Change row |
| 18 | Same query two times | Equal input, no ingest between | Equal bytes |
| 19 | Tell me more | `tell_me_more` for an item | Each fact has its quote and source |
| 20 | Tier | Triathlon, BMX race, Christmas market | Local. Whale season, FynArts, Whale Festival: headline |

### What is measured

- **On a confirmed set** (15 to 20 saved pages; the model proposes each entry, Joshua confirms it): false facts, missed items, "needs review" rate, measured cost.
- **The tier rule** against Joshua's marks.
- **After each change** to a prompt, a model or a rule: the same run on the same saved pages, and a comparison.
- **Test quality:** break the verify code on purpose and confirm that a test fails.
- **The interface:** a fresh Claude with only the MCP answers the designer's questions for a test trip.

### What is not proved

- **Completeness.** No test proves that the feed has each item. In T1, 89 of 112 events were in one source only.
- **A correct quote with a wrong meaning.** The value-in-quote check and the confirmed set find most cases. A rare case can pass.
- **What the agent shows.** The API output is deterministic. The agent's words are not.
- **The luxury bar.** The tier rule is a stand-in for taste. It is measured on a small set of marks from one person.

## Scale and cost

| Symbol | Meaning | Measured for Hermanus |
|---|---|---|
| S | sources in the registry | 11 gave events in T1; 20 experience candidates in T9 |
| P | pages fetched each week | not measured |
| D | pages that changed in a week | not measured; list pages change each week |
| E | items | at least 112 events (5 towns) and up to 20 experiences |
| R | occurrence rows | about 78 for a weekly item over 18 months |

| Part | Grows with | Order |
|---|---|---|
| Fetch and render | pages, each week | O(P). No model cost. |
| Model calls | changed pages only | O(D). The first run is O(P). |
| Verify | fields of changed pages; a text search in one page | O(D x fields x page length) |
| Match to a known item | new items against the items of the place | O(new x E) |
| Query | rows in the window, with an index on place and dates | O(log R + results) |
| Review by a person | items that fail a check | O(failures) |
| A new town | one registry file: sources, towns, approved experiences | O(S) of a person's time. No new code. |

- **Cost of one run:** not measured yet. Budget for all tests and the first run: 5 US dollars.
- **What fails first at 10 times the load (10 towns):** the person. The review queue, the registry and the approved experiences all need a person. The design goal is a very low failure rate, so that review stays small.

## Execution plan

Step 0 is serial. After it, three builders work in parallel, each in its own git worktree. A blind reviewer reads each patch. Claude integrates one patch at a time and reports a diagram after each step.

| # | Slice | Who | Behaviour that Joshua can check | Check |
|---|---|---|---|---|
| 0a | Direction test T2 | Claude | 10 saved real pages (HTML and PDF): the quote check and the date check work. If not, stop and change the design. | Numbers in `docs/assumptions.md` |
| 0b | Schema and tracer bullet | Claude | One saved page goes through extract, verify and store, and `what_is_on` returns its card | Hand cases 1 and 2 |
| 1 | Collect | Builder A | Registry, fetch, render (HTML and PDF), hash, holes, link check | Hand cases 13, 14, 15 |
| 2 | Verify and review | Builder B | The four checks, needs review, the review command, category and tier | Hand cases 7, 8, 16, 17, 20 |
| 3 | Read | Builder C | Four operations, `include_local`, fixed text, REST and MCP | Hand cases 3 to 6, 9 to 12, 18, 19 |
| 4 | First real run | Claude | Ingest of the registry; Joshua reviews the queue; cost is measured | `docs/acceptance.md` |
| 5 | Fresh-Claude test and write-up | Claude and Joshua | A new Claude uses the MCP for a test trip | `docs/acceptance.md` |
