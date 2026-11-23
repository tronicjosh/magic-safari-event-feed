# Model: Hermanus event feed

Last change: 2026-11-23. This file is the shared mental model. If the code and this file disagree, one of them has a fault. The full design is in `docs/design.md`.

## The problem in one paragraph

A travel designer sells a luxury trip to Africa, usually 6 to 18 months before it starts, and refines it weeks before. To know what is on in a place, they search tourism sites by hand. That is admin, and "agents sell what's easy to sell". Magic Safari earns only when a trip is booked. "Good" is: the designer's AI agent asks one question and gets a short list of what is on in Hermanus, where each fact has a source and nothing is false. The designer knows the guest and makes the choice.

## How the system works

```text
INGEST, weekly
 sources -> Fetch -> Render -> hash -> Extract -> Verify -> Update -> Store (SQLite)
                               same?    model      code        |
                                 |                   |         v
                           no model call           fail --> needs review --> Joshua

QUERY, on request
 designer -> agent -> REST or MCP (read-only) -> Read -> Card
```

- **Fetch and Render** get the text that a visitor sees. They must never pass hidden text on.
- **Extract** is the only model step. It returns fields with word-for-word quotes, and it decides with proof: the town from the list, "held each year", "this weekly rule has no end", and the two bars of the registry. It must never verify, write or use a tool.
- **Verify** is code. It checks quote on page, value in quote, shape, and links. It must never let a field through on the model's word.
- **Store** holds events, their occurrence rows, the evidence for each field and a change log.
- **Update** gives each item a category from Joshua's list. It sets no tier and no rank: the feed stores facts, not judgments. It never deletes an item that a run does not find.
- **Read and Card** are six read operations: places, what is on (dates known), when to go (no dates), find (by name or subject), what changed, tell me more. A list gives short cards with enough facts to judge; tell me more gives the depth for the items that the agent recommends. The order is neutral (group, date, title). Each list starts with `counts`, so the designer knows how many items exist. The fact rules are sent one time in the server instructions; a tool description says only when to call the tool. Each answer shows all groups; there is no `include_local` (design draft 3). They must never start a fetch or invent a date.
- An item has a time shape (single date, repeating dates, run, season) and a category. Both are facts.
- **Discovery** runs each week: sources that collected pages name, and that the registry does not have, go to a candidates list for Joshua. `holes` shows how many wait.

## Findings that shaped the model

Each line: what we believed, what the test showed, what changed. Newest first.

- 2026-11-23 Decision by Joshua, with tests T12 and T13: the model has more discretion, and two bars act at ingest. We believed (draft 4) that the feed stores only facts and that the town is a quoted value. Joshua's decisions: the model chooses the town from the list; a weekly rule needs the model's mark that it has no end; a hard bar keeps out what a visitor cannot go to; a soft bar marks what is not worth showing to a traveller on a luxury trip, and those items stay and are shown in their own group. This changes "facts, not judgments": the soft bar is a judgment of the feed, kept reversible because nothing is removed and the wording is data in the registry. Effect, measured on 2 real pages (56 items) before and after: stored 37 and 40; lost true items found 1 and 0 (the Hemel-en-Aarde market); 12 of the 40 are below the bar. T2 numbers of the verify step before and after the weekly guard: 205 live of 259 and 223 of 226 dates, no change. False facts against a confirmed set: not measured, the set does not exist. New risks: a town choice from the model's knowledge can be wrong and code cannot see it ("Markets" got Hermanus where the page names several towns); the judgments differ between runs; cost of extraction plus 39 percent.
- 2026-11-23 First real run: 10 live pages, 0 failed, 194 items from the model, 151 stored, 2 updated, 41 not stored (16 town outside the place, 8 no time, 6 no town on a regional source, 4 months with no proof of each year, 7 other). Cost 0.064780 US dollars. A second run: 0 model calls. The answer for 20 to 27 June 2027 has 13 items, with the FynArts Festival (24 June to 4 July 2027) from the organiser's page.
- 2026-11-23 We believed that months with no year are a season. The joined run showed "October" of a 2026 calendar as October 2027 and 2028. Thus a season with no year needs the model's yearly quote on the page. Effect: 4 real items not stored, 0 projected.
- 2026-11-23 We believed that "throughout the year" and "first Friday of every month" must fail, because no month name is in the quote. Thus January to December with no year passes on the model's judgment, and the card shows "All year" with the quote. Effect on the T2 answers: 208 of 259 items live (was 205), 226 of 226 dates (was 223).
- 2026-11-23 Decision by Joshua: a basic change log. Each card gives `first seen` and its latest change, so an agent with no memory can answer "what is new since January"; `what_changed(place, since)` answers the direct question. Category is a choice of the model from the list of the registry.
- 2026-11-23 We believed that code can stop a false weekly rule with date patterns. Two blind reviews showed that a pattern list leaks ("Saturday 05.12.2026", "every saturday in may"). Thus three parts: code refuses any digit in a weekly quote except a clock time with minutes; the model decides the meaning; the card shows the rule and its quote, not "confirmed". Effect: T2 numbers 205 of 259 before and after; a true rule such as "Saturday 9 - 1pm" is now lost, with the reason in the report.
- 2026-11-23 Scope cut, approved by Joshua: one path that shows each thing the brief names; the rest is design only (see `docs/design.md`, "Scope of the build"). The hard visitor bar is removed, because T13 gave 0 of 180 items.
- 2026-11-23 A range card now says "a range, each day is not stated", because code cannot see a closed day inside a range (decision by Joshua: tell the user, so that they take it into account).

