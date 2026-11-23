# Scenarios: what a designer can ask, well or badly

Written by `research/acceptance/scenarios.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has only the four tools and the server instructions of the feed.
**14 of 20 scenarios pass the checks by code.** Measured cost: 0.762562 US dollars.

| Scenario | Last question | Tools called | Words | Checks | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| dated_one_day | Is anything on in Hermanus on Saturday 5 December 2026? | what_is_on | 147 | PASS |  | 0.0444 |
| dated_quiet_day | Is anything on in Hermanus on Tuesday 9 March 2027? | what_is_on | 114 | FAIL | 1 quotes of a page | 0.0350 |
| dated_past | What was on in Hermanus from 1 to 31 March 2026? | what_is_on | 138 | PASS |  | 0.0374 |
| dated_june_2028 | What is on in Hermanus from 3 to 10 June 2028? | what_is_on | 171 | FAIL | 171 words (limit 150) | 0.0397 |
| dated_2029 | What is on in Hermanus from 10 to 17 June 2029? | what_is_on | 169 | FAIL | 169 words (limit 150) | 0.0431 |
| nodates_recurring | What recurring or regular events does Hermanus have? | when_to_go | 176 | FAIL | 176 words (limit 170) | 0.0790 |
| nodates_weekly_market | Is there a weekly market in Hermanus? | find | 118 | PASS |  | 0.0330 |
| nodates_wine | My guests love wine. No dates yet. What does Hermanus have | find | 145 | PASS |  | 0.0396 |
| named_brief_market | Is the Hermanus Country Market on on a Saturday? | find, tell_me_more | 100 | FAIL | 1 quotes of a page | 0.0305 |
| named_kalfiefees | When is Kalfiefees? | find | 77 | PASS |  | 0.0262 |
| bad_town_inside | What is on in Stanford in the first week of December 2026? | find, what_is_on | 99 | PASS |  | 0.0577 |
| bad_gibberish | asdf qwer zxcv | none | 23 | PASS |  | 0.0138 |
| follow_proof | How sure is the date of the wine market? | what_is_on, tell_me_more | 100 | PASS |  | 0.0582 |
| changed_same_day | I last looked on 23 November 2026. What changed in Hermanu | what_changed | 85 | PASS |  | 0.0213 |
| named_fynarts | When is FynArts? | find | 74 | PASS |  | 0.0270 |
| subject_music | My guests love live music. What does Hermanus have? | find | 101 | FAIL | lacks /\d+ of (the )?\d+|\d+ items?/ | 0.0408 |
| subject_parkrun | Is there a parkrun in Hermanus? | find | 81 | PASS |  | 0.0250 |
| named_kalfiefees_2027 | Is Kalfiefees on in August 2027? | find | 75 | PASS |  | 0.0250 |
| subject_none | Is there a jazz festival in Hermanus? | find, find | 78 | PASS |  | 0.0396 |
| town_no_dates | What is there to do in Stanford? | find | 134 | PASS |  | 0.0461 |

## dated_one_day

### Turn 1

> Is anything on in Hermanus on Saturday 5 December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-05", "to_date": "2026-12-05"})`
Cost: 0.0444

<!-- answer -->
Yes. Three events are confirmed for Saturday 5 December, and several Saturday markets usually run that day. Here are 6 of the 15 items the feed has:

- Hawston Sea Festival, Sat 5 Dec, Hawston: Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Ubumnandi Summer Picnic, Sat 5 Dec, Hermanus: Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Stanford 100 Miler, Sat 5 Dec, Stanford: Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Akwaaba Market, Sat 5 Dec, Hermanus: From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanuspietersfontein Food and Wine Market, Sat 5 Dec, Hemel-en-Aarde: From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- De Wet Hall Onrus market, first Saturday of every month, Onrus: From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Left out: other markets, events that run across December, parkruns, and items held on Fridays or Sundays.

The feed doesn't cover Quicket or Webtickets.

I can show the proof for any of these.
<!-- end -->

