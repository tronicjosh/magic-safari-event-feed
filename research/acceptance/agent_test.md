# Agent test: a new Claude with only the four tools of the feed

Written by `research/acceptance/agent_test.py` on 2026-11-23. Model: `claude-opus-5-5`.
The agent has the tools, the tool descriptions and the server instructions of `feed/mcp_server.py`, and no other prompt.
Questions 1 to 3 are one conversation. Each other question is a new conversation.
Code made the checks below against the text that the tools returned. Joshua's judgment is the last check.

| # | Question | Tools called | Checks by code | What failed | Cost (USD) |
|---|---|---|---|---|---|
| 1 | What is on in Hermanus for my clients from 20 to 27 June 2027? | what_is_on, tell_me_more | PASS |  | 0.0674 |
| 2 | The same dates, a second guest: a couple in their 60s who love wine an | none | FAIL | each date is from the feed or the question; dates not in the feed: ['2 July', '4 June'] | 0.0301 |
| 3 | The same dates, a third guest: a family with two children of 8 and 11. | tell_me_more | PASS |  | 0.0467 |
| 4 | My clients have no dates yet. When is the best time to go to Hermanus? | when_to_go, tell_me_more | PASS |  | 0.1136 |
| 5 | Tell me more about the FynArts Festival in June 2027. How sure is the  | what_is_on, tell_me_more | PASS |  | 0.0434 |
| 6 | I last looked on 1 November 2026. What changed in Hermanus? | what_changed | FAIL | gives a source link; each date is from the feed or the question; dates not in the feed: ['23 November'] | 0.2384 |
| 7 | Is the Hermanus Whale Festival on in October 2027? | what_is_on, tell_me_more | FAIL | gives no day in October 2027 | 0.0535 |

- The selections for guest 2 and guest 3 differ: **yes**.
  - Guest 2 (wine and art, no crowds): Akwaaba Market, FynArts Festival, Hermanus Whale Watching Experience, Hermanuspietersfontein Food and Wine Market, Southern Right Whales
  - Guest 3 (family, children 8 and 11): Akwaaba Market, Benguela Cove Parkrun, Food and craft market at the Hermanus Cricket Club, FynArts Festival, Hermanus Park Run, Hermanus Whale Watching Experience, Hermanuspietersfontein Food and Wine Market, Southern Right Whales
- Measured cost of the 7 answers: 0.593061 US dollars.

## Review of the three flags (2026-11-23)

The first version of three checks was too coarse. I read each flagged answer against the text that the tools returned, corrected the checks in the script, and applied them to these saved answers with no new model call.

| # | Flag | What the answer says | Verdict |
|---|---|---|---|
| 2 | Dates not in the feed: 4 June, 2 July | "First Friday Artwalk: ... going by its rule (\"first Friday of every month\"), it falls on 4 June or 2 July. Both dates are outside their stay." | Not a changed fact. The agent worked the dates out from the rule that the feed quotes, and said so. The calendar agrees: the first Friday of June 2027 is 4 June, and of July is 2 July. This is the effect of open decision O2 (a rule by month is shown as "All year") |
| 6 | No source link; date 23 November | The answer gives a key of the 8 sources and tags each item with its source. "23 November 2026" is the `as of` date of the feed, which the feed gives as 2026-11-23 | A fault of the check, not of the answer: the check did not read a link with no "https://" and did not read an ISO date |
| 7 | A day in October 2027 | "The feed has 14 items for Hermanus from 1 to 31 October 2027". On the festival: "no 2027 dates have been announced yet ... please don't give the guest a date" | A fault of the check: it read the window of the query as a festival date. The answer keeps "not confirmed" |

Result with the corrected checks: 7 of 7 answers call the expected tool; 0 links and 0 stated dates that are not in the feed; 2 dates that the agent worked out from a quoted rule and marked as such.

One more finding: question 6 cost 0.2384 US dollars, because `what_changed` returned 151 items (on a first run each item is new). The cost of an agent's answer grows with the number of cards that a call returns.

## Question 1

> What is on in Hermanus for my clients from 20 to 27 June 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-20", "to_date": "2027-06-27"})`, `tell_me_more({"ids": [151, 148, 11, 10, 6, 147]})`

