# Agent test: a new Claude with only the four tools of the feed

Written by `research/acceptance/agent_test.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.
Questions 1 to 3 are one conversation. Each other question is a new conversation.
Code made the checks below against the text that the tools returned and against the agreed shape (`expected.md`).

| # | Question | Tools called | Size | Checks by code | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| 1 | What is on in Hermanus for my clients from 20 to 27 June 202 | what_is_on | 121 words, 0 quotes | PASS |  | 0.0353 |
| 2 | The same dates, a second guest: a couple in their 60s who lo | none | 107 words, 0 quotes | PASS |  | 0.0186 |
| 3 | The same dates, a third guest: a family with two children of | none | 148 words, 0 quotes | PASS |  | 0.0159 |
| 4 | My clients have no dates yet. When is the best time to go to | when_to_go | 122 words, 0 quotes | PASS |  | 0.0706 |
| 5 | Tell me more about the FynArts Festival in June 2027. How su | what_is_on, tell_me_more | 125 words, 1 quotes | PASS |  | 0.0371 |
| 6 | I last looked on 1 November 2026. What changed in Hermanus? | what_changed | 150 words, 0 quotes | PASS |  | 0.1301 |
| 7 | Is the Hermanus Whale Festival on in October 2027? | what_is_on | 100 words, 0 quotes | PASS |  | 0.0326 |

- The selections for guest 2 and guest 3 differ: **yes**.
  - Guest 2 (wine and art, no crowds): FynArts Festival, Hermanuspietersfontein Food and Wine Market, Southern Right Whales
  - Guest 3 (family, children 8 and 11): Akwaaba Market, Food and craft market at the Hermanus Cricket Club, Hermanus Park Run, Hermanus Whale Watching Experience, Southern Right Whales
- Measured cost of the 7 answers: 0.340222 US dollars.

## Question 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`

Checks: calls what_is_on: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**6 of 13 items** in the feed for 20–27 June 2027:

- FynArts Festival — 24 June–4 July 2027 — Confirmed, programme not stated
- Southern Right Whales — June–November — Season
- Hermanus Whale Watching Experience (boat) — June–November — Season
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde — Sat 26 June — From a weekly rule, confirm near the date
- Akwaaba Market — Sat 26 June — From a weekly rule, confirm near the date
- Hermanus Country Market — all year — Season

**Left out:** monthly art walks and markets, another Saturday market and parkruns.
**Not covered:** the feed does not include Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can show the proof for any item.

## Question 2

> The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

**3 of 13 items** fit wine, art and fewer crowds, 20–27 June 2027:

- FynArts Festival — 24 June–4 July 2027 — Confirmed, programme not stated — for art
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde — Sat 26 June — From a weekly rule, confirm near the date — for wine, though its source says Saturdays are busy
- Southern Right Whales — June–November — Season

**Left out:** other markets, monthly art walks and markets (not on these dates), a whale-watching boat trip and parkruns.
**Not covered:** the feed does not include Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za. I can show the proof for any item.

## Question 3

> The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

**5 of 13 items** for a family with children of 8 and 11, 20–27 June 2027:

- Southern Right Whales — June–November — Season
- Hermanus Whale Watching Experience (boat) — June–November — Season. The feed does not state an age limit, so check this with the operator.
- Food and craft market at the Hermanus Cricket Club — Sat 26 June — From a weekly rule, confirm near the date
- Akwaaba Market — Sat 26 June — From a weekly rule, confirm near the date
- Hermanus Park Run — Sat 26 June — From a weekly rule, confirm near the date

**Left out:** an arts festival, wine and country markets, monthly art walks and markets (not on these dates) and a second parkrun.
**Not covered:** the feed does not include Quicket or Webtickets.

**Sources:** hermanus-tourism.co.za, southernrightcharters.co.za, xplorio.com. I can show the proof for any item.

## Question 4

> My clients have no dates yet. When is the best time to go to Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`

Checks: calls when_to_go: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**5 of 14 items: the best window is June to November, which is whale season. September to early October gives your clients the most on top of the whales.**

- Southern Right Whales, June to November, Hermanus: Season
- FynArts Festival, 24 June to 4 July 2027: Confirmed, programme not stated
- Hermanus Flower and Eco Fair, September: Season
- Hermanus Adventure Week, September: Season
- Whale Festival, early October: Not confirmed, no dates yet (last held 2 to 4 October 2026)

I left out the monthly markets, the art walks, a whale-watching boat trip and an art exhibition that has already happened.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, hermanusfynarts.co.za, xplorio.com, hermanuswhalefestival.co.za. I can get proof for any item.

## Question 5

> Tell me more about the FynArts Festival in June 2027. How sure is the date?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-01", "to_date": "2027-06-30"})`, `tell_me_more({"ids": [151]})`

Checks: calls tell_me_more: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 2 or less: pass; names a source: pass

The dates are firm: the festival's own website gives Thu 24 June to Sun 4 July 2027. It doesn't yet say what's on each day, so check the programme before you book any single event.

Showing 1 of the 13 items on in Hermanus in June 2027:

- **FynArts Festival**, 24 June – 4 July 2027, Hermanus. Confirmed, programme not stated.

What the page says: "24 June 2027 – 4 July 2027". It has run every year since 2013, and it was last checked today with no changes. The venue and prices aren't given.

Left out: weekly and monthly markets, art walks, whale watching and parkruns.

The feed doesn't cover Quicket or Webtickets.

Source: hermanusfynarts.co.za. I can send the full link if you'd like it.

## Question 6

> I last looked on 1 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-01"})`

Checks: calls what_changed: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass

**Nothing changed since 1 November, but there are 151 new items. The feed first saw all of them today (23 November), so it can't tell which ones were really added after your last look.** Here are 7 of the 151, all still to come:

- Hermanuspietersfontein Food and Wine Market, Saturdays, Hemel-en-Aarde: From a weekly rule, confirm near the date
- KliK arts festival, 27–29 Nov 2026, Kleinmond: Confirmed, programme not stated
- Alan Committie Live, 28 Nov 2026: Confirmed
- Oysters & Bubbles, 29 Nov 2026, Stanford: Confirmed
- Hawston Sea Festival, 5 Dec 2026: Confirmed
- FynArts Old Harbour Sunset Concert, 6 Mar 2027: Confirmed
- FynArts Festival, 24 Jun–4 Jul 2027: Confirmed, programme not stated

**Left out:** past events, duplicates, local community items, workshops, sport and smaller shows.
The feed doesn't cover Quicket or Webtickets.

**Sources:** whalecoast.info, hermanusfynarts.co.za, hermanus-tourism.co.za. I can show the proof for any item.

## Question 7

> Is the Hermanus Whale Festival on in October 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-10-01", "to_date": "2027-10-31"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; says not confirmed: pass; gives no day in October 2027: pass

The 2027 dates for the Hermanus Whale Festival are not out yet. It is held every year and last ran Fri 2 to Sun 4 October 2026, but no page gives dates for 2027.

2 of the 14 items in the feed for October 2027:

- **Hermanus Whale Festival**, October 2027: Not confirmed, no dates yet
- **Southern Right Whales**, June to November: Season

I left out the markets, the art walks, the parkruns and a second card for the same festival.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, hermanuswhalefestival.co.za. I can send the proof for either item.

