# Acceptance: when the work is done

Work stops when every line below passes. A line that does not pass is reported as "fail" or "not checked", with the output. Nothing more gets built once all lines pass.

## The end result

A designer asks an AI agent that has only the feed's MCP: "What's on in Hermanus for my clients from 20 to 27 June 2027?"

The agent chooses the items that fit the clients and says how many the feed has for those dates. Each item has a title that says what it is, its date, its town and a working source link. Nothing in it is false. The designer can ask for more on one item and get the quote behind each fact.

## Checks

| # | Check | How I prove it | Target |
|---|---|---|---|
| A1 | No false facts | Compare every live fact in the confirmed set (15 to 20 saved pages) with my confirmed entry | 0 false facts |
| A2 | Missed items are counted | Count items in my confirmed entries that the feed does not have | Reported, no target |
| A3 | Hand cases pass | `pytest` runs the 24 hand cases in `docs/design.md` | 24 of 24 |
| A4 | The checks are really tested | Break each of the four verify checks on purpose. A test must fail each time | 4 of 4 |
| A5 | Few items need review | Share of extracted items sent to review on the first real run | Under 10% |
| A6 | Every time shape works on real data | The live feed has at least one real item of each shape: single date, repeating dates, run, season, yearly with no new dates | All 5 present |
| A7 | Key items are there | I check by hand: whale season, FynArts, Hermanus Whale Festival, each approved experience | All present |
| A8 | The cards carry enough to judge | A new Claude with only the MCP gets two different guests for the same dates. It selects from the short cards, and calls `tell_me_more` only for the items that it recommends | The two selections differ, each fits its guest, and no fact is changed. I judge |
| A9 | Links work | Request every source link and action link of a live item | 100% return a page |
| A10 | Gaps are visible | Stop one source on purpose. The response names it in `holes`. Quicket shows as "not collected" | Pass |
| A11 | The retry adds no errors | Run the confirmed set with and without the stronger-model retry | Review rate drops, false facts stay 0 |
| A12 | The API controls the output | Same query twice gives the same bytes. REST and MCP give the same bytes. The order is neutral (group, date, title), `counts` is equal to the number of cards, and no item in the window is left out | Pass |
| A13 | `holes` shows what is missing | The response gives sources collected against sources known, each source not collected with its declared count, and the items that wait for review | Hand cases 10 and 11 pass on real data |
| A14 | A fresh Claude can use it | A new Claude session with only the MCP answers the questions in the design's question table for a test trip (places, when to go, what is on, find by name, what changed, tell me more). It picks the expected call, changes no fact, gives each source link, and says how many items the feed has and how many it shows | I judge pass or fail |
| A15 | Cost is known | Measured cost of the first run and of a second run a week later (or a replay). Weekly-run estimate with the model named and the arithmetic shown | Recorded; total spend under $5 |
| A16 | Unchanged pages are free | Second run on unchanged saved pages | 0 model calls |
| A17 | One command checks everything | One command runs lint and all tests | Exit code 0 |
| A18 | The write-up is true | `docs/design.md` matches the code and `docs/assumptions.md`, and I can explain every part without AI | I confirm |

## Not part of done

- More sources than the version 1 registry.
- A screen for people, a relevance score, audience tags, location data.
- A second town.

## Checks only I can do

- A1 and A2: the confirmed set is mine.
- A7 and A8: which items must be there, and if a selection fits a guest, is my call.
- A14: whether the answer a designer sees is good enough.