Checks: calls what_is_on: pass; each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: pass; says how many the feed has (13): pass; says that the list can be incomplete: pass

For 20–27 June 2027 the feed has 13 items in Hermanus. I recommend 6 of them below, and there are short notes on the other 7. The list may be incomplete because the feed doesn't collect two ticketing sources: Quicket, which lists 136 events within 60 km, and Webtickets. Check those for ticketed concerts and shows.

**Festival**
- **Hermanus FynArts Festival** runs from Thu 24 June to Sun 4 July 2027 (confirmed). Your clients overlap with its first four days, 24–27 June. The page gives only the first and last day, not what happens on each day in between. The venue and price aren't stated. It has been held every year since 2013.
  Source: https://www.hermanusfynarts.co.za/

**Nature: whale season**
- **Southern right whales** come to Walker Bay "from June till end November mostly." The page doesn't give a year, so late June is at the very start of the season.
  Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/
- **Hermanus Whale Watching Experience** with Southern Right Charters runs "June to end November." No year or price is stated.
  Source: https://www.southernrightcharters.co.za/

**Saturday markets (Sat 26 June 2027)**
The date comes from each market's weekly rule. None of the pages names this date.
- **Akwaaba Market** is held "Every Saturday from 09:00 – 14:00" at the corner of St Peters Church, next to the Windsor Hotel.
  Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- **Hermanuspietersfontein Food and Wine Market** is in Hemel-en-Aarde village. The page says "Saturdays are busy market days."
  Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- **Food and craft market at the Hermanus Cricket Club** is held "any Saturday morning."
  Source: https://xplorio.com/hermanus/en/things-to-do/events

**Items I left out**
- **Three monthly events fall outside the stay:** the First Friday Artwalk ("first Friday of every month"; the feed lists it twice, ids 1 and 140), De Wet Hall Onrus ("first Saturday of every month") and Art in the Park ("1st Sunday of the month"). Going by those rules, they land in early June or early July, not 20–27 June.
- **Hermanus Country Market:** the page says only "throughout the year," with no days, so I can't place it in the stay.
  Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- **Two parkruns, if your clients are runners:** Benguela Cove Parkrun ("every Saturday morning at 8:00am") and Hermanus Park Run ("at 08:00 every Saturday"). Going by those rules, both would be on Sat 26 June. The feed rates them "below the traveller bar," meaning it sees them as routine local life.
  Source for both: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/

None of the sources states a price.

## Question 2

> The same dates, a second guest: a couple in their 60s who love wine and art, and do not like crowds. What do you recommend?

Tools called: none

Checks: each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: FAIL; says how many the feed has (13): pass

Nothing in the feed says how crowded any of these events gets, so I can't promise a quiet experience. Here is how the same facts fit this couple. The feed still has 13 items for these dates, and I recommend 4. The list may be incomplete because Quicket (136 events within 60 km) and Webtickets aren't collected.

**Recommended**

1. **Hermanus FynArts Festival** is the main art item. It runs from Thu 24 June to Sun 4 July 2027 (confirmed), so it overlaps their stay on 24–27 June. The page gives only the first and last day, and no programme, venues or prices. The festival website should show which events are smaller.
   Source: https://www.hermanusfynarts.co.za/

2. **Hermanuspietersfontein Food and Wine Market** in Hemel-en-Aarde village is the only wine item the feed has for these dates. The date, Sat 26 June, comes from the page's weekly rule. The same rule warns about crowds: "Saturdays are busy market days." If they go, they should arrive early.
   Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/

3. **Southern right whales** come to Walker Bay "from June till end November mostly." Late June is the very start of the season, so sightings are less certain than later in the year.
   Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/

4. **Hermanus Whale Watching Experience** by Southern Right Charters runs "June to end November." The page doesn't give group size or price, so ask the operator about smaller or private trips.
   Source: https://www.southernrightcharters.co.za/

**Not recommended for this couple**
- **First Friday Artwalk:** it suits their love of art, but going by its rule ("first Friday of every month"), it falls on 4 June or 2 July. Both dates are outside their stay.
- **Akwaaba Market and the Cricket Club market:** these are general Saturday markets with nothing on wine or art.
- **Parkruns:** they aren't relevant to this couple.
- **De Wet Hall, Art in the Park and the Country Market:** going by their rules, the first two fall outside the stay. The Country Market says only "throughout the year," so it can't be placed in the stay.

