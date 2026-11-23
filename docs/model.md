# Model: Hermanus event feed

Last change: 2026-11-22. This file is the shared mental model. If the code and this file disagree, one of them has a fault. The full design is in `docs/design.md`.

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
- **Extract** is the only model step. It returns fields with word-for-word quotes. It must never verify, write or use a tool.
- **Verify** is code. It checks quote on page, value in quote, shape, and links. It must never let a field through on the model's word.
- **Store** holds events, their occurrence rows, the evidence for each field and a change log.
- **Update** gives each item a category and a tier (headline or local) by a rule in a file. It never deletes an item that a run does not find.
- **Read and Card** answer four questions: what is on, when to go, what changed, tell me more. Headline comes first. `include_local` is `auto`, `true` or `false`. They must never start a fetch or invent a date.
- An item has two separate properties: its time shape (single date, repeating dates, run, season) and its tier.

## Findings that shaped the model

Each line: what we believed, what the test showed, what changed. Newest first.

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

- Does the value-in-quote check work for dates in words and for a year in a header? T2 answers it.
- Is the category rule good enough for the tier? Joshua's marks answer it (design O1, acceptance A6).
- Which towns are inside 45 minutes, and which experiences are approved? Joshua decides (design O2, O3).
- Which access path is the most reliable for each source? T10 answers it.
- Which model? T4 answers it.
