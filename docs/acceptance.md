# Acceptance: when the work is done

Work stops when every line below passes. A line that does not pass is reported as "fail" or "not checked", with the output. Nothing more gets built once all lines pass.

## The end result

A designer asks an AI agent that has only the feed's MCP: "What's on in Hermanus for my clients from 20 to 27 June 2027?"

The answer is short. Headline items come first. Each item has a title that says what it is, its date, its town and a working source link. Nothing in it is false. The designer can ask for more on one item and get the quote behind each fact.

## Checks

| # | Check | How I prove it | Target |
|---|---|---|---|
| A1 | No false facts | Compare every live fact in the confirmed set (15 to 20 saved pages) with my confirmed entry | 0 false facts |
| A2 | Missed items are counted | Count items in my confirmed entries that the feed does not have | Reported, no target |
| A3 | Hand cases pass | `pytest` runs the 20 hand cases in `docs/design.md` | 20 of 20 |
| A4 | The checks are really tested | Break each of the four verify checks on purpose. A test must fail each time | 4 of 4 |
| A5 | Few items need review | Share of extracted items sent to review on the first real run | Under 10% |
| A6 | Every time shape works on real data | The live feed has at least one real item of each shape: single date, repeating dates, run, season, yearly with no new dates | All 5 present |
| A7 | Headline items are there | I check by hand: whale season, FynArts, Hermanus Whale Festival, each approved experience | All present |
| A8 | The tier rule matches my judgment | Run the rule on the 16 rows I marked | No marked headline is local; at most 2 of 16 wrong |
| A9 | Links work | Request every source link and action link of a live item | 100% return a page |
| A10 | Gaps are visible | Stop one source on purpose. The response names it in `holes`. Quicket shows as "not collected" | Pass |
| A11 | The retry adds no errors | Run the confirmed set with and without the stronger-model retry | Review rate drops, false facts stay 0 |
| A12 | The API controls the output | Same query twice gives the same bytes. REST and MCP give the same bytes. With `include_local=true`, every headline card comes before every local card | Pass |
| A13 | `auto` works | One window with 5 or more headline items, one with fewer | Hand cases 10 and 11 pass on real data |
| A14 | A fresh Claude can use it | A new Claude session with only the MCP answers three questions for a test trip: what's on, when to go, what changed. It shows the feed's text unchanged | I judge pass or fail |
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
- A7 and A8: what counts as a luxury headline is my call.
- A14: whether the answer a designer sees is good enough.