The feed has no wine estates, tastings or galleries for these dates. If you want to offer those, you'll need to find them yourself, and I can't add any from memory.

## Question 3

> The same dates, a third guest: a family with two children of 8 and 11. What do you recommend?

Tools called: `tell_me_more({"ids": [8, 9]})`

Checks: each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: pass; says how many the feed has (13): pass

The feed has no facts about whether any of these items suit children, such as age limits or family programmes. My choices below are based only on what each item is. The feed still has 13 items for these dates, and I recommend 6. The list may be incomplete because Quicket (136 events within 60 km) and Webtickets aren't collected, and these may list family shows.

**Whales, the highlight for the children**
1. **Southern right whales** come to Walker Bay "from June till end November mostly." Late June is the very start of the season, so sightings aren't certain.
   Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/
2. **Hermanus Whale Watching Experience** by Southern Right Charters runs "June to end November." The page doesn't give a minimum age, trip length or price, so check these with the operator before booking for an 8-year-old.
   Source: https://www.southernrightcharters.co.za/

**Saturday 26 June, a family morning**
All dates below come from each page's weekly rule. None of the pages names this date.
3. **Hermanus Park Run** is "a free, timed 5km run/walk" held "at 08:00 every Saturday" at Forest Adventures, Camphill Rd, Hemel & Aarde Valley. It can be walked, so it may suit the children, but the page says nothing about age limits. The feed rates it "below the traveller bar" (routine local life), but I think it fits an active family.
   Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
4. **Benguela Cove Parkrun** is another option, "every Saturday morning at 8:00am." The venue isn't stated, and it's also rated below the traveller bar.
   Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
5. **Akwaaba Market** is held "Every Saturday from 09:00 – 14:00" at the corner of St Peters Church, next to the Windsor Hotel.
   Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
6. **Food and craft market at the Hermanus Cricket Club** is held "any Saturday morning."
   Source: https://xplorio.com/hermanus/en/things-to-do/events

**Possible, but check first**
- **FynArts Festival** runs from Thu 24 June to Sun 4 July 2027 (confirmed; only the first and last day are given). The feed has no programme details, so I can't say whether any events are for children. Look at the website before suggesting it.
  Source: https://www.hermanusfynarts.co.za/

**Not recommended**
- **The Hermanuspietersfontein Food and Wine Market** is aimed at adults.
- **The monthly art events** (First Friday Artwalk, De Wet Hall, Art in the Park) fall outside the stay, going by their rules.
- **The Country Market** can't be placed in the stay because the page says only "throughout the year."

None of the sources states a price, except that the Hermanus Park Run is free.

## Question 4

> My clients have no dates yet. When is the best time to go to Hermanus?

Tools called: `when_to_go({"place": "Hermanus"})`, `tell_me_more({"ids": [11, 148, 151, 146, 145, 142, 4, 1, 7]})`

Checks: calls when_to_go: pass; each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: pass; says that the list can be incomplete: pass

Based on the feed, **June to November** looks like the best time to go to Hermanus. That's when the whales are there. **September and October** are the strongest months because several festivals fall inside the whale season. **Late June to early July 2027** suits clients who care more about the arts.

**Counts:** The feed has 14 items for Hermanus across the year: 9 seasons and experiences, 3 yearly items with a date and 2 not confirmed. Some are duplicates from different sources. I show 9 below.

**The main reason to go: whale season, June to November**
- **Southern Right Whales.** The page gives no year; it says the whales are there "from June till end November mostly" and that they "visit Walker Bay annually". Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/
- **Hermanus Whale Watching Experience** (Southern Right Charters). The page gives no year; it says "June to end November". Price not stated. Source: https://www.southernrightcharters.co.za/

**Best months within the season**
- **September**
  - **Hermanus Flower and Eco Fair** at Fernkloof Nature Reserve. The page says "in September every year"; no exact dates are given. Source: https://xplorio.com/hermanus/en/things-to-do/events
  - **Hermanus Adventure Week.** The page says "it is held in September" and calls it a "new annual addition". No exact dates are given. Source: https://xplorio.com/hermanus/en/things-to-do/events
