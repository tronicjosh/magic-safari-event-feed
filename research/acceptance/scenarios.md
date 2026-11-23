# Scenarios: what a designer can ask, well or badly

Written by `research/acceptance/scenarios.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has only the four tools and the server instructions of the feed.
**21 of 33 scenarios pass the checks by code.** Measured cost: 1.429700 US dollars.

| Scenario | Last question | Tools called | Words | Checks | What failed | Cost (USD) |
|---|---|---|---|---|---|---|
| dated_one_day | Is anything on in Hermanus on Saturday 5 December 2026? | what_is_on | 143 | FAIL | lacks /5 Dec/ | 0.0383 |
| dated_month | What is on in Hermanus in December 2026? | what_is_on | 166 | PASS |  | 0.0466 |
| dated_long | My clients are in Hermanus from 1 June to 31 August 2027.  | what_is_on | 131 | FAIL | lacks /\d+ of \d+/ | 0.0402 |
| dated_quiet_day | Is anything on in Hermanus on Tuesday 9 March 2027? | what_is_on | 107 | FAIL | 1 quotes of a page | 0.0296 |
| dated_past | What was on in Hermanus from 1 to 31 March 2026? | what_is_on | 138 | PASS |  | 0.0310 |
| dated_june_2028 | What is on in Hermanus from 3 to 10 June 2028? | what_is_on | 115 | PASS |  | 0.0355 |
| dated_2029 | What is on in Hermanus from 10 to 17 June 2029? | what_is_on | 90 | FAIL | lacks /too far|does not (reach|go|cover)|only (reaches|covers|goes)|horizon|as far as|beyond/ | 0.0212 |
| dated_tonight | My clients are in Hermanus now. Is anything on tonight or  | what_is_on | 141 | PASS |  | 0.0360 |
| dated_next_weekend | What is on in Hermanus next weekend? | what_is_on | 157 | FAIL | 157 words (limit 150) | 0.0562 |
| nodates_recurring | What recurring or regular events does Hermanus have? | when_to_go | 129 | PASS |  | 0.0808 |
| nodates_weekly_market | Is there a weekly market in Hermanus? | when_to_go | 97 | FAIL | 1 quotes of a page | 0.0720 |
| nodates_wine | My guests love wine. No dates yet. What does Hermanus have | when_to_go | 119 | PASS |  | 0.0691 |
| nodates_september | They are thinking of September 2027. What is on then? | what_is_on | 141 | PASS |  | 0.0424 |
| nodates_compare | Which is better for whales in Hermanus: July or October? | when_to_go | 118 | PASS |  | 0.0427 |
| named_brief_market | Is the Hermanus Country Market on on a Saturday? | when_to_go, tell_me_more | 79 | PASS |  | 0.0780 |
| named_missing | Is there a J. Cole concert in Hermanus in December 2026? | what_is_on | 92 | PASS |  | 0.0339 |
| named_experience | Can my clients do shark cage diving near Hermanus in July  | what_is_on | 102 | PASS |  | 0.0313 |
| named_kalfiefees | When is Kalfiefees? | when_to_go | 113 | FAIL | lacks /August 2026|Aug 2026/ | 0.0696 |
| named_price | How much does the FynArts Festival cost? | when_to_go | 75 | PASS |  | 0.0681 |
| bad_other_city | What is on in Cape Town from 1 to 5 January 2027? | none | 77 | PASS |  | 0.0156 |
| bad_town_inside | What is on in Stanford in the first week of December 2026? | what_is_on | 107 | PASS |  | 0.0374 |
| bad_impossible_date | What is on in Hermanus from 30 February to 2 March 2027? | none | 48 | FAIL | a date that is not in the feed: ['28 February'] | 0.0154 |
| bad_reversed | What is on in Hermanus from 27 June to 20 June 2027? | what_is_on | 144 | PASS |  | 0.0375 |
| bad_no_place | What is on from 1 to 7 December 2026? | what_is_on | 145 | PASS |  | 0.0443 |
| bad_gibberish | asdf qwer zxcv | none | 112 | FAIL | a date that is not in the feed: ['10 December', '20 December']; 112 words (limit 80); 1 quotes of a page; lacks /\?/ | 0.0156 |
| bad_weather | What is the weather like in Hermanus in June? | when_to_go | 87 | FAIL | 1 quotes of a page | 0.0287 |
| bad_booking | Book two tickets for the FynArts Festival on 25 June 2027. | what_is_on | 97 | PASS |  | 0.0258 |
| follow_rest | Show me the ones you left out. | what_is_on | 139 | PASS |  | 0.0499 |
| follow_proof | How sure is the date of the wine market? | what_is_on, tell_me_more | 124 | FAIL | lacks /rule/ | 0.0316 |
| follow_link | Send me the link for the FynArts Festival. | what_is_on | 40 | PASS |  | 0.0261 |
| changed_same_day | I last looked on 23 November 2026. What changed in Hermanu | what_changed | 131 | PASS |  | 0.1291 |
| changed_future | What changed in Hermanus since 1 January 2027? | none | 62 | FAIL | does not call what_changed; a date that is not in the feed: ['23 November'] | 0.0154 |
| afrikaans | Wat is aan in Hermanus van 20 tot 27 Junie 2027? | what_is_on | 153 | PASS |  | 0.0348 |

## dated_one_day

### Turn 1

> Is anything on in Hermanus on Saturday 5 December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-05", "to_date": "2026-12-05"})`
Cost: 0.0383

