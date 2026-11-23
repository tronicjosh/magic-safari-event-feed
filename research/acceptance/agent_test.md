# Agent test: a new Claude with only the four tools of the feed

Written by `research/acceptance/agent_test.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.
Questions 1 to 3 are one conversation. Each other question is a new conversation.
Code made the checks below against the text that the tools returned and against the agreed shape (`expected.md`).

| # | Question | Tools called | Size | Checks by code | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| 1 | What is on in Hermanus for my clients from 20 to 27 June 202 | what_is_on | 140 words, 0 quotes | PASS |  | 0.0397 |
| 2 | The same dates, a second guest: a couple in their 60s who lo | find, find | 125 words, 0 quotes | PASS |  | 0.0529 |
| 3 | The same dates, a third guest: a family with two children of | find, find | 138 words, 0 quotes | PASS |  | 0.0292 |
| 4 | My clients have no dates yet. When is the best time to go to | when_to_go | 149 words, 0 quotes | PASS |  | 0.0774 |
| 5 | Tell me more about the FynArts Festival in June 2027. How su | find, tell_me_more | 138 words, 2 quotes | PASS |  | 0.0365 |
| 6 | I last looked on 1 November 2026. What changed in Hermanus? | what_changed | 79 words, 0 quotes | PASS |  | 0.0212 |
| 7 | Is the Hermanus Whale Festival on in October 2027? | find | 95 words, 0 quotes | PASS |  | 0.0245 |

- The selections for guest 2 and guest 3 differ: **yes**.
  - Guest 2 (wine and art, no crowds): FynArts Festival, Hermanus Whale Watching Experience, Hermanuspietersfontein Food and Wine Market
  - Guest 3 (family, children 8 and 11): Food and craft market at the Hermanus Cricket Club, Hermanus Park Run, Hermanus Whale Watching Experience, Southern Right Whales
- Measured cost of the 7 answers: 0.281390 US dollars.

## Question 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`

Checks: calls what_is_on: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 12: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**I'm showing 6 of 12 items for 20–27 June 2027.** The highlights are the FynArts Festival opening and the start of whale season.

- FynArts Festival, 24 June – 4 July 2027. Confirmed, programme not stated. [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)
- Southern Right Whales, June – November. Season. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
- Hermanus Whale Watching Experience, June – November. Season. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde, Sat 26 June 2027. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Akwaaba Market, Sat 26 June 2027. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Country Market, all year. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

**Left out:** one more Saturday market, two parkruns and three monthly first-weekend events.

The feed does not cover Quicket or Webtickets.

I can show you the proof for any of these items.

## Question 2

> The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?

Tools called: `find({"place": "Hermanus", "text": "wine"})`, `find({"place": "Hermanus", "text": "art"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 12: pass; gives a tag for how sure: pass

**I'm showing 3 of 12 items for 20–27 June 2027 that suit a couple who love wine and art.**

- FynArts Festival, 24 June – 4 July 2027. Confirmed, programme not stated. It's the art highlight; ask the organiser for its smaller events. [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde, Sat 26 June 2027. From a weekly rule, confirm near the date. The page says Saturdays are busy, so they should arrive early. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Whale Watching Experience, June – November. Season. It's a calm outing at sea. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)

**Left out:** other markets, parkruns and monthly art events whose dates fall outside the trip.

The feed does not cover Quicket or Webtickets.

I can show you the proof for any of these items.

## Question 3

> The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?

Tools called: `find({"place": "Hermanus", "text": "family"})`, `find({"place": "Hermanus", "text": "kids"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; starts with how many of 12: pass; gives a tag for how sure: pass

**I'm showing 4 of 12 items for 20–27 June 2027.** None of them is marked for children, and the feed's only family festival is in November 2026.

- Southern Right Whales, June – November. Season. Watching from the shore is easy with children. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
- Hermanus Whale Watching Experience, June – November. Season. Check the minimum age for children. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
- Hermanus Park Run, Sat 26 June 2027. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Food and craft market at the Hermanus Cricket Club, Sat 26 June 2027. From a weekly rule, confirm near the date. [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)

**Left out:** the arts festival, the wine market, other markets and monthly events whose dates fall outside the trip.

The feed does not cover Quicket or Webtickets.

I can show you the proof for any of these items.

## Question 4

> My clients have no dates yet. When is the best time to go to Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`

Checks: calls when_to_go: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; names what the feed does not cover: pass

**Go between June and November, the Southern Right whale season.** Late June to early July adds FynArts, and September to early October adds festivals.

6 of 18 items:
- Southern Right Whales · June–November · Season · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
- FynArts Festival · 24 June – 4 July 2027 · Confirmed, programme not stated · [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)
- Hermanus Adventure Week · September · Season · [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)
- Hermanus Flower and Eco Fair · September · Season · [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)
- Whale Festival · last held 2–4 October 2026 · Not confirmed, no dates yet · [hermanuswhalefestival.co.za](https://hermanuswhalefestival.co.za/)
- Hermanus First Friday Artwalk · first Friday of every month · From a rule of the page, check the day · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Left out: weekly and monthly markets, parkruns, a whale-watching boat trip, and a November 2026 art exhibition.
The feed doesn't cover Quicket or Webtickets.

I can send the proof for any item.

## Question 5

> Tell me more about the FynArts Festival in June 2027. How sure is the date?

Tools called: `find({"place": "Hermanus", "text": "FynArts"})`, `tell_me_more({"ids": [151]})`

Checks: calls tell_me_more: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 2 or less: pass; names a source: pass

The FynArts Festival in Hermanus runs **Thu 24 June – Sun 4 July 2027**. Tag: **Confirmed, programme not stated**. Source: [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)

**How sure the date is**
- The festival's own website states the dates: "24 June 2027 – 4 July 2027". The feed last checked this on 23 Nov 2026, and nothing has changed.
- The page gives only the first and last day. It doesn't say what happens on each day in between, so check the programme before booking anything for a set day.
- The festival runs past June into early July. The same page also says "ten inspiring days in June", so confirm the end date with the organiser.
- The festival has been held every year since 2013. The venue and prices aren't given.

I can also show you the 2026 dates for comparison.

## Question 6

> I last looked on 1 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-01"})`

Checks: calls what_changed: pass; each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass

The feed can't tell you what changed since 1 November, because it first collected Hermanus today (23 November 2026). It holds 151 items from that first collection, but it can't show which of them are new or changed since your last look.

The feed also doesn't cover Quicket or Webtickets.

I can list what's on in Hermanus for your guest's trip dates, or show the best months to go if the trip has no dates yet. Which would help?

## Question 7

> Is the Hermanus Whale Festival on in October 2027?

Tools called: `find({"place": "Hermanus", "text": "Whale Festival"})`

Checks: each site is from the feed: pass; each date is from the feed or the question: pass; 150 words or less: pass; quotes of a page: 0 or less: pass; names a source: pass; gives a tag for how sure: pass; says not confirmed: pass; gives no day in October 2027: pass

**Probably, but no 2027 dates are out yet.** The Hermanus Whale Festival takes place every year, and no page gives its October 2027 dates. It was last held Fri 2 – Sun 4 October 2026.

- Hermanus Whale Festival, 2027 dates not yet published, Hermanus. Not confirmed, no dates yet. [hermanuswhalefestival.co.za](https://hermanuswhalefestival.co.za/)

Check with the organiser before booking anything around the festival. If it keeps the same early-October weekend, the dates would fall around then, but no page says so.

The feed doesn't cover Quicket or Webtickets.

Would you like the source details for this festival?