- 2026-11-23 (slice 0b.1) We believed that an item with no usable town can take the default town of its source. The real weekend page showed why that is too wide: "Bring & Braai" is in Pringle Bay, which is not in the place, and the default would give it the town Hermanus, a false fact. Thus the default applies only when the page states no town. A town that the page states and that is not in the list keeps the item out. A town that fails the check also keeps the item out, and a source for a region (Overstrand Municipality) has no default town. Measured on 2 real pages (56 items): 37 stored, 19 not stored (8 town not in the list, 3 no town and no default, 5 no time on the page, 3 a rule by month). 1 of the 8 is a loss of a true item ("Hemel-en-Aarde village" against "Hemel-en-Aarde" in the list); slice 2 (the model chooses from the list) repairs it. False facts: not measured, because the confirmed set does not exist yet.
- 2026-11-23 (slice 0b.1) We believed that 43 passing tests and 5 break tests made the tracer safe. A blind review showed 11 faults. Repaired, each with a test: an item that is not an object stopped the page; a town that failed the check got the default town; the stored price was the model's text and is now the quote; the place filter was a town name and is now the place of the source; the order, a day two times on one card, a title over two lines, a reversed window. Not repaired, because each is a design question for Joshua: (1) a weekly rule becomes 18 months of dates on the weekday word alone, so "Every Wednesday in December 2026" or "Closed on Sundays" gives false dates; the 7 real weekly entries in the saved answers are all true rules; (2) a show that the model gives as one range (1 to 26 June) is shown on its closed days. Also not repaired: a short title ("a") passes the value-in-quote check (slice 2, verify).
- 2026-11-23 (slice 0b.1) Implementation choices, reversible: the registry is `registry.json`; a weekly rule is stored as one row for each date for 18 months after the ingest (rejected: match the rule at query time, which gives two code paths for time); the place of an item is its town looked up in the registry at query time, with no `place` field on the item; an item that is not stored is in the run report only, and the set-aside table is slice 2.

- 2026-11-23 We believed that "repeats yearly" needs a registry field that Joshua sets. Joshua's direction: the person is the last resort, and the model looks for proof on the page. T11 showed that the model gives a quote that is on the page for 7 of 7 yearly marks, at plus 0.5 percent cost, but that the pages state it for only 7 of 87 items (not for FynArts on 2 pages). Thus `repeats_yearly` is an extracted field with a quote, a failed check leaves it empty with no review, and the "not confirmed" group is small until organiser pages are collected. Effect on the two measures: false facts 0 found in 7 marks (1 weak quote); items for review: no change, because this field never sends an item to review.

- 2026-11-23 Decision by Joshua, not a test: the feed controls what the agent knows, not what it decides. We believed that four operations and the instruction "show the text as it is" were enough. Joshua's points: an agent must look up an item by name and see which places exist; rules belong one time in the server instructions; the agent decides how many items to show; and a designer who sees 5 items must know that 47 exist. Thus design draft 5 has six operations, a short card with kind, category, price and one quote, `counts` in each list, and server instructions. Effect on the two measures: none measured; this is tested by acceptance A8 and A14 with a new Claude.

- 2026-11-23 Decision by Joshua, not a test: the feed stores facts, not judgments. We believed that the feed must mark headline items by a table from category to tier. Joshua's reason: travellers have different interests, so relevance belongs to the agent at query time. Thus the tier, the headline-first order and the promote and demote commands are removed (design draft 4). Effect on the two measures: none measured; no code used the tier yet. Acceptance lines A7, A8, A12 and hand cases 10, 12, 15, 20 still describe the tier and wait for Joshua.
- 2026-11-23 We believed that the T2 pass rate was equal for each kind of item. Joshua's review of T2 showed that the items closest to what Magic Safari sells are the weakest: the whale page gave 0 items, shark cage diving has no time, and only 3 of 11 saved pages are experience or season pages. Thus the 198 of 213 result is mostly small local events. I then measured 15 experience and season pages (T2b): no check failed, but only 9 of 49 items have a time, 5 a price and 7 a town, because operator pages do not state them or need a browser. Thus the weak point for experiences is the source page, not the check. An experience needs its operator, town and booking link from the registry, and the page adds only what it states.