<!-- answer -->
Yes. Three events are confirmed for that Saturday, and several markets are likely. Here are 7 of the 16 items in the feed:

- Hawston Sea Festival, Hawston: Confirmed
- Ubumnandi Summer Picnic, Hermanus: Confirmed
- Stanford 100 Miler, Stanford: Confirmed
- Akwaaba Market, Hermanus, 09:00–14:00: From a weekly rule, confirm near the date
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde: From a weekly rule, confirm near the date
- Food and craft market at the Hermanus Cricket Club: From a weekly rule, confirm near the date
- De Wet Hall market, Onrus, first Saturday of every month: Season

Left out: events that run through December without set days, monthly art events on Fridays or Sundays, a market open all year and two parkruns.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, whalecoast.info, xplorio.com. I can show the proof for any item.
<!-- end -->

## dated_month

### Turn 1

> What is on in Hermanus in December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-01", "to_date": "2026-12-31"})`
Cost: 0.0466

<!-- answer -->
**9 of 19 items in the feed for December 2026:**

- Hawston Sea Festival · Sat 5 Dec · Hawston · Confirmed
- Ubumnandi Summer Picnic · Sat 5 Dec · Hermanus · Confirmed
- Stanford 100 Miler · Sat 5 Dec · Stanford · Confirmed
- Sixth Cricket · Sat 26 Dec · Stanford · Confirmed
- Trans Agulhas Boat Race · Thu 31 Dec · Gansbaai · Confirmed
- Christmas Lights Festival · December · Gansbaai · Confirmed, programme not stated
- Deli Dining at Dal-Italia · Fri 4, 11, 18, 25 Dec · Hermanus · Confirmed
- Akwaaba Market · Sat 5, 12, 19, 26 Dec · Hermanus · From a weekly rule, confirm near the date
- Hermanus First Friday Artwalk · first Friday of every month · Season

**Not shown:** other markets, the Stanford Christmas lights and music, and parkruns.

**Not covered:** the feed doesn't include Quicket or Webtickets.

**Sources:** whalecoast.info, hermanus-tourism.co.za, xplorio.com. I can show the proof for any item.
<!-- end -->

## dated_long

### Turn 1

> My clients are in Hermanus from 1 June to 31 August 2027. What is on?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-01", "to_date": "2027-08-31"})`
Cost: 0.0402

<!-- answer -->
I picked **7 of the 13** things the feed lists for Hermanus from 1 June to 31 August 2027:

- **FynArts Festival**: 24 June – 4 July 2027. Confirmed, programme not stated
- **Southern right whales**: June – November. Season
- **Whale Watching Experience**: June – November. Season
- **First Friday Artwalk**: first Friday of each month. Season
- **Hermanus Art in the Park**: first Sunday of each month. Season
- **Akwaaba Market**: Saturdays. From a weekly rule, confirm near the date
- **Hermanuspietersfontein Food and Wine Market**: Saturdays, Hemel-en-Aarde. From a weekly rule, confirm near the date

I left out the other markets and two Saturday parkruns.

The feed does not cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, hermanusfynarts.co.za, southernrightcharters.co.za, whalecoast.info. I can show you the proof for any of these.
<!-- end -->

## dated_quiet_day

### Turn 1

> Is anything on in Hermanus on Tuesday 9 March 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-03-09", "to_date": "2027-03-09"})`
Cost: 0.0296

<!-- answer -->
**No. The feed has nothing dated for Tuesday 9 March 2027.** It has 5 items that repeat all year, and most of them fall on days other than Tuesday. Showing 4 of 5:

- Hermanus First Friday Artwalk: first Friday of every month, Season
- De Wet Hall Onrus market: first Saturday of every month, Onrus, Season
- Hermanus Art in the Park: first Sunday of the month, Season
- Hermanus Country Market: "throughout the year", day not stated, Season

Left out: a second listing of the Artwalk.

The feed does not cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, whalecoast.info. I can send the proof for any item.
<!-- end -->

## dated_past

### Turn 1

> What was on in Hermanus from 1 to 31 March 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-03-01", "to_date": "2026-03-31"})`
Cost: 0.0310

<!-- answer -->
Here are **7 of 8** items listed for Hermanus in March 2026. First Friday Artwalk appears twice in the feed, so I show it once. The month is over, so this is what the feed lists now, not a record of what actually happened.

- Lighthouse2Lighthouse Walk, 5–8 March, Gansbaai: Confirmed, programme not stated
- Cape 1000 Classic Cars, 18 March, Hermanus: Confirmed
- Baardskeerdersbos Art Route, 27–29 March, Gansbaai: Confirmed, programme not stated
- First Friday Artwalk, first Friday of every month: Season
- Art in the Park, first Sunday of the month: Season
- De Wet Hall market, Onrus, first Saturday of every month: Season
- Hermanus Country Market, throughout the year: Season

Nothing was left out. The feed does not cover Quicket or Webtickets.

Sources: whalecoast.info, hermanus-tourism.co.za. I can show the proof for any item.
<!-- end -->

## dated_june_2028

### Turn 1

> What is on in Hermanus from 3 to 10 June 2028?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2028-06-03", "to_date": "2028-06-10"})`
Cost: 0.0355

<!-- answer -->
**I'm showing 5 of the 7 items on for 3–10 June 2028.** None has a set date for 2028. Whale season begins in June, and the markets happen on set days each month:

- Southern Right Whales: June to November. Season
- Hermanus Whale Watching Experience: June to November. Season
- De Wet Hall Market, Onrus: first Saturday of every month. Season
- Hermanus Art in the Park: first Sunday of the month. Season
- Hermanus Country Market: all year. Season

I left out the art walks (the First Friday Artwalk, listed twice).

The feed doesn't cover events sold on Quicket or Webtickets.

Sources: hermanus-tourism.co.za, whalecoast.info, southernrightcharters.co.za. I can show the evidence for any item.
<!-- end -->

## dated_2029

### Turn 1

> What is on in Hermanus from 10 to 17 June 2029?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2029-06-10", "to_date": "2029-06-17"})`
Cost: 0.0212

<!-- answer -->
**The feed has nothing for Hermanus from 10 to 17 June 2029 (0 items).** That date is two and a half years away, and the feed doesn't yet hold events or seasons that far ahead.

The feed doesn't cover two sources: Quicket (it lists about 136 events within 60 km) and Webtickets.

What I can do now is show what Hermanus usually has in June each year: its seasons and its yearly events. Should I pull that?

Sources: 8 sites for Hermanus were checked; none had items for those dates.
<!-- end -->

## dated_tonight

### Turn 1

> My clients are in Hermanus now. Is anything on tonight or tomorrow?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-11-23", "to_date": "2026-11-24"})`
Cost: 0.0360

<!-- answer -->
Yes, there are 3 options, though the feed doesn't give times, so I can't confirm anything specifically for tonight. The listings I found are:

- **Annual Art Exhibition**, 19–25 Nov, Hermanus: Confirmed, programme not stated
- **Christmas Stalletjies** (market), 18–24 Nov, Gansbaai: Confirmed, programme not stated
- **Whale watching** (boat trip or watching southern right whales from shore), June to end November, Hermanus: Season

The exhibition and the market are listed with a first and last day only, so check they're open on the night or day your clients want to go.

I left out the monthly markets and the art walk (not on these dates), a market with no stated days and duplicate listings.

The feed doesn't cover events on the Quicket or Webtickets ticketing sites.

Sources: overstrand.gov.za, whalecoast.info, hermanus-tourism.co.za, southernrightcharters.co.za. I can show you the proof for any item.
<!-- end -->

## dated_next_weekend

### Turn 1

> What is on in Hermanus next weekend?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-11-28", "to_date": "2026-11-29"})`
Cost: 0.0562

<!-- answer -->
**Next weekend (Sat 28 – Sun 29 November), 9 of the 34 items in the feed:**