## dated_quiet_day

### Turn 1

> Is anything on in Hermanus on Tuesday 9 March 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-03-09", "to_date": "2027-03-09"})`
Cost: 0.0350

<!-- answer -->
**No: the feed has no dated event in Hermanus on Tuesday 9 March 2027.** It has 4 items for that day, all of them all-year listings:

- Hermanus Country Market, Hermanus: listed as "throughout the year", but the page gives no day of the week. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

The other 3 can't fall on a Tuesday:
- Hermanus First Friday Artwalk: first Friday of the month. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- De Wet Hall market, Onrus: first Saturday of the month. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Art in the Park: first Sunday of the month. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)

The feed doesn't cover Quicket or Webtickets.

I can give you the proof for any item.
<!-- end -->

## dated_past

### Turn 1

> What was on in Hermanus from 1 to 31 March 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-03-01", "to_date": "2026-03-31"})`
Cost: 0.0374

<!-- answer -->
In March 2026 the feed has 7 items for Hermanus. Here are 6 of them:

- Lighthouse2Lighthouse Walk, 5–8 March 2026, Gansbaai: Confirmed, programme not stated. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Cape 1000 Classic Cars, 18 March 2026, Hermanus: Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Baardskeerdersbos Art Route, 27–29 March 2026, Gansbaai: Confirmed, programme not stated. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- Hermanus First Friday Artwalk, first Friday of every month: From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Art in the Park, first Sunday of the month: From a rule of the page, check the day. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- De Wet Hall Onrus market, first Saturday of every month, Onrus: From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Left out: one all-year market.

The feed does not cover Quicket or Webtickets.

I can show you the proof for any of these items.
<!-- end -->

## dated_june_2028

### Turn 1

> What is on in Hermanus from 3 to 10 June 2028?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2028-06-03", "to_date": "2028-06-10"})`
Cost: 0.0397

<!-- answer -->
Here are **6 of the 11 items** the feed has for Hermanus, 3–10 June 2028. No item has a confirmed date yet. The feed writes dates from rules only up to 20 May 2028, so the items below give their rule and no date.

