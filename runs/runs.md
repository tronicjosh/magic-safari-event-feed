# Runs

One line for each run. Cost is measured tokens times the list price; it is not an estimate.

| Date | Run | Model | Tokens in | Tokens out | Cost (USD) | Items | Live | For review | Note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | T2 direction test, 11 saved pages | claude-haiku-5-5 | 47,486 | 87,332 | 0.048414 | 213 | 198 | 15 | One more call (Kalfiefees pilot) ran before these and its usage was not saved, because the script failed after the call. Its cost is not in this number. No database yet, so new / changed / unchanged do not apply. |
| 2026-11-23 | T2b, 12 more experience and season pages | claude-haiku-5-5 | 47,447 | 14,973 | 0.012231 | 46 | 7 with a time | 39 with no time | Total measured spend to here: 0.060645 US dollars. |
| 2026-11-23 | T11, yearly field with a quote, 7 saved pages | claude-haiku-5-5 | 34,497 | 36,362 | 0.021631 | 87 | 7 marked yearly | 0 | The T2 calls of the same 7 pages cost 0.021534. Total measured spend to here: 0.082276 US dollars. |
| 2026-11-23 | T12, town from the list and weekly `ongoing`, 4 real pages and 1 trap page | claude-haiku-5-5 | 23,769 | 75,018 | 0.039887 | 180 | | | The 4 real pages cost 0.038327 against 0.037383 in T2 (plus 2.5 percent). |
| 2026-11-23 | T13, T12 plus the visitor bar and the traveller bar, the same 5 pages | claude-haiku-5-5 | 26,624 | 102,365 | 0.053845 | 180 | 143 above the bar | 37 below the bar | The 4 real pages cost 0.051802 against 0.037383 in T2 (plus 39 percent). Total measured spend to here: 0.176008 US dollars. |
| 2026-11-23 | Ingest, 10 pages: 10 changed, 0 unchanged, 0 failed | claude-haiku-5-5 | 56,659 | 118,229 | 0.064780 | 194 | 151 new, 2 updated | 41 | 10 model calls. Live: items stored. For review: items set aside, in the report only. |
| 2026-11-23 | Ingest, 10 pages: 0 changed, 10 unchanged, 0 failed | claude-haiku-5-5 | 0 | 0 | 0.000000 | 0 | 0 new, 0 updated | 0 | 0 model calls. Live: items stored. For review: items set aside, in the report only. |
| 2026-11-23 | Demo agent, 4 test answers (1 on Opus 5.5, 3 on Haiku 5.5) | claude-opus-5-5, claude-haiku-5-5 | | | 0.069481 | | | | One answer: 0.064573 on Opus 5.5 and 0.001902 on Haiku 5.5 for the same question (2 tool calls). The page shows the cost of each later answer; those are not in this file. Total measured spend to here: 0.310269 US dollars. |
| 2026-11-23 | Agent test for acceptance A7 and A8: 7 questions | claude-opus-5-5 | | | 0.593061 | | | | The dearest answer was `what_changed` with 151 new items: 0.2384. Total measured spend to here: 0.903330 US dollars. |
| 2026-11-23 | Agent answers tuned to the agreed shape: 3 rounds of the 7 questions | claude-opus-5-5 | | | 0.919520 | | | | Round 1: 0.351900; round 2: 0.340222; round 3: 0.227398 (before: 0.593061). The 7 answers are now 108 to 129 words. Total measured spend to here: 1.822850 US dollars. |
| 2026-11-23 | Scenario suite: 33 conversations with the agent | claude-opus-5-5 | | | 1.429536 | | | | 21 of 33 passed the checks by code on the run. Total measured spend to here: 3.252386 US dollars. |
| 2026-11-23 | Scenario suite, round 2: a run with no transcript (a fault of my edit), then 20 scenarios | claude-opus-5-5 | | | 1.256884 | | | | 0.494322 for the run that saved nothing; 0.762562 for the 20 scenarios, 14 of 20 pass the checks by code. Total measured spend to here: 4.509270 US dollars. |
| 2026-11-23 | Final acceptance run: the 7 questions of the agent test | claude-opus-5-5 | | | 0.281390 | | | | 7 of 7 pass the checks by code. Total measured spend: 4.790660 of 5 US dollars. No more model calls are planned. |