- Alan Committie Live (stand-up comedy), Sat 28 Nov, Hermanus: Confirmed
- The King of Pop Experience, Sat 28 Nov, Hermanus: Confirmed
- Food, Fun & Family Festival, Sat 28 Nov, Hermanus: Confirmed
- Hermanuspietersfontein Food and Wine Market, Sat 28 Nov, Hemel-en-Aarde: From a weekly rule, confirm near the date
- Open Air Cinema: Raiders of the Lost Ark, Sat 28 Nov, Stanford: Confirmed
- Kleinmond Inniebos Kunstefees (KliK), 27–29 Nov, Kleinmond: Confirmed, programme not stated
- Oysters & Bubbles, Sun 29 Nov, Stanford: Confirmed
- The Blending Table: Create your own wine, Sun 29 Nov, Hermanus: Confirmed
- Southern right whales, June to November: Season

**Left out:** other markets, workshops, a retreat, small local events, monthly events and parkruns.

The feed does not cover Quicket or Webtickets.

**Sources:** whalecoast.info, hermanus-tourism.co.za, southernrightcharters.co.za. I can show the proof for any item.
<!-- end -->

## nodates_recurring

### Turn 1

> What recurring or regular events does Hermanus have?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0808

<!-- answer -->
**8 of 14 items**: these are the regular events in Hermanus.

- Hermanus First Friday Artwalk: first Friday of every month. Season
- De Wet Hall market, Onrus: first Saturday of every month. Season
- Hermanus Art in the Park: first Sunday of the month. Season
- Hermanus Country Market: throughout the year. Season
- Southern Right Whales: June to November. Season
- Hermanus Flower and Eco Fair: September. Season
- Hermanus Adventure Week: September. Season
- Whale Festival: last held 2–4 October 2026. Not confirmed, no dates yet

Left out: two events with fixed dates (FynArts Festival and Annual Art Exhibition), a whale-watching boat trip and repeated listings.

The feed does not cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, whalecoast.info, xplorio.com. I can give the proof for any item.
<!-- end -->

## nodates_weekly_market

### Turn 1

> Is there a weekly market in Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0720

<!-- answer -->
The feed doesn't list a weekly market in Hermanus. It has three markets, but none has a stated weekly day:

- **Hermanus Country Market**: held all year ("throughout the year"), no day given. Season
- **De Wet Hall market, Onrus**: first Saturday of every month. Season
- **Hermanus Art in the Park**: first Sunday of the month. Season

Hermanus Country Market is the one most likely to be weekly. The feed doesn't say, so check with the organiser.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, whalecoast.info. I can show the proof for any of these.
<!-- end -->

## nodates_wine

### Turn 1

> My guests love wine. No dates yet. What does Hermanus have for them?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0691

<!-- answer -->
**The feed has no wine events or experiences for Hermanus.** Its 14 items are art, festivals, markets and whale watching. None of the cards mention wine, and I won't add wine items from memory.

The feed does not cover two ticketing sites, Quicket and Webtickets. Wine events may be listed there.

The nearest I can give you:
- **The full list of the 14 items by month.** It includes the FynArts Festival, 24 June to 4 July 2027 (Confirmed, programme not stated), but the feed says nothing about wine there.
- **Everything that's on for set dates,** once your guests have travel dates.

Sources: hermanus-tourism.co.za, whalecoast.info, hermanusfynarts.co.za, xplorio.com, southernrightcharters.co.za, hermanuswhalefestival.co.za, overstrand.gov.za. I can show the proof for any item.
<!-- end -->

## nodates_september

### Turn 1

> They are thinking of September 2027. What is on then?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-09-01", "to_date": "2027-09-30"})`
Cost: 0.0424

<!-- answer -->
I'd pick **7 of the 14 items** the feed has for Hermanus in September 2027. September falls in whale season, and two festivals happen sometime that month.

- Southern Right Whales: June to November. Season
- Hermanus Whale Watching Experience: June to November. Season
- Hermanus Flower and Eco Fair: September. Season
- Hermanus Adventure Week: September. Season
- Hermanus First Friday Artwalk: first Friday of every month. Season
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde: Saturdays 4, 11, 18 and 25 September 2027. From a weekly rule, confirm near the date
- Akwaaba Market: Saturdays 4, 11, 18 and 25 September 2027. From a weekly rule, confirm near the date

**Left out:** other markets and the Saturday parkruns.
**Not in the feed:** Quicket and Webtickets.

**Sources:** hermanus-tourism.co.za, xplorio.com, southernrightcharters.co.za, whalecoast.info. I can get the proof for any of these items.
<!-- end -->

## nodates_compare

### Turn 1

> Which is better for whales in Hermanus: July or October?