- Southern Right Whales, June–November · Season · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
- Hermanus Whale Watching Experience, June–November · Season · [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
- Akwaaba Market, each Saturday · From a weekly rule, confirm near the date · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde, each Saturday · From a weekly rule, confirm near the date · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- De Wet Hall market, Onrus, first Saturday of every month · From a rule of the page, check the day · [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Art in the Park, first Sunday of the month · From a rule of the page, check the day · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)

Not shown: other markets, an art walk and parkruns.
The feed does not cover Quicket or Webtickets.

I can show you the proof for any item.
<!-- end -->

## dated_2029

### Turn 1

> What is on in Hermanus from 10 to 17 June 2029?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2029-06-10", "to_date": "2029-06-17"})`
Cost: 0.0431

<!-- answer -->
**I'm showing 6 of the 11 items in the feed.** Your dates are in the whale season, and the Saturday markets run every week.

- Southern Right Whales: June to November. Season. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
- Hermanus Whale Watching Experience: June to November. Season. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
- Akwaaba Market: every Saturday. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde: every Saturday. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Food and craft market at the Hermanus Cricket Club: every Saturday. From a weekly rule, confirm near the date. [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)
- Hermanus Country Market: all year. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

The feed only gives dates up to 31 December 2028, so it can't give exact dates for 2029. That's why I've shown the rules instead.

I left out the parkruns and the events on the first weekend of each month.

The feed doesn't cover Quicket or Webtickets.

I can show you the proof for any of these.
<!-- end -->

## nodates_recurring

### Turn 1

> What recurring or regular events does Hermanus have?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0790

<!-- answer -->
Hermanus has **9** weekly or monthly items, mostly markets and art. The list shows **6 of the 18 items** the feed has for the year.

- Akwaaba Market: each Saturday, 09:00–14:00. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanuspietersfontein Food and Wine Market: each Saturday, Hemel-en-Aarde. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Food and craft market at the Hermanus Cricket Club: Saturday mornings. From a weekly rule, confirm near the date. [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)
- Hermanus First Friday Artwalk: first Friday of every month. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Hermanus Art in the Park: first Sunday of the month. From a rule of the page, check the day. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- De Wet Hall market, Onrus: first Saturday of every month. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Not shown: the two Saturday parkruns, the Hermanus Country Market, the whale season and the yearly festivals and exhibitions.

The feed doesn't cover Quicket or Webtickets.

I can show the proof for any of these.
<!-- end -->

## nodates_weekly_market

### Turn 1

> Is there a weekly market in Hermanus?

Tools called: `find({"place": "Hermanus", "text": "market"})`
Cost: 0.0330

<!-- answer -->
Yes, there are three markets every Saturday in and near Hermanus.

These are 3 of the 12 markets in the feed:
- Akwaaba Market: each Saturday, 09:00–14:00, Hermanus. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- Food and craft market at the Hermanus Cricket Club: Saturday mornings, Hermanus. From a weekly rule, confirm near the date. [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)
- Hermanuspietersfontein Food and Wine Market: each Saturday, Hemel-en-Aarde. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

I left out the monthly markets, the year-round market, the one-off Christmas and Sunset markets, a church bazaar and the past markets.

The feed does not cover Quicket or Webtickets.

I can show you the proof for any of these markets.
<!-- end -->

## nodates_wine

### Turn 1

> My guests love wine. No dates yet. What does Hermanus have for them?

Tools called: `find({"place": "Hermanus", "text": "wine"})`
Cost: 0.0396

<!-- answer -->
I found 11 wine items in Hermanus. Since you have no dates yet, the steady option is the Saturday market. The other wine events coming up are all in the next week. Here are 5 of the 11:

- **Hermanuspietersfontein Food and Wine Market**: each Saturday, Hemel-en-Aarde. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- **The Blending Table: Create your own wine**: Sun 29 November 2026, Hermanus. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- **Oysters & Bubbles**: Sun 29 November 2026, Stanford. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- **Think & Drink**: Thu 26 November 2026, Stanford. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- **Deli Dining at Dal-Italia**: Fridays from 27 November to 25 December 2026, Hermanus. Confirmed. [xplorio.com](https://xplorio.com/hermanus/en/things-to-do/events)

I left out an open-air cinema night and 5 past events, including the Wine & Cheese Festival and Wines2Whales.

The feed doesn't cover Quicket or Webtickets.

I can show you the proof for any of these.
<!-- end -->

## named_brief_market

### Turn 1

> Is the Hermanus Country Market on on a Saturday?

Tools called: `find({"place": "Hermanus", "text": "Hermanus Country Market"})`, `tell_me_more({"ids": [7]})`
Cost: 0.0305

<!-- answer -->
I can't confirm a Saturday. The feed has the Hermanus Country Market, but its source doesn't say which day of the week it runs. The source only says the market is held "throughout the year" at the Hermanus Cricket Club.

- Hermanus Country Market, Hermanus Cricket Club: runs all year, day not stated. Tag: From a rule of the page, check the day. Source: [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Before you plan a Saturday around it, check the day with the organiser.

The feed doesn't cover listings on Quicket or Webtickets.

I can send you the proof for this item if you'd like it.
<!-- end -->

## named_kalfiefees

### Turn 1

> When is Kalfiefees?

Tools called: `find({"place": "Hermanus", "text": "Kalfiefees"})`
Cost: 0.0262

<!-- answer -->
The latest Kalfiefees ran **Wed 5 – Mon 10 August 2026** in Hermanus and is now over. Confirmed, programme not stated: [kalfiefees-hermanus.co.za](https://kalfiefees-hermanus.co.za/).

The feed doesn't have dates for 2027 yet, so check with the organiser before you plan around it. Two other sources list the same dates: [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/) and [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf). The Whale Coast listing places it in Onrus.

The feed doesn't cover Quicket or Webtickets.

I can show you the proof for these dates if you'd like.
<!-- end -->

## bad_town_inside

### Turn 1

> What is on in Stanford in the first week of December 2026?

Tools called: `find({"place": "Hermanus", "text": "Stanford"})`, `what_is_on({"place": "Hermanus", "from_date": "2026-12-01", "to_date": "2026-12-07"})`
Cost: 0.0577

<!-- answer -->
There are **3 Stanford events** in the feed for 1–7 December 2026, out of 16 events across the Hermanus area that week:

- **Stanford 100 Miler**, Sat 5 December 2026. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- **Sunset Sessions**, December 2026. Confirmed, programme not stated. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- **Christmas Lights Campaign**, December 2026. Confirmed, programme not stated. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)

I left out the events in other towns that week: Hermanus, Hawston, Gansbaai, Onrus and Hemel-en-Aarde. They include markets, festivals, a food event, an art walk and park runs.

The feed doesn't cover Quicket or Webtickets.

I can show you the proof for any of these.
<!-- end -->

## bad_gibberish

### Turn 1

> asdf qwer zxcv

Tools called: none
Cost: 0.0138

<!-- answer -->
What do you need for Hermanus? For example, what's on for certain trip dates, the best time to go, or a particular event?
<!-- end -->

## follow_proof

### Turn 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0396

<!-- answer -->
Here are **6 of the 12 items** the feed has for Hermanus from 20 to 27 June 2027:

1. FynArts Festival, 24 June to 4 July 2027. Confirmed, programme not stated. [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)
2. Southern Right Whales, June to November. Season. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/)
3. Hermanus Whale Watching Experience, June to November. Season. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
4. Hermanuspietersfontein Food and Wine Market, Sat 26 June 2027, Hemel-en-Aarde. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
5. Akwaaba Market, Sat 26 June 2027. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
6. Hermanus Country Market, all year. From a rule of the page, check the day. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

**Left out:** other markets, an art walk and parkruns.

**Not covered:** the feed doesn't cover Quicket or Webtickets.

I can give you the proof for any item.
<!-- end -->

### Turn 2

> How sure is the date of the wine market?

Tools called: `tell_me_more({"ids": [6]})`
Cost: 0.0186

<!-- answer -->
**It's not certain.** No page gives 26 June 2027 as a date. The feed calculated that Saturday from a weekly rule on one page, which says only: "Saturdays are busy market days." That page doesn't list opening hours or a venue. It also doesn't say clearly that a market runs every Saturday. The feed last checked the page on 23 November 2026.

**Tag:** From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

Before you plan around it, confirm the market and its hours directly with Hermanuspietersfontein, nearer to June.

I can also give you the proof for any other item.
<!-- end -->

## changed_same_day

### Turn 1

> I last looked on 23 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-23"})`
Cost: 0.0213

<!-- answer -->
**Nothing has changed in Hermanus since 23 November 2026.** No items are new or changed.

That date is today, and it's also the day the feed first collected Hermanus. So the feed can't compare against anything earlier. The 151 items it collected today aren't counted as new.

The feed does not cover Quicket or Webtickets.

If you share the trip dates, I can show what's on in Hermanus then. If there are no dates yet, I can show the seasons and yearly events by month.
<!-- end -->

## named_fynarts

### Turn 1

> When is FynArts?

Tools called: `find({"place": "Hermanus", "text": "FynArts"})`
Cost: 0.0270

<!-- answer -->
The next **FynArts Festival** in Hermanus runs **Thu 24 June – Sun 4 July 2027** (Confirmed, programme not stated). Source: [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)

The same organiser also has a **FynArts Old Harbour Sunset Concert** on **Sat 6 March 2027** (Confirmed). Source: [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)

I left out past FynArts events: the 2026 festival and the FynArts Select weekend that ended 22 November 2026.

The feed doesn't cover Quicket or Webtickets.

Would you like the proof for either date?
<!-- end -->

## subject_music

### Turn 1

> My guests love live music. What does Hermanus have?

Tools called: `find({"place": "Hermanus", "text": "music"})`
Cost: 0.0408

<!-- answer -->
The feed has **4 upcoming live-music events** that suit your guests, out of 8 coming music-and-shows items (with no dates given):

- Hermanus Music Society Concert: Fri 27 November 2026, Hermanus. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- The King of Pop Experience: Sat 28 November 2026, Hermanus. Confirmed. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- Sunset Sessions: December 2026, Stanford. Confirmed, programme not stated. [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)
- FynArts Old Harbour Sunset Concert: Sat 6 March 2027, Hermanus. Confirmed. [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)

I left out a DJ party, a drag show, a dance concert, comedy and past events.

The feed doesn't cover Quicket or Webtickets.

I can show proof for any of these.
<!-- end -->

## subject_parkrun

### Turn 1

> Is there a parkrun in Hermanus?

Tools called: `find({"place": "Hermanus", "text": "parkrun"})`
Cost: 0.0250

<!-- answer -->
Yes. The feed lists 2 Saturday-morning parkruns in Hermanus:

- **Benguela Cove Parkrun**: every Saturday at 8:00am. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
- **Hermanus Park Run**: every Saturday at 08:00. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)

The feed marks both as routine local life, but they could still suit a guest who runs. Neither has a stated price.

The feed doesn't cover Quicket or Webtickets.

I can show you the proof for either one.
<!-- end -->

## named_kalfiefees_2027

### Turn 1

> Is Kalfiefees on in August 2027?

Tools called: `find({"place": "Hermanus", "text": "Kalfiefees"})`
Cost: 0.0250

<!-- answer -->
**Kalfiefees doesn't have dates for August 2027 yet.** No page in the feed gives 2027 dates. It was last held Wed 5 to Mon 10 August 2026 in Hermanus, so an August 2027 edition is likely, but check with the organiser before you plan around it.

- Kalfiefees Hermanus Kunstefees: August 2027, Hermanus. Not confirmed, no dates yet. [kalfiefees-hermanus.co.za](https://kalfiefees-hermanus.co.za/)

The feed doesn't cover Quicket or Webtickets.

Would you like the proof for the 2026 dates?
<!-- end -->

## subject_none

### Turn 1

> Is there a jazz festival in Hermanus?

Tools called: `find({"place": "Hermanus", "text": "jazz"})`, `find({"place": "Hermanus", "text": "music"})`
Cost: 0.0396

<!-- answer -->
I couldn't find a jazz festival in Hermanus. The feed has nothing with "jazz" in its title, category, venue or town, either coming up or in the past.

The feed doesn't cover Quicket or Webtickets, so a jazz event sold only there wouldn't show up.

The closest I can offer is the music events still to come: 8 in the feed, through to the FynArts Old Harbour Sunset Concert on 6 March 2027. Would you like that list?
<!-- end -->

## town_no_dates

### Turn 1

> What is there to do in Stanford?

Tools called: `find({"place": "Hermanus", "text": "Stanford"})`
Cost: 0.0461

<!-- answer -->
The feed has 11 upcoming things to do in Stanford. Here are 6 of them:

- Think & Drink · Thu 26 Nov 2026 · Confirmed · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- The Sunset Market · Fri 27 Nov 2026 · Confirmed · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- Open Air Cinema: Raiders of the Lost Ark · Sat 28 Nov 2026 · Confirmed · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- Oysters & Bubbles · Sun 29 Nov 2026 · Confirmed · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- Stanford 100 Miler · Sat 5 Dec 2026 · Confirmed · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf)
- Sunset Sessions · December 2026 · Confirmed, programme not stated · [whalecoast.info](https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf)

I left out a drag show, a walking event, a community toy run, Christmas lights, cricket and past events.

The feed does not cover Quicket or Webtickets.

Would you like the proof for any of these?
<!-- end -->

