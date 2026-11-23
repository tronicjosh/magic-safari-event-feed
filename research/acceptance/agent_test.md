# Agent test: a new Claude with only the four tools of the feed

Written by `research/acceptance/agent_test.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.
Questions 1 to 3 are one conversation. Each other question is a new conversation.
Code made the checks below against the text that the tools returned and against the agreed shape (`expected.md`).

| # | Question | Tools called | Size | Checks by code | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| 1 | What is on in Hermanus for my clients from 20 to 27 June 202 | what_is_on | 126 words, 0 quotes | PASS |  | 0.0337 |
| 2 | The same dates, a second guest: a couple in their 60s who lo | none | 129 words, 0 quotes | PASS |  | 0.0163 |
| 3 | The same dates, a third guest: a family with two children of | none | 125 words, 0 quotes | PASS |  | 0.0146 |
| 4 | My clients have no dates yet. When is the best time to go to | when_to_go | 121 words, 0 quotes | PASS |  | 0.0736 |
| 5 | Tell me more about the FynArts Festival in June 2027. How su | what_is_on, tell_me_more | 123 words, 2 quotes | PASS |  | 0.0363 |
| 6 | I last looked on 1 November 2026. What changed in Hermanus? | what_changed | 111 words, 0 quotes | PASS |  | 0.0195 |
| 7 | Is the Hermanus Whale Festival on in October 2027? | what_is_on | 108 words, 0 quotes | PASS |  | 0.0334 |

- The selections for guest 2 and guest 3 differ: **yes**.
  - Guest 2 (wine and art, no crowds): FynArts Festival, Hermanus Whale Watching Experience, Hermanuspietersfontein Food and Wine Market
  - Guest 3 (family, children 8 and 11): Food and craft market at the Hermanus Cricket Club, Hermanus Park Run, Hermanus Whale Watching Experience, Southern Right Whales
- Measured cost of the 7 answers: 0.227398 US dollars.

## Question 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`

Checks: calls what_is_on: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

I'm showing **6 of the 13 items** in the feed for 20 to 27 June 2027:

- **FynArts Festival**: 24 June to 4 July 2027, Hermanus. Confirmed, programme not stated
- **Southern Right Whales**: June to November. Season
- **Hermanus Whale Watching Experience**: June to November. Season
- **Hermanuspietersfontein Food and Wine Market**: Sat 26 June, Hemel-en-Aarde. From a weekly rule, confirm near the date
- **Akwaaba Market**: Sat 26 June. From a weekly rule, confirm near the date
- **Hermanus Country Market**: all year. Season

**Left out:** monthly art walks and markets (their first-of-the-month days fall outside these dates), a second craft market, and two parkruns.

The feed doesn't cover Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can send the evidence for any item.

## Question 2

> The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

For this couple I'd suggest **3 of the 13 items**:

- **FynArts Festival**: 24 June to 4 July 2027, Hermanus. Confirmed, programme not stated. It's an art festival. The feed says nothing about crowd sizes, so check the programme for smaller events.
- **Hermanuspietersfontein Food and Wine Market**: Sat 26 June, Hemel-en-Aarde. From a weekly rule, confirm near the date. It fits their love of wine, but its page says Saturdays are busy.
- **Hermanus Whale Watching Experience**: June to November. Season. It's a nature outing they can take at a slower pace.

**Left out:** other markets, the parkruns, and monthly art events whose first-of-the-month days fall outside these dates.

The feed doesn't cover Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can send the evidence for any item.

## Question 3

> The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?

Tools called: none

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 13: pass; gives a tag for how sure: pass

For the family I'd suggest **4 of the 13 items**:

- **Southern Right Whales**: June to November, Hermanus. Season
- **Hermanus Whale Watching Experience**: June to November. Season
- **Hermanus Park Run**: Sat 26 June, 08:00. From a weekly rule, confirm near the date. It's a run they can take part in. The feed doesn't give age rules, so check those.
- **Food and craft market at the Hermanus Cricket Club**: Sat 26 June. From a weekly rule, confirm near the date

**Left out:** the arts festival, other markets, the wine market, a second parkrun, and monthly art events whose first-of-the-month days fall outside these dates.

The feed doesn't cover Quicket or Webtickets.

**Sources:** hermanus-tourism.co.za, southernrightcharters.co.za, xplorio.com. I can send the evidence for any item.

## Question 4

> My clients have no dates yet. When is the best time to go to Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`

Checks: calls when_to_go: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**The best time to go is June to November, which is whale season.** For the most to do, choose September, which also has two yearly festivals. For culture, choose late June.

5 of 14:
- Southern Right Whales, June to November: Season
- FynArts Festival, 24 June to 4 July 2027: Confirmed, programme not stated
- Hermanus Flower and Eco Fair, September: Season
- Hermanus Adventure Week, September: Season
- Whale Festival: Not confirmed, no dates yet

Left out: a whale-watching boat trip, monthly markets and art walks, a duplicate Whale Festival listing and an art exhibition in November 2026.
The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, hermanusfynarts.co.za, xplorio.com, hermanuswhalefestival.co.za. I can show the proof for any of these.

## Question 5

> Tell me more about the FynArts Festival in June 2027. How sure is the date?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-01", "to_date": "2027-06-30"})`, `tell_me_more({"ids": [151]})`

Checks: calls tell_me_more: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 2 or less: pass; names a source: pass

The festival is Thu 24 June – Sun 4 July 2027 in Hermanus. **Confirmed, programme not stated**

**How sure:** The organiser's own website gives the dates as "24 June 2027 – 4 July 2027." We last checked them today (23 Nov 2026), and they haven't changed. The page gives only the first and last day, so it doesn't show what's on each day.

**Other details:**
- The festival has run every year since 2013 and lasts "ten inspiring days in June."
- It's one of 13 items the feed lists for Hermanus in June 2027.
- The venue and price aren't stated.

**Before booking:** Check the daily programme with the organiser.

**Source:** hermanusfynarts.co.za. I can send the full link if you need it.

## Question 6

> I last looked on 1 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-01"})`

Checks: calls what_changed: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass

I can't tell you what changed since 1 November. The feed only started collecting Hermanus today, 23 November 2026, so it has nothing earlier to compare against. It found 151 items in that first collection, and none of them are marked as new or changed.

The feed doesn't cover Quicket or Webtickets for Hermanus.

I can still help in two ways:
- **If you have trip dates:** I can list what's on in Hermanus between them.
- **If you don't have dates yet:** I can show the seasons and yearly events month by month.

If you check back after today, I can show you exactly what changed since this first collection.

## Question 7

> Is the Hermanus Whale Festival on in October 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-10-01", "to_date": "2027-10-31"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; says not confirmed: pass; gives no day in October 2027: pass

Nobody has announced dates for the Hermanus Whale Festival in October 2027 yet. It's an annual event, and the most recent one ran Fri 2 to Sun 4 October 2026. That might suggest early October, but I can't give it a 2027 date. Check with the organiser closer to the time before you book.

- **Whale Festival, Hermanus:** Not confirmed, no dates yet

The whale-watching season itself runs from June to the end of November, so October falls inside it. Its listing gives months but no year.

I don't have Quicket or Webtickets listings.

Sources: hermanuswhalefestival.co.za, hermanus-tourism.co.za, southernrightcharters.co.za. I can show the source pages for any of this.

