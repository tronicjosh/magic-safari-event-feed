# Acceptance: when the work is done

Work stops when each line below passes, or is mine to do. A line that does not pass is "fail" or "not checked", with the evidence. Nothing more is built when all lines pass.

## The end result

A designer asks an AI agent that has only the feed's MCP server: "What's on in Hermanus for my clients from 20 to 27 June 2027?"

The agent selects the items that fit the clients, and says how many the feed has for those dates. Each item has a title that says what it is, its date, its town and a source link. Nothing in it is false. The designer can ask for more on one item and get the quote behind each fact.

## Checks, and the status on 2026-11-23

| # | Check | How it is proved | Status | Evidence |
|---|---|---|---|---|
| A1 | No false facts | I compare each fact of a sample of 20 stored items with its page. Target: 0 false facts | **Pre-read done; my marks are open** | `evals/sample_check.md` has 20 items and 100 facts. Claude read each fact against its quote: 0 false found; 3 doubts for me to judge ("Walker Bay" gives the town Hermanus; "Pearly Beach Hengel Klub" is listed under Gansbaai by the page; a rule by month is stored as "all year"). A reviewer checked by code: 0 of 145 dates that a page states failed against the stored page text |
| A2 | Missed items are counted | Items of the model that the feed did not store, each with a reason | Pass | First run: 41 of 194 not stored (21 percent). 22 are towns outside the place or with no town |
| A3 | Hand cases pass | Each built hand case of `docs/design.md` is a test | Pass | Cases 1 to 14, 16, 18, 19, 20, 24. Cases 15, 17, 21 to 23 are not built |
| A4 | The checks are really tested | Each key line is broken on purpose; a test must fail | Pass | Done for verify, update, read and ingest. Where no test failed, a test was added or the line was removed |
| A5 | Each kind of event works on real data | The real database has a single date, repeating dates, a run, a season, and a yearly item | Pass | `feed.db`: 142 events, 9 seasons, 9 yearly items; weekly rules; FynArts as a run |
| A6 | Key items are there | Whale season, FynArts 2027, Hermanus Whale Festival | Pass | All three are stored. The Whale Festival has its 2026 dates and "held each year" |
| A7 | The cards carry enough to judge | A new Claude with only the feed gets two different guests for the same dates | **Pass by test; my judgment is open** | `research/acceptance/agent_test.md`, questions 2 and 3. The two selections differ: the couple (wine and art, no crowds) gets FynArts, the wine market and a whale item; the family gets the whales, a parkrun and a craft market. Each says "3 of 13" or "4 of 13", and each item has its tag |
| A8 | A new Claude can use it | It answers the 7 questions: the expected tool, no changed fact, each item with its tag and its source, "3 of 13", and the agreed shape (`research/acceptance/expected.md`) | **Pass by test; my judgment is open** | `research/acceptance/agent_test.md` (the final run): 7 of 7 answers pass the checks by code; no site and no stated date from outside the feed; 79 to 149 words; each item has its tag and its source link. `research/acceptance/scenarios_round2.md`: 20 more conversations after the repairs, with no false "not in the feed" statement. The agent is the API agent with the tools and instructions of the MCP server; the MCP transport has its own tests |
| A9 | The feed controls the output | The same query gives the same bytes; neutral order; `counts` equal to the cards; nothing in the window left out | Pass | Tests, and a blind review on the real database |
| A10 | Gaps are visible | `holes` names each source that is not collected, with what it declares | Pass | Quicket (136 events within 60 km) and Webtickets are in each answer |
| A11 | Cost is known | Measured cost of the first run and a second run; the weekly arithmetic; total spend under the limit (5 US dollars at first; 10 from 2026-11-23) | Pass | 0.064780 and 0.000000 US dollars; `docs/design.md`, "Scale and cost"; total 7.29 |
| A12 | Unchanged pages are free | A second run on unchanged pages | Pass | 0 model calls, on live pages |
| A13 | One command checks everything | Lint and all tests | Pass | 247 tests; exit code 0 |
| A14 | The write-up is true | `docs/design.md` matches the code, and I can explain each part without AI | **Mine, open** | Draft 6 was written against the code |

## Not part of done

Each of these is in `docs/design.md` as "next": links checked; `cancelled`; merge of one event from two sources; a retry with a stronger model; standing experiences; REST, `find`, `places`; a hosted server; a second town; a run one week later.

## Checks only I can do

- A1: the sample is mine to mark.
- A7 and A8: if a selection fits a guest, and if the answer is good enough for a designer, is my call.
- A14: I must be able to explain it.