Tools called: `when_to_go({"place": "Hermanus", "from_month": 7, "to_month": 10})`
Cost: 0.0427

<!-- answer -->
The feed can't say which month has more whales. July and October are both inside the whale season, and no source compares the months. October has one extra: the Whale Festival.

These are 3 of the 12 items the feed has for July to October:
- Southern Right Whales: June to November ("mostly"). **Season**
- Hermanus Whale Watching Experience (boat trips): June to November. **Season**
- Hermanus Whale Festival: no dates yet. It was last held 2–4 October 2026. **Not confirmed, no dates yet**

I left out the markets, art events, the FynArts Festival and the September festivals.

The feed does not cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, southernrightcharters.co.za, hermanuswhalefestival.co.za. I can show the proof for any item.
<!-- end -->

## named_brief_market

### Turn 1

> Is the Hermanus Country Market on on a Saturday?

Tools called: `when_to_go({"place": "Hermanus"})`, `tell_me_more({"ids": [7]})`
Cost: 0.0780

<!-- answer -->
I can't confirm that. The feed's source says the Hermanus Country Market runs all year at the Hermanus Cricket Club, but it doesn't say which day of the week. Please check Saturday with the market before you book.

The nearest Saturday option in the feed:
- **De Wet Hall Onrus** (market), first Saturday of every month, Onrus · Season

The Quicket and Webtickets ticket sites aren't in the feed.

Sources: hermanus-tourism.co.za. I can send the evidence for either market.
<!-- end -->

## named_missing

### Turn 1

> Is there a J. Cole concert in Hermanus in December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-01", "to_date": "2026-12-31"})`
Cost: 0.0339

<!-- answer -->
The feed lists no J. Cole concert in Hermanus in December 2026. However, it doesn't cover two ticketing sites, Quicket and Webtickets, so it can't rule a concert out. Those sites are where to check.

The nearest match is the feed's only music item for December (1 of 19):
- Sunset Sessions, December 2026, Stanford: Confirmed, programme not stated

I left out festivals, markets, food and wine, art walks, sport and community events.

Sources: whalecoast.info, hermanus-tourism.co.za, xplorio.com. I can show you the evidence for Sunset Sessions, or list the other December items.
<!-- end -->

## named_experience

### Turn 1

> Can my clients do shark cage diving near Hermanus in July 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-07-01", "to_date": "2027-07-31"})`
Cost: 0.0313

<!-- answer -->
The feed can't answer this. It has no shark cage diving item for Hermanus in July 2027, so I can't confirm the activity or its season. That doesn't mean it isn't offered. The feed just doesn't cover it.

The closest marine wildlife in the feed for July 2027 is 2 of 13 items:
- Southern Right Whales, June to November: Season
- Hermanus Whale Watching Experience (boat trips), June to November: Season

I left out markets, art events, FynArts Festival and parkruns.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanus-tourism.co.za, southernrightcharters.co.za. I can show you the proof for either whale item.
<!-- end -->

## named_kalfiefees

### Turn 1

> When is Kalfiefees?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0696

<!-- answer -->
Kalfiefees isn't in the feed, so I can't give you a date for it. I checked every month of the year for Hermanus and found no item with that name. The feed also doesn't cover Quicket or Webtickets, and those ticketing sites may list it.

The closest thing I can give you is the Hermanus festivals the feed does have:
- FynArts Festival, 24 June to 4 July 2027: Confirmed, programme not stated
- Whale Festival: Not confirmed, no dates yet (last held 2 to 4 October 2026)

If you have trip dates, I can list everything on in Hermanus for those dates.

Sources: hermanusfynarts.co.za, hermanus-tourism.co.za. I can send proof for either item.
<!-- end -->

## named_price

### Turn 1

> How much does the FynArts Festival cost?

Tools called: `when_to_go({"place": "Hermanus"})`
Cost: 0.0681

<!-- answer -->
I can't tell you what the FynArts Festival costs, because the feed doesn't have a price for it.

What the feed does have is the dates:

- **FynArts Festival**, Thu 24 June – Sun 4 July 2027, Hermanus. Confirmed, programme not stated

The feed doesn't cover Quicket or Webtickets, which are the ticket sites where prices would usually be listed.

**Source:** hermanusfynarts.co.za. I can send you the proof for the dates if you'd like it.
<!-- end -->

## bad_other_city

### Turn 1

> What is on in Cape Town from 1 to 5 January 2027?

Tools called: none
Cost: 0.0156

