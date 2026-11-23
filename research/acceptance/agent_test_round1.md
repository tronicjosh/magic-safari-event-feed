# Agent test: a new Claude with only the four tools of the feed

Written by `research/acceptance/agent_test.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.
Questions 1 to 3 are one conversation. Each other question is a new conversation.
Code made the checks below against the text that the tools returned and against the agreed shape (`expected.md`).

| # | Question | Tools called | Size | Checks by code | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| 1 | What is on in Hermanus for my clients from 20 to 27 June 202 | what_is_on | 162 words, 0 quotes | FAIL | 150 words or less | 0.0373 |
| 2 | The same dates, a second guest: a couple in their 60s who lo | none | 157 words, 0 quotes | FAIL | 150 words or less | 0.0181 |
| 3 | The same dates, a third guest: a family with two children of | none | 196 words, 0 quotes | FAIL | 150 words or less | 0.0185 |
| 4 | My clients have no dates yet. When is the best time to go to | when_to_go | 193 words, 0 quotes | FAIL | 150 words or less | 0.0745 |
| 5 | Tell me more about the FynArts Festival in June 2027. How su | what_is_on, tell_me_more | 189 words, 2 quotes | FAIL | 150 words or less | 0.0387 |
| 6 | I last looked on 1 November 2026. What changed in Hermanus? | what_changed | 186 words, 0 quotes | FAIL | 150 words or less | 0.1319 |
| 7 | Is the Hermanus Whale Festival on in October 2027? | what_is_on | 142 words, 0 quotes | PASS |  | 0.0329 |

- The selections for guest 2 and guest 3 differ: **yes**.
  - Guest 2 (wine and art, no crowds): FynArts Festival, Hermanuspietersfontein Food and Wine Market, Southern Right Whales
  - Guest 3 (family, children 8 and 11): Akwaaba Market, Benguela Cove Parkrun, Food and craft market at the Hermanus Cricket Club, Hermanus Park Run, Hermanus Whale Watching Experience, Southern Right Whales
- Measured cost of the 7 answers: 0.351900 US dollars.

## Question 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`

Checks: calls what_is_on: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**5 of the feed's 13 items** for Hermanus, 20–27 June 2027:

1. **FynArts Festival**, Thu 24 June – Sun 4 July. *Confirmed, programme not stated:* check which events fall on the clients' days.
2. **Hermanus Whale Watching Experience** (boat trips), June to November. *Season:* confirm with the operator.
3. **Southern Right Whales**, seen from the shore, June to November. *Season.*
4. **Hermanuspietersfontein Food and Wine Market**, Hemel-en-Aarde, Sat 26 June. *From a weekly rule, confirm near the date.*
5. **Akwaaba Market**, Sat 26 June, 09:00–14:00. *From a weekly rule, confirm near the date.*

**Left out:** the monthly art walk and markets, because the first Friday, Saturday and Sunday of the month all fall outside these dates. I also left out the Cricket Club market, the Country Market (the feed gives no day for it) and two Saturday parkruns.

**Not covered:** the feed doesn't include events listed on Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can show the proof for any item.

## Question 2

> The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

**3 of the feed's 13 items** fit a couple who love wine and art and dislike crowds, 20–27 June 2027:

1. **FynArts Festival**, Thu 24 June – Sun 4 July. It's the art highlight, but it's a festival, so pick smaller events once the programme is out. *Confirmed, programme not stated:* check which events fall on their days.
2. **Hermanuspietersfontein Food and Wine Market**, Hemel-en-Aarde, Sat 26 June. It's the wine match, but the page says Saturdays are busy, so suggest arriving early. *From a weekly rule, confirm near the date.*
3. **Southern Right Whales**, seen from the shore at their own pace, June to November. *Season.*

**Left out:** the other markets and the boat trips, which are likely busier. I also left out the parkruns. The monthly art walk falls outside their dates.

**Not covered:** the feed doesn't include events listed on Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za. I can show the proof for any item.

## Question 3

> The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

**5 of the feed's 13 items** fit a family with children of 8 and 11, 20–27 June 2027:

1. **Southern Right Whales**, seen from the shore, June to November. Easy, free-form fun for the children. *Season.*
2. **Hermanus Whale Watching Experience** (boat trips), June to November. Ask the operator about minimum ages. *Season:* confirm with the operator.
3. **Food and craft market at the Hermanus Cricket Club**, Sat 26 June, in the morning. *From a weekly rule, confirm near the date.*
4. **Akwaaba Market**, Sat 26 June, 09:00–14:00. *From a weekly rule, confirm near the date.*
5. **Hermanus Park Run**, Sat 26 June, 08:00. The feed marks it as routine local life, but it can be a fun family outing. *From a weekly rule, confirm near the date.*

**Left out:** FynArts, which may suit them once the programme is out. I also left out the wine market, the Benguela Cove parkrun and the Country Market (the feed gives no day for it). The monthly art walk and markets fall outside their dates.

**Not covered:** the feed doesn't include events listed on Quicket or Webtickets.