- **Early October: Hermanus Whale Festival.** This is held every year but is **not confirmed** for 2027, because no page gives next year's dates yet. It was last held from 2 to 4 October 2026. Two sources list it: https://hermanuswhalefestival.co.za/ and https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/

**For arts lovers: FynArts Festival, Thu 24 June to Sun 4 July 2027 (confirmed)**
- The page gives only the first and last day, not what happens on each day in between. It falls in the early part of the whale season. Source: https://www.hermanusfynarts.co.za/

**Any month**
- **Hermanus First Friday Artwalk.** The page says "On the First Friday of every month", through Hermanus Old Town. Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- **Hermanus Country Market** at Hermanus Cricket Club. The page says it runs "throughout the year". Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- Other monthly markets I didn't check in full: **Hermanus Art in the Park** ("1st Sunday of the month", https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf) and **De Wet Hall Onrus** ("on the first Saturday of every month", https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/).

**Notes**
- I left out the Annual Art Exhibition (19 to 25 November 2026). It ends this week, so it's too soon for a trip that has no dates yet.
- **This list may be incomplete.** The feed doesn't collect Quicket, which lists 136 events within 60 km, or Webtickets.
- The feed has no weather or price data, so I can't compare months on those.

Once your clients pick dates, I can check exactly what's on during their stay.

## Question 5

> Tell me more about the FynArts Festival in June 2027. How sure is the date?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-06-01", "to_date": "2027-06-30"})`, `tell_me_more({"ids": [151]})`

Checks: calls tell_me_more: pass; each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: pass

The FynArts Festival in Hermanus runs **Thursday 24 June to Sunday 4 July 2027**, and the date is confirmed. The festival's own website gives these exact dates: *"24 June 2027 – 4 July 2027."* The date wasn't worked out from a rule or copied from last year.

**How sure is it?**
- **Confirmed for 2027.** The festival's official page gives the dates.
- **Recently checked.** The feed first saw the page and last checked it today, 2026-11-23. Nothing has changed since then.
- **Only one source.** No second site backs the dates up. Since it's the organiser's own page, that's the best single source to have.
- **Only the start and end are known.** The page gives the first and last day, not a daily programme. Don't assume there's something on every day in between. Check the programme once it's published.
- **A small mismatch.** Elsewhere the same page says *"Over ten inspiring days in June,"* but the dates run into July and cover 11 days. This is probably loose wording. Still, check with the organiser before you book anything around the last days.

**Other facts from the page**
- Held every year: *"Since 2013, Hermanus FynArts has been celebrating"*
- Place: Hermanus. No venue is named.
- Price: not stated.

**Source:** https://www.hermanusfynarts.co.za/

**Counts:** The feed has 13 items for Hermanus in June 2027: 4 dated, 7 seasons and experiences, 0 not confirmed and 2 below the traveller bar. Since you asked about FynArts, it's the only one I'm showing. The festival also falls in the southern right whale season (*"June to end November"*), if that would suit the guest.

**The list may be incomplete:** the feed doesn't collect from two ticketing sites, Quicket and Webtickets. Quicket alone lists 136 events within 60 km. Any separately ticketed FynArts shows sold there may not appear here.

## Question 6

> I last looked on 1 November 2026. What changed in Hermanus?

Tools called: `what_changed({"place": "Hermanus", "since": "2026-11-01"})`

Checks: calls what_changed: pass; each link is from the feed: pass; gives a source link: FAIL; each date is from the feed or the question: FAIL

# Hermanus: what changed since 1 November 2026

**Nothing has changed, but there's a catch.** The feed shows **151 items as "new" and 0 as "changed."** Every one of the 151 was first seen today, 23 November 2026. That means the feed started collecting Hermanus today. It has no earlier record to compare against.

So "new" here means new to the feed, not newly announced since your last look. For example, 87 of the items already took place earlier in 2026, some as far back as February. I can't tell you which items were announced after 1 November. From now on, a later check from today's date will show real changes.

**The list can be incomplete.** The feed doesn't collect from **Quicket**, which lists 136 events within 60 km, or **Webtickets**.

**How much I show:** 64 of the 151. I left out the 87 that are already over. Many events appear twice because two sources list them. I haven't opened the full cards with their quotes yet. I can do that for anything you want to recommend.