- 2026-11-23 We believed that 22 passing tests made the verify step safe. A blind review showed 6 ways for a false value to pass, for example a quote "8 17:30 Hangklip Hotel" on a page that says "18 17:30". Thus a quote must start and end at a word or number boundary, a day number must stand alone, and a date part that the kind does not use must be 0. Effect, measured on the saved T2 answers before and after: false facts found 0 and 0; items for review 15 of 213 and 15 of 213. Known gaps that stay open: text hidden by a stylesheet class passes `feed/render.py`; an inline tag splits a word or a price over two lines; a price passes if its number is anywhere in the quote, with any currency; "Jan" and "Julie" in a name count as a month.

- 2026-11-23 We believed that a date in a list row (day only, year in a header) may not be checkable by code. T2 showed that it is: the model gives day, month and year as numbers with one quote for each place (row, month header, year header), and code finds each part. 215 of 218 date entries pass on 11 real pages; 32 of 32 dates agree between two pages of the same office. Thus the verify design stays. Measured: 0 false dates found in the sample and the cross-check; 15 of 213 items (7 percent) need review or have no time.
- 2026-11-23 We believed that quotes need loose matching. T2 showed that 745 of 755 checked fields match exactly and 10 need only whitespace. Thus the punctuation level is not needed by the data so far; it stays until T4, then it is removed if still 0.
- 2026-11-23 We believed that four time kinds cover the pages (date, range, months, weekly). T2 showed a fifth: a rule by month ("first Friday of every month", 3 items, and 2 more in a PDF footnote with no date entry). Thus the time shape "repeating dates" needs a monthly rule, or these items wait for review. Joshua decides.
- 2026-11-23 We believed that a quote ties a date to its item. T2 showed that it does only where the row holds both (166 of 214 entries). On pages where the title and the date are on different lines, code proves that the date is on the page, not that it is this item's date. Thus this is a known gap of the check; a position rule (the date quote is the nearest to the title quote) is a candidate, not built.

- 2026-11-23 We believed that a Hermanus list gives the standing experiences. T9 showed that no list is complete, and that 15 of 20 candidates start outside Hermanus (shark cage diving starts in Kleinbaai). Thus experiences come from a list of operator pages that Joshua approves, and their place rule is wider than for events.
- 2026-11-23 We believed that an operator page states months and price. T9 showed months on 5 of 15 pages and price on 7 of 15; the facts are often in a booking engine. Thus many experience cards say "not stated", and the booking link is the main value.
- 2026-11-22 We believed that Hermanus has 20 to 30 events. T1 counted 112 as a lower limit (5 towns), and 79 percent are in one source only. Thus a bar or an order is necessary, and the scope (which towns) is a decision.
- 2026-11-22 We believed that events are known months ahead. T1 showed that sources publish small events 1 to 5 weeks ahead: 59 of 66 dated events are in the next 6 weeks. Thus the feed has two populations. The durable one (annual, recurring, season: about 46) serves the 6 to 18 month use. The weekly flow serves only the last weeks before a trip.
- 2026-11-22 We believed that the weekly delta is small. T1 showed about 39 new small events in one week. Thus model cost and review load follow the weekly flow, if the flow is in scope.
- 2026-11-22 We believed that tourism sites give HTML. T1 showed that the largest source is PDF files and one image. Thus Fetch and Render must read PDF text.
- 2026-11-22 We believed that a quote holds the full date. T1 showed rows with the day only; the year is in a header. Thus one field can need two quotes.
- 2026-11-22 We believed that sources mostly agree. T1 showed 14 contradictions in 23 shared events, and last year's dates on tourism pages. Thus owner rank is necessary, and a review for each conflict is too much.

From the prototype (stated in `docs/handover.md`, not tested again here):

- A page is not a reliable witness, and a model alone cannot be the judge. Thus each fact needs evidence that code can check.
- A false fact on a trip costs more than a missed event. Thus a failed check holds the event for a person.

## Where an error is expensive

1. **The verify step.** A fault here puts a false fact on a client's trip.
2. **The time model.** A wrong overlap says that an event is on when it is not.
3. **The confirmed set.** Each gate depends on labels that Joshua confirmed.

## Open questions

- T2 answered the date question (yes). Open from T2: a monthly rule as a time kind; "free" as a price; the link between a date quote and its item on pages with one field for each line.
- Can a new Claude, with only the tool descriptions, pick the correct call and rank the items well? Acceptance A14 answers it.
- Does extraction work on operator pages (experiences, seasons) as well as on event lists?
- Which towns are inside 45 minutes, and which experiences are approved? Joshua decides (design O2, O3).
- Which access path is the most reliable for each source? T10 answers it.
- Which model? T4 answers it.