**Sources:** hermanus-tourism.co.za, southernrightcharters.co.za, xplorio.com. I can show the proof for any item.

## Question 4

> My clients have no dates yet. When is the best time to go to Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`

Checks: calls when_to_go: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**I'd suggest June to November.** That's the whale season, and the main festivals fall inside it. I've picked 6 of the 14 items the feed has:

- **Southern Right Whales and boat whale-watching:** June to end of November. *Season: months, no year stated.*
- **FynArts Festival:** Thu 24 June to Sun 4 July 2027. *Confirmed, programme not stated.*
- **Hermanus Whale Festival:** last held 2–4 October 2026. *Not confirmed, no dates yet: check the organiser nearer the time.*
- **Hermanus Flower and Eco Fair:** September. *Season: months, no year stated.*
- **Hermanus Adventure Week:** September. *Season: months, no year stated.*
- **First Friday Artwalk:** held on the first Friday of every month, all year. *Season: months, no year stated.*

**Left out:** three monthly or year-round markets (De Wet Hall in Onrus, Art in the Park and the Country Market). I also left out the Annual Art Exhibition, which ends 25 November 2026. Some items appeared twice in the feed, and I've listed them once.

**Not covered:** the feed doesn't collect events from Quicket or Webtickets.

**Sources:** hermanus-tourism.co.za, southernrightcharters.co.za, hermanusfynarts.co.za, hermanuswhalefestival.co.za, xplorio.com, whalecoast.info. I can send the source evidence for any of these items.

## Question 5

> Tell me more about the FynArts Festival in June 2027. How sure is the date?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-01", "to_date": "2027-06-30"})`, `tell_me_more({"ids": [151]})`

Checks: calls tell_me_more: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 2 or less: pass; names a source: pass

**The festival dates are confirmed, but the daily programme is not stated.** This is 1 of the 13 items the feed has for Hermanus in June 2027.

- **FynArts Festival**, Thu 24 June – Sun 4 July 2027, Hermanus. It's an arts festival that has been held every year since 2013. **Confirmed, programme not stated:** the festival's own site gives the first and last day, so the date range is solid. It doesn't say what's on each day, so don't promise a specific event or day yet. Check the programme before booking.

**Proof:** the festival site says "24 June 2027 – 4 July 2027" and "Over ten inspiring days in June, Hermanus becomes a meeting place." This was last checked today, and the date hasn't changed.

**Also worth knowing:**
- The festival runs into July, so make sure the trip dates cover the days you want.
- The venue and prices are not stated.

**Left out:** the other 12 June items, which are markets, art walks, whale season and parkruns. The feed doesn't cover Quicket or Webtickets.

**Source:** hermanusfynarts.co.za. I can send the full link if you need it.

## Question 6

> I last looked on 1 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-01"})`

Checks: calls what_changed: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: FAIL; quotes of a page: 0 or less: pass

**Nothing changed in Hermanus since 1 November, but every item is new to the feed (151 items, 0 changes).** The feed first saw all of them today, 23 November. "New" means new to the feed, not newly announced. Here are 8 of 151 that are still ahead:

- **Hermanus Music Society Concert**, Fri 27 Nov: Confirmed.
- **Kleinmond Inniebos Kunstefees (KliK)**, 27–29 Nov: Confirmed, programme not stated.
- **Oysters & Bubbles**, Stanford, Sun 29 Nov: Confirmed.
- **Hermanuspietersfontein Food and Wine Market**, Saturdays: From a weekly rule, confirm near the date.
- **Southern right whales**, June to end November: Season. Only about a week is left this year.
- **Hawston Sea Festival**, Sat 5 Dec: Confirmed.
- **FynArts Old Harbour Sunset Concert**, Sat 6 Mar 2027: Confirmed.
- **FynArts Festival**, 24 Jun–4 Jul 2027: Confirmed, programme not stated.

**Left out:** events already past, repeat listings of the same event from different sites, and items the feed marks as routine local life (quizzes, parkruns, bingo).

**Not covered:** the feed doesn't collect Quicket or Webtickets listings.

**Sources:** whalecoast.info, hermanusfynarts.co.za, hermanus-tourism.co.za. I can show the proof for any item.

## Question 7

> Is the Hermanus Whale Festival on in October 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-10-01", "to_date": "2027-10-31"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; says not confirmed: pass; gives no day in October 2027: pass

I can't confirm it yet. The Whale Festival is held every year, but no page gives dates for 2027. It was last held on Fri 2 – Sun 4 October 2026.

Showing 2 of 14 items:

- **Hermanus Whale Festival:** last held 2–4 Oct 2026, with no date for 2027 yet. Two sources list it. *Not confirmed, no dates yet: check the organiser nearer the time.*
- **Southern right whales / whale-watching trips:** whales are around from June to the end of November. *Season: months, with no year stated.*

I left out the weekly Saturday markets, the monthly art walk and markets, and the parkruns. I can list them if they suit the guest. The feed doesn't cover Quicket or Webtickets, so ticketed events listed only there won't show up here.

Sources: hermanuswhalefestival.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can send proof for either item.