**Source key** (each item is tagged with its source):
- **[Nov]**: whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf
- **[Year]**: whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf
- **[Ovs]**: www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content
- **[HT]**: hermanus-tourism.co.za/things-to-do/festivals-and-markets/
- **[HTW]**: hermanus-tourism.co.za/about-hermanus/southern-right-whales/
- **[Xp]**: xplorio.com/hermanus/en/things-to-do/events
- **[Fyn]**: www.hermanusfynarts.co.za/
- **[SRC]**: www.southernrightcharters.co.za/

## On now
For these, the page gives only a first and last day, so it doesn't say the event is on every day in between.
- **Annual Art Exhibition**, Hermanus: 19–25 Nov (ids 28 [Ovs], 58 [Nov])
- **Christmas Stalletjies**, Gansbaai: 18–24 Nov (ids 19 [Ovs], 50 [Nov])

## Coming up (all dates confirmed)
**Wed 25 – Thu 26 Nov**
- Christof van der Berg: Stories & Sterre, Kleinmond, 25 Nov (71) [Nov]
- Alien Hacking, Gansbaai, 26 Nov (51) [Nov]
- The Art of Edible Experience Workshop, Hermanus, 26 Nov (73) [Nov]
- Think & Drink, Stanford, 26 Nov (75) [Nov]

**Fri 27 Nov**
- Hermanus Music Society Concert, Hermanus (79) [Nov]
- The Sunset Market, Stanford (80) [Nov]
- Universals RFC presents Miss Drag, Stanford (82) [Nov]
- Sunshine Nation Modeling Show, Gansbaai (77) [Nov]
- Deli Dining at Dal-Italia, Hermanus: 27 Nov and 4, 11, 18 and 25 Dec (144) [Xp]

**Fri 27 – Sun 29 Nov**
- Kleinmond Inniebos Kunstefees (KliK): page gives first and last day only (84) [Nov]
- KliK Pre-Christmas Market, Kleinmond: 27 and 28 Nov (78) [Nov]
- Sacred Pause Women's Retreat, Gansbaai: page gives first and last day only (85) [Nov]

**Sat 28 Nov**
- Hermanus:
  - Food, Fun & Family Festival (87) [Nov]
  - Stand-up Comedy: Alan Committie Live (95) [Nov]
  - The King of Pop Experience (97) [Nov]
  - Tekkies & Bowties Sunset Soiree (94) [Nov]
  - Secret Sunrise (86) [Nov]
  - Mosaic Workshop (92) [Nov]
  - Grip Gymnastics and Dance Concert, 28 and 29 Nov (98) [Nov]
- Kleinmond:
  - Rosoberry Harvest Festival (91) [Nov]
  - Kintsugi Intermediate Workshop (88) [Nov]
  - Cookie Decorating Techniques Workshop (90) [Nov]
- Stanford:
  - Stanford Stumble (93) [Nov]
  - Open Air Cinema: Raiders of the Lost Ark (96) [Nov]

**Sun 29 Nov**
- The Blending Table: Create your own wine, Hermanus (101) [Nov]
- Oysters & Bubbles, Stanford (102) [Nov]
- Youth Christmas Carol Festival, Gansbaai (104) [Nov]

**December 2026**
- **Sat 5 Dec:**
  - Hawston Sea Festival (135) [Year]
  - Stanford 100 Miler (134) [Year]
  - Ubumnandi Summer Picnic, Hermanus (136) [Year]
- **Sometime in December** (page gives the month only, not each day):
  - Christmas Lights Festival, Gansbaai (132) [Year]
  - Christmas Lights Campaign, Stanford (133) [Year]
  - Sunset Sessions, Stanford (137) [Year]
- **Sat 26 Dec:** Sixth Cricket, Stanford (138) [Year]
- **Thu 31 Dec:** Trans Agulhas Boat Race, Gansbaai (139) [Year]

**2027**
- FynArts Old Harbour Sunset Concert, Hermanus: Sat 6 Mar 2027 (150) [Fyn]
- FynArts Festival, Hermanus: 24 Jun – 4 Jul 2027, page gives first and last day only (151) [Fyn]

