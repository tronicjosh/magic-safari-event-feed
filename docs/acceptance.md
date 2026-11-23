# Acceptance: when the work is done

Status: **draft** (2026-11-23), written by Claude from the design. Joshua defines the end result; his definition replaces or corrects this file. Each number marked "Joshua sets" is not decided.

Work stops when each line below passes. A line that does not pass is reported as "fail" or "not checked", with the output. Nothing more is built after all lines pass.

## What the designer gets (the end result)

A designer asks an AI agent that has only the feed's MCP: "What is on in Hermanus for my clients from 20 to 27 June 2027?" The answer is short. Headline items come first. Each item has a title that tells the story, its date, its town and a working source link. Nothing in it is false. The designer can ask "tell me more" for one item and get the quote behind each fact.

## Checks

| # | Check | How it is proved | Target |
|---|---|---|---|
| A1 | No false fact | Each live fact of the confirmed set is compared with Joshua's confirmed entry | 0 false facts |
| A2 | Hand cases | `pytest` runs the 20 hand cases of `docs/design.md` | 20 of 20 pass |
| A3 | The verify step has real tests | Break each of the four checks on purpose; a test must fail each time | 4 of 4 |
| A4 | Few items fail | Share of extracted items that go to "needs review" on the first real run | Joshua sets (proposed: below 10 percent) |
| A5 | Headline items are present | Checked by hand in the live feed: whale season, FynArts Festival, Hermanus Whale Festival, and each approved experience | All present |
| A6 | The tier rule agrees with Joshua | The rule runs on the rows that Joshua marked | Joshua sets (proposed: no marked headline is local, and at most 2 wrong in 16) |
| A7 | Links work | Each source link and action link of a live item is requested | 100 percent give a page |
| A8 | Holes are visible | Stop one source on purpose; the response names it in `holes` | Pass |
| A9 | Output is governed by the API | The same query two times gives equal bytes; with `include_local=true`, each headline card is before each local card | Pass |
| A10 | `auto` works | A window with 5 or more headline items, and one with fewer | Hand cases 10 and 11 pass on real data |
| A11 | A fresh Claude can use it | A new Claude session with only the MCP answers three questions for a test trip: what is on, when to go, what changed. It shows the feed's text unchanged | Joshua judges: pass or fail |
| A12 | Cost is known | The measured cost of the first run and of a second run one week later (or a replay) | Recorded; total spend below 5 US dollars |
| A13 | Unchanged pages cost nothing | A second run on unchanged saved pages | 0 model calls |
| A14 | One command checks all | One command runs lint and all tests | Exit code 0 |
| A15 | The write-up is true | `docs/design.md` agrees with the code and with `docs/assumptions.md`; Joshua can explain each part without AI | Joshua confirms |

## Not part of done

- More sources than the registry of version 1.
- A view for people, a relevance score, tags for audience, location data.
- A second town.

## Results that Joshua must check himself

- A1: the confirmed set is his.
- A5 and A6: the luxury bar is his judgment.
- A11: the answer that a designer sees.
