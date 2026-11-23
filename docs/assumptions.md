# Assumptions and feature ledger

A feature stays only if a test result or a requirement needs it. Add one row for each test. Do not delete a row; a wrong belief is useful history.

| # | Assumption or feature | Test result | Decision |
|---|---|---|---|
| T1 | Hermanus has about 20 to 30 events in an 18-month window, and the public sources find most of them | **Wrong** (2026-11-22). 112 distinct events counted as a lower limit, in Hermanus and 4 near towns. 55 one-day, 11 runs, 14 recurring, 4 seasons, 28 annual with no new date. 89 of 112 are in one source only. 59 of 66 dated events are in the next 6 weeks; none is dated after 4 July 2027. Best overlap estimate: about 39 events in one week. Evidence: `research/t1_event_census.md`. Limit: quotes came through a fetch tool that summarises, except 2 PDFs. | Open. The feed has two populations: about 46 durable items (annual, recurring, season) and a weekly flow of small local events. Joshua decides the scope and the bar (design O1). |
| T1b | The main tourism data is in HTML | **Wrong.** The two tourism offices have empty HTML calendars. The data (75 of 112 events) is in PDFs with changing file names, and one PNG. | PDF text must be read in version 1, or the largest source is a hole (design O6). |
| T1c | A date quote holds the full date | **Wrong for lists.** Rows give the day only ("28") or day and month ("5 Dec"). The year is in a header, a title or the URL. | The value-in-quote check needs a second quote for month and year. Test in T2. |
| T1d | Sources mostly agree | **Wrong.** 14 contradictions in 23 events that have 2 or more sources. Tourism pages show last year's dates. One agency differs from the organiser in 4 of 6 rows. | Supports owner rank. "Each conflict goes to review" gives too many reviews (design O4). |
| T1e | Pages show an age limit | **Wrong.** No page showed one. | The age mark has no data. Keep or remove: Joshua decides. |
| T2 | Code can find each field value in its quote, and each quote on its page | not tested | |
| T3 | A content hash skips an unchanged page | not tested | |
| T4 | The cheapest model loses no quality against a stronger one | not tested | |
| T5 | Hidden or hostile page text cannot change a fact, and cannot pass in an `about` sentence | not tested | |
| T6 | Each `action` and `source` link on a card gives a working page | not tested | |
| T7 | The page's own summary (meta description) is a coherent `about` text for a one-event page | not tested | |
| T8 | A rule in code can select the headline events | **First pass, by hand on the T1 table (2026-11-22): not good enough alone.** Rule: (annual, season or a run of days) and (own site, ticket page, or 2 or more independent sources). It selects 6: FynArts Festival, FynArts Select weekend, Whale Festival, Kalfiefees, Fernkloof Flower Show, Wine & Food Festival. It misses the whale season (one source read), Wines2Whales (one source read) and each market. Joshua has not marked the list yet. | Proposed: code proposes, Joshua confirms and can promote. Waits for Joshua. |

## Still untested

- T1: one research agent lists the sources and records which source lists which event. It estimates the total from the overlap (capture-recapture, a lower limit). Wrong if: the count is far above 30, or the estimate is far above the count.
- T2: extract 10 real pages, then run the two code checks. Joshua reviews the failures. Wrong if: dates in words ("every Saturday", "June to November") fail the value-in-quote check.
- T3: fetch the same 10 pages two times, one day apart, and compare the hashes. Wrong if: the hash changes when the visible text did not.
- T4: run 2 or 3 low-cost models on the confirmed set from T2. Compare false facts, missed events, "needs review" rate and measured cost.
- T5: 2 or 3 test pages made by hand, with an injected instruction and with hidden text. Wrong if: a stored fact or an `about` text changes.
- T6: request each link at ingest and record the status.
- T7: in the review of T2, Joshua marks each `about` as "describes the event: yes or no".