## Weekly
The pages state a weekly rule; the feed's code worked out the dates from it. No page states a specific date.
- Akwaaba Market, Hermanus: "Every Saturday from 09:00 – 14:00" (10) [HT]
- Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde: "Saturdays are busy market days" (6) [HT]
- Food and craft market at the Hermanus Cricket Club: "any Saturday morning" (147) [Xp]

## Monthly or all year
The pages give a rule with no year, so these are not dates.
- Hermanus First Friday Artwalk: "On the First Friday of every month" (1 [HT], 140 [Year])
- De Wet Hall, Onrus: "on the first Saturday of every month" (5) [HT]
- Hermanus Art in the Park: "1st Sunday of the month" (141) [Year]
- Hermanus Country Market: "throughout the year" (7) [HT]

## Seasons (no year stated)
- **Southern right whales:** "from June till end November mostly" (11) [HTW]. Whale Watching Experience: "June to end November" (148) [SRC]. **The season is ending now.**
- Hermanus Adventure Week: "it is held in September" (146) [Xp]
- Hermanus Flower and Eco Fair: "in September every year" (145) [Xp]

## Below the traveller bar (coming up)
The feed judges these to be routine local life. You decide whether they suit a guest. All are from [Nov] unless noted.
- **Thu 26 Nov:** Nativity Play, Hermanus (72); Business Chamber Gala Dinner, Hermanus (74)
- **Fri 27 Nov:** Christmas Fun Fair, Sandbaai (81); Toy Run, Gansbaai (76); Traffic Light Party with DJ Milky, Gansbaai (83)
- **Sat 28 Nov:** Rotsfondasie Kerk Basaar, Gansbaai (89)
- **Sun 29 Nov:** Overberg Toy Run, Stanford (100); Practice Walk, Hermanus (99); Singles' Night, Hermanus (103)
- **Every Saturday:** Benguela Cove Parkrun, "every Saturday morning at 8:00am" (8) [HT]; Hermanus Park Run, "at 08:00 every Saturday" (9) [HT]

If you tell me the guest's dates and interests, I can narrow this down and open the full cards with their quotes.

## Question 7

> Is the Hermanus Whale Festival on in October 2027?

Tools called: `what_is_on({"place": "Hermanus", "from_date": "2027-10-01", "to_date": "2027-10-31"})`, `tell_me_more({"ids": [142, 4, 11, 148]})`

Checks: each link is from the feed: pass; gives a source link: pass; each date is from the feed or the question: pass; says not confirmed: pass; gives no day in October 2027: FAIL

**It probably will be, but no 2027 dates have been announced yet.** The feed lists the Hermanus Whale Festival as "not confirmed" for October 2027. Both sources say it happens every year, but neither gives a 2027 date.

**What the sources say**
- **Hermanus Whale Festival:** The official site says the festival celebrates "the arrival of the Southern Right Whales to the shores of Hermanus each year." It was last held **2–4 October 2026** ("Taking place from 2–4 October 2026"). That page gives only the first and last day, not each day in between.
  Source: https://hermanuswhalefestival.co.za/
- **Whale Festival (Hermanus Tourism):** This page calls it "The annual Whale Festival." It gives the same dates last time: "02-04 October 2026."
  Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/

Early October 2027 is a reasonable guess, but please don't give the guest a date or book around one until the organisers announce it. Check the official site again closer to the time.

**Whale season covers all of October**
Whatever the festival dates turn out to be, the whales themselves are a safe bet. Two sources give the season, though neither names a year:
- **Southern Right Whales:** "from June till end November mostly," and they "visit Walker Bay annually."
  Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/
- **Hermanus Whale Watching Experience (Southern Right Charters):** "June to end November."
  Source: https://www.southernrightcharters.co.za/

**Counts:** The feed has 14 items for Hermanus from 1 to 31 October 2027:
- 3 with dates
- 7 seasons and experiences
- 2 not confirmed (both are this festival)
- 2 marked "below the traveller bar," meaning the feed judges them routine local life

I've shown 4 of them. The others are mostly markets, art walks and parkruns. I can go through those if they'd help.

**This list may be missing things.** The feed doesn't collect Quicket, which lists 136 events within 60 km, or Webtickets. A 2027 festival announcement or ticket sale on either site wouldn't show up here.