<!-- answer -->
I can't answer that for Cape Town. The feed covers only Hermanus, so it has no events, seasons or experiences for Cape Town.

The nearest thing I can do is list what's on in Hermanus from 1 to 5 January 2027, with a confirmation tag for each date. Hermanus is a coastal town about 1.5 hours' drive from Cape Town, so it could work as a day trip or an overnight stop. Do you want that list?
<!-- end -->

## bad_town_inside

### Turn 1

> What is on in Stanford in the first week of December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-01", "to_date": "2026-12-07"})`
Cost: 0.0374

<!-- answer -->
The feed covers Stanford as part of the Hermanus area. **It lists 3 events in Stanford out of 17 for the Hermanus area** from 1 to 7 December 2026:

- **Stanford 100 Miler**: Sat 5 December 2026. Confirmed
- **Christmas Lights Campaign**: December 2026. Confirmed, programme not stated
- **Sunset Sessions**: December 2026. Confirmed, programme not stated

I left out the events in other towns nearby (Hermanus, Hawston, Gansbaai, Onrus and Hemel-en-Aarde). These are markets, a sea festival, a summer picnic, a dinner, art walks and parkruns.

The feed doesn't cover Quicket or Webtickets.

Source: whalecoast.info. I can show you the proof for any of these events.
<!-- end -->

## bad_impossible_date

### Turn 1

> What is on in Hermanus from 30 February to 2 March 2027?

Tools called: none
Cost: 0.0154

<!-- answer -->
There is no 30 February. February 2027 has 28 days, so I can't run this search as you wrote it.

Did you mean 28 February to 2 March 2027, or perhaps 1 to 2 March? Tell me the dates and I'll list what's on in Hermanus for them.
<!-- end -->

## bad_reversed

### Turn 1

> What is on in Hermanus from 27 June to 20 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0375

<!-- answer -->
I've read your dates as **20–27 June 2027**, because the end date was before the start date. Tell me if you meant something else.

**6 of 13 items:**
- FynArts Festival, 24 June – 4 July 2027: Confirmed, programme not stated
- Southern Right Whales, June – November: Season
- Hermanus Whale Watching Experience, June – November: Season
- Akwaaba Market, Sat 26 June: From a weekly rule, confirm near the date
- Hermanuspietersfontein Food and Wine Market, Sat 26 June, Hemel-en-Aarde: From a weekly rule, confirm near the date
- Food and craft market at the Hermanus Cricket Club, Sat 26 June: From a weekly rule, confirm near the date

**Left out:** monthly markets, the First Friday Artwalk, the Country Market and parkruns.

The feed doesn't cover Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za, xplorio.com. I can send the proof for any item.
<!-- end -->

## bad_no_place

### Turn 1

> What is on from 1 to 7 December 2026?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2026-12-01", "to_date": "2026-12-07"})`
Cost: 0.0443

<!-- answer -->
**Hermanus, 1–7 December 2026: 8 of 17**

- Hawston Sea Festival · Sat 5 Dec · Hawston · Confirmed
- Stanford 100 Miler · Sat 5 Dec · Stanford · Confirmed
- Ubumnandi Summer Picnic · Sat 5 Dec · Hermanus · Confirmed
- Deli Dining at Dal-Italia · Fri 4 Dec · Hermanus · Confirmed
- Christmas Lights Festival · December · Gansbaai · Confirmed, programme not stated
- Sunset Sessions · December · Stanford · Confirmed, programme not stated
- Hermanus First Friday Artwalk · first Friday of every month · Season
- Hermanuspietersfontein Food and Wine Market · Sat 5 Dec · Hemel-en-Aarde · From a weekly rule, confirm near the date

I left out other markets, a Christmas lights campaign and parkruns.

The feed doesn't cover Quicket or Webtickets.

Sources: whalecoast.info, xplorio.com, hermanus-tourism.co.za. I can show the proof for any item.
<!-- end -->

## bad_gibberish

### Turn 1

> asdf qwer zxcv

Tools called: none
Cost: 0.0156

<!-- answer -->
I couldn't find a question in "asdf qwer zxcv". It looks like a test or a typo.

Right now I can only check Hermanus. I can help in three ways:

- **Trip dates known:** I can list what's on between two dates, for example 2026-12-10 to 2026-12-20.
- **No dates yet:** I can tell you the best months to go, with the seasons and the events held each year.
- **Changes since your last look:** give me the date you last checked, and I'll list what's new or has changed since then.

Just tell me the dates or the month, plus anything about the guest's interests, and I'll pick what suits them.
<!-- end -->

## bad_weather

### Turn 1

> What is the weather like in Hermanus in June?

Tools called: `when_to_go({"place": "Hermanus", "from_month": 6, "to_month": 6})`
Cost: 0.0287

<!-- answer -->
I can't tell you about the weather. My feed only has events, seasons and experiences for Hermanus, with no weather or climate data.

Here's what it does have for June:
- **Southern Right Whales:** whale season runs June to November ("Season").
- **FynArts Festival:** 24 June to 4 July 2027 ("Confirmed, programme not stated").
- **Monthly markets and the First Friday Artwalk:** these run all year.

Do you want the full June list of 8 items, or proof for any of them?

Sources: hermanus-tourism.co.za, southernrightcharters.co.za, hermanusfynarts.co.za, whalecoast.info
<!-- end -->

## bad_booking

### Turn 1

> Book two tickets for the FynArts Festival on 25 June 2027.

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-25", "to_date": "2027-06-25"})`
Cost: 0.0258

<!-- answer -->
I can't book tickets. This feed only gives facts about events, and it has no tickets, prices or programme. What it can tell you is that 25 June 2027 falls inside the festival:

- FynArts Festival, Thu 24 June to Sun 4 July 2027, Hermanus: Confirmed, programme not stated

The feed doesn't say which shows are on 25 June, or what they cost. Please check the programme and book through the organiser. The feed doesn't cover the ticket sites Quicket and Webtickets.

Source: hermanusfynarts.co.za. I can show you the proof of the dates if you want it.
<!-- end -->

## follow_rest

### Turn 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0345

<!-- answer -->
[The first paragraph of this answer was lost by a fault of the transcript script.]

- FynArts Festival, 24 June – 4 July 2027, Hermanus: Confirmed, programme not stated
- Hermanus Whale Watching Experience, June – November: Season
- Hermanuspietersfontein Food and Wine Market, Sat 26 June 2027, Hemel-en-Aarde: From a weekly rule, confirm near the date
- Akwaaba Market, Sat 26 June 2027: From a weekly rule, confirm near the date
- Food and craft market at the Hermanus Cricket Club, Sat 26 June 2027: From a weekly rule, confirm near the date
- Hermanus Country Market, throughout the year: Season

Left out: markets and art walks held once a month, a second whale-season item, and Saturday parkruns.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanusfynarts.co.za, hermanus-tourism.co.za, southernrightcharters.co.za, xplorio.com. I can show the proof for any item.
<!-- end -->

### Turn 2

> Show me the ones you left out.

Tools called: none
Cost: 0.0154

<!-- answer -->
These are the **other 7 of the 13 items**:

- Hermanus First Friday Artwalk, first Friday of every month: Season (2 items from 2 sources)
- De Wet Hall Onrus market, first Saturday of every month, Onrus: Season
- Hermanus Art in the Park, first Sunday of every month: Season
- Southern Right Whales, June – November: Season
- Benguela Cove Parkrun, Sat 26 June 2027: From a weekly rule, confirm near the date
- Hermanus Park Run, Sat 26 June 2027: From a weekly rule, confirm near the date

The three monthly events don't happen during the stay. Their June dates would be the 4th, 5th and 6th. The feed rated the two parkruns as routine local life. The whale-season item repeats the one I already listed.

Sources: hermanus-tourism.co.za, whalecoast.info. I can show the proof for any item.
<!-- end -->

## follow_proof

### Turn 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0150

<!-- answer -->
[The first paragraph of this answer was lost by a fault of the transcript script.]

- FynArts Festival: 24 June to 4 July 2027. Confirmed, programme not stated
- Southern Right Whales: June to November. Season
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde: Sat 26 June. From a weekly rule, confirm near the date
- Akwaaba Market: Sat 26 June. From a weekly rule, confirm near the date
- Food and craft market at the Hermanus Cricket Club: Sat 26 June. From a weekly rule, confirm near the date
- Hermanus Country Market: open all year. Season

**Left out:** monthly first-Friday, first-Saturday and first-Sunday events, a duplicate whale-watching item, and parkruns.

The feed doesn't cover Quicket or Webtickets.

**Sources:** hermanusfynarts.co.za, hermanus-tourism.co.za, xplorio.com. I can send proof for any item.
<!-- end -->

### Turn 2

> How sure is the date of the wine market?

Tools called: `tell_me_more({"ids": [6]})`
Cost: 0.0166

<!-- answer -->
**I'm only moderately sure. No page gives 26 June 2027 as a date. I worked it out from a weekly pattern on one page, so please confirm it closer to the time.**

- **What the page says:** hermanus-tourism.co.za says "Saturdays are busy market days" for the Hermanuspietersfontein Boeremark in Hemel-en-Aarde village.
- **What the page doesn't say:** opening hours, venue or price. It also doesn't say whether the market runs every Saturday of the year.
- **How current it is:** this is the only source. It was last checked on 23 November 2026, with no changes recorded.

Before booking, check with the Hermanuspietersfontein estate that the market is on that Saturday, and ask for the hours.

**Source:** hermanus-tourism.co.za. I can send the full link.
<!-- end -->

## follow_link

### Turn 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0191

<!-- answer -->
[The first paragraph of this answer was lost by a fault of the transcript script.]

- FynArts Festival, 24 June – 4 July 2027, Hermanus: Confirmed, programme not stated
- Hermanus Whale Watching Experience, June – November: Season
- Hermanuspietersfontein Food and Wine Market, Sat 26 June, Hemel-en-Aarde: From a weekly rule, confirm near the date
- Akwaaba Market, Sat 26 June: From a weekly rule, confirm near the date
- Food and craft market at the Hermanus Cricket Club, Sat 26 June: From a weekly rule, confirm near the date
- Hermanus Country Market, all year: Season

Left out: monthly art walks and markets, a second whale season item and parkruns.

The feed doesn't cover Quicket or Webtickets.

Sources: hermanusfynarts.co.za, southernrightcharters.co.za, hermanus-tourism.co.za, xplorio.com. I can send proof for any item.
<!-- end -->

### Turn 2

> Send me the link for the FynArts Festival.

Tools called: none
Cost: 0.0070

<!-- answer -->
The link for the FynArts Festival is https://www.hermanusfynarts.co.za/

That page gives the dates as 24 June – 4 July 2027. It doesn't give the programme for each day. I can send the proof for the dates if you'd like it.
<!-- end -->

## changed_same_day

### Turn 1

> I last looked on 23 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-23"})`
Cost: 0.1291

<!-- answer -->
I can't tell what's new since your last look. All 151 items were first seen today (23 November), the same day you looked, and none have changed.

Here are 5 of the 151 that are still to come:

- KliK arts festival, 27–29 Nov 2026, Kleinmond: Confirmed, programme not stated
- Alan Committie Live (stand-up comedy), 28 Nov 2026, Hermanus: Confirmed
- Oysters & Bubbles, 29 Nov 2026, Stanford: Confirmed
- Hawston Sea Festival, 5 Dec 2026: Confirmed
- FynArts Festival, 24 Jun–4 Jul 2027, Hermanus: Confirmed, programme not stated

**Left out:** past events, duplicates, weekly markets and parkruns, items the feed marks as routine local life, workshops, and seasons.

**Not covered:** the feed doesn't include Quicket or Webtickets listings.

**Sources:** whalecoast.info, hermanusfynarts.co.za. I can show the proof for any item.
<!-- end -->

## changed_future

### Turn 1

> What changed in Hermanus since 1 January 2027?

Tools called: none
Cost: 0.0154

<!-- answer -->
I can't answer that yet. 1 January 2027 is still in the future (today is 23 November 2026), so no changes can be recorded after that date.

Did you mean **1 January 2026**? If so, I can list everything in Hermanus that's new or changed since then, with each old and new value. Or give me another date when you last looked.
<!-- end -->

## afrikaans

### Turn 1

> Wat is aan in Hermanus van 20 tot 27 Junie 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`
Cost: 0.0348

<!-- answer -->
**7 van 13** items vir Hermanus, 20–27 Junie 2027:

- FynArts Festival – 24 Jun tot 4 Jul 2027 – Confirmed, programme not stated
- Southern Right Whales – Junie tot November – Season
- Hermanus Whale Watching Experience (boottoere) – Junie tot November – Season
- Akwaaba Market – Sa 26 Jun – From a weekly rule, confirm near the date
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde – Sa 26 Jun – From a weekly rule, confirm near the date
- Food and craft market by die Hermanus Cricket Club – Sa 26 Jun – From a weekly rule, confirm near the date
- Hermanus Country Market – die hele jaar – Season

Weggelaat: twee parkruns en markte en kunsstap op die eerste Vrydag, Saterdag of Sondag van die maand.

Hierdie feed dek nie Quicket of Webtickets nie.

Bronne: hermanusfynarts.co.za, hermanus-tourism.co.za, xplorio.com, southernrightcharters.co.za. Ek kan die bewys vir enige item gee.
<!-- end -->

