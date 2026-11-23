# T1 - Event census, Hermanus and near Overstrand

Read on 2026-11-22. Window: 2026-11-22 to 2028-05-31. Scope: Hermanus (with Onrus, Sandbaai, Vermont, Hawston, Fisherhaven/Benguela Cove), Hemel-en-Aarde, Stanford, Gansbaai, Kleinmond.

## 1. Result

1. **112 distinct events** counted (108 if the 4 "possible duplicate" rows are duplicates). This is a lower limit. It is not 20 to 30.
2. Time types: `day` 55, `run` 11, `recurring` 14, `season` 4, `annual_no_date` 28. (55+11+14+4+28 = 112.)
3. Sources: 11 gave events (3 tourism, 3 venue/festival, 2 ticketing, 2 aggregators, 1 provincial agency). 9 more pages or sites failed or were empty.
4. Chapman: Overstrand Tourism against AllEvents, all rows: n1=75, n2=28, m=5, **N = 366** (unreliable, see section 4). Same pair, limited to 22-29 Nov 2026 where the two have equal detail: n1=32, n2=5, m=4, **N = 39 events in one 8-day week**. AllEvents against Quicket: N = 34 (too low, AllEvents copies ticketing sites).
5. Confidence: high that the total is more than 100 and that ordering/ranking is necessary. Low for each Chapman number. Important shape: 59 of 66 dated events are in the next 6 weeks; only 7 dated events are after 2026-12-31; none is dated in 2028. Sources publish small events 1 to 5 weeks ahead.

```
Dated events per period (66 rows)
22-30 Nov 2026  | ################################## 34
Dec 2026        | ######################### 25
Jan-Jun 2027    | ####### 7   (KliK?, 2 screenings... see E60-E66)
Jul 2027-May 28 | 0
```

## 2. Sources

| Code | Source | URL read | Type | Loaded | Dates as text | Events in window |
|---|---|---|---|---|---|---|
| OT | Overstrand Tourism / Cape Whale Coast (municipal) | U1 `https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf` (annual 2026); U2 `https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-111126.pdf`; U3 `https://www.overstrand.gov.za/top-things-to-do-this-weekend/` | tourism | yes | PDF text (U1, U2), HTML text (U3) | 75 |
| HT | Hermanus Tourism | U4 `https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/`; U5 `https://hermanus-tourism.co.za/whale-watching/` | tourism | yes | yes, partly stale | 15 |
| FA | Hermanus FynArts | U6 `https://www.hermanusfynarts.co.za/`; U7 `https://www.hermanusfynarts.co.za/event-list`; U8 `https://www.hermanusfynarts.co.za/event-details-1/2027-hermanus-fynarts-festival-2027-06-24-09-00` | festival | yes | yes (list page has no year) | 3 |
| WF | Hermanus Whale Festival | U9 `https://hermanuswhalefestival.co.za/` | festival | yes | yes, 2026 edition only | 1 |
| KF | Kalfiefees | U10 `https://kalfiefees-hermanus.co.za/` | festival | yes | yes, 2026 edition only | 1 |
| XP | Xplorio Hermanus | U11 `https://xplorio.com/hermanus/en/things-to-do/events` | tourism / directory | yes | yes (dd/mm/yyyy) for 3 items; prose without dates for the others | 11 |
| AE | AllEvents.in Hermanus | U12 `https://allevents.in/hermanus/all`; U13 `https://allevents.in/hermanus/all?page=2` | aggregator | yes, truncated ("more events omitted") | yes | 28 |
| QK | Quicket | U14 `https://www.quicket.co.za/events/395886-rosoberry-harvest-fest-2026/`; U15 `https://www.quicket.co.za/organisers/91267-creedence-a-clearwater-revival`; U16 `https://www.quicket.co.za/organisers/97628-camphill-farm-community-hermanus`; U17 `https://www.quicket.co.za/organisers/23532-secret-sunrise-cape-town` | ticketing | event and organiser pages yes; search no | yes | 5 (partial) |
| WT | Webtickets | U18 `https://webtickets.co.za/Hermanusrotary` | ticketing | one event page yes; search no | yes | 1 (partial) |
| WG | Wesgro (provincial tourism agency) | U19 `https://www.wesgro.co.za/travel/events?q=hermanus` | tourism | page 1 of 4 only | yes | 6 |
| BC | Benguela Cove wine estate | U20 `https://benguelacove.co.za/events/` | venue | list yes; detail page HTTP 429 | no dates on the list | 2 counted, 11 leads without date |

Failed, empty or zero:

| Source | URL | Result |
|---|---|---|
| Whale Coast events page | `https://www.whalecoast.info/events/` and `https://whalecoast.info/events-calendar/` | Loaded. Calendar empty: "No posts were found." Only links to PDFs and one PNG diary. |
| Hermanus Tourism events | `https://hermanus-tourism.co.za/events/` | Loaded. No event entries, only menus. |
| Quicket search | `https://www.quicket.co.za/events/?q=hermanus` | Loaded, empty (title only). Needs JavaScript. |
| Quicket location page | `https://www.quicket.co.za/explore/south-africa/western-cape/hermanus/` | HTTP 404 (URL was my guess). |
| Webtickets search | `https://www.webtickets.co.za/v2/search.aspx?searchterm=hermanus` | Loaded, empty. Needs JavaScript. |
| Computicket | `https://computicket.com/search?q=hermanus` | HTTP 404 (URL was my guess). Computicket is not checked. |
| SA-Venues Hermanus | `https://www.sa-venues.com/events/westerncape/suburb/hermanus/` | Loaded. 5 events, 0 in scope (Franschhoek, Cape Town, Kenilworth, Durbanville). |
| Bandsintown | `https://www.bandsintown.com/c/hermanus-south-africa` | HTTP 403. |
| GoTrail / running.life | `https://gotrail.run/trail-running-calendar/south-africa/western-cape/hermanus`, `https://running.life/en/event/hermanus-trail-run` | HTTP 403 for both. |
| Stanford Tourism | `https://stanfordinfo.co.za/events/` | Loaded. Events are 4 images (uploaded Nov 2025) and a Mailchimp archive link. No text. |
| Benguela Cove detail | `https://benguelacove.co.za/products/dancing-queen-ultimate-abba-experience` | HTTP 429. |

## 3. Distinct events

Columns B / P / A: bookable (y / n / ?), price shown (y / n), age limit shown (y / n). No page showed an age limit, so A is "n" in each row. "pd" = possible duplicate. "loc?" = the town is not confirmed on the page that I read.

### 3a. Dated, `day` and `run` (66)

| ID | Event | Type | Date wording (quote) | Venue | B/P/A | Sources (URL) |
|---|---|---|---|---|---|---|
| E1 | FynArts Select Weekend: Makers & Masters | run | "20 – 22 November 2026" (FA); "20 - 22" (U2). Last day is the first day of the window | Various venues, Hermanus | y/n/n | FA U6, OT U2 U3, XP U11 |
| E2 | Annual Art Exhibition 2026 | run | "19 - 25" Nov (U2) | Enlighten Education Trust, Hermanus | ?/n/n | OT U2 U3 |
| E3 | Christmas Stalletjies | run | "18–24 Nov" (U3) | Uilenkraalsmond Resort, Gansbaai | ?/n/n | OT U3 |
| E4 | Aligned Living Women's Silent Retreat | run | "19–22 Nov" (U3) | Bodhi Khaya, Gansbaai | ?/n/n | OT U3 |
| E5 | Louna Stofberg Organ Recital | day | "22 11:30 - 12:30" (U2) | Dutch Reformed Church, Hermanus | ?/n/n | OT U2 U3 |
| E6 | Atnote Music Coastal Band Showcase | day | "22 15:30 - 18:30" (U2); "Sun Nov 22 2026 at 03:00 pm" (AE) | Hawston Primary School Hall | ?/n/n | OT U2 U3, AE U12 |
| E7 | Soulful Sunday ft. Mario Live | day | "Sunday 22nd November 2026" 16:00 (U3) | Mozambik, Hermanus | ?/n/n | OT U3 |
| E8 | Kalahari Christmas Carol Service | day | "Sunday 22nd November 2026" 18:00 (U3) | NG Kerk, Gansbaai | ?/n/n | OT U3 |
| E9 | Walker Bay Classic Mixed (golf) | day | "Sun Nov 22 2026 at 11:30 am" | Hermanus Golf Club | ?/n/n | AE U12 |
| E10 | Christof van der Berg: Stories & Sterre | day | "25 19:00" | NG Kerksaal, Kleinmond | ?/n/n | OT U2 |
| E11 | Think & Drink | day | "26 19:00" | In the end, 25 Church Street, Stanford | ?/n/n | OT U2 |
| E12 | Toy Run | day | "27 All Day" | Harbour on Deck, Gansbaai | ?/n/n | OT U2 |
| E13 | Sunshine Nation Modeling Show | day | "27 16:00 - 18:00" | Black Leaves Club House, Gansbaai | ?/n/n | OT U2 |
| E14 | KliK Pre-Christmas Market | run | "27 16:00 - 21:00" and "28 9:00 - 14:00" | Kleinmond Town Hall | n/n/n | OT U2 |
| E15 | Hermanus Music Society Concert | day | "27 17:45" | Sandbaai Gereformeerde Church | ?/n/n | OT U2 |
| E16 | The Sunset Market | day | "27 18:00" | The Village Green, Stanford | n/n/n | OT U2 |
| E17 | Christmas Fun Fair | day | "27 18:00 - 20:00" | Jukskei Hall, Sandbaai | ?/n/n | OT U2 |
| E18 | Traffic Light Party with DJ Milky | day | "27 19:00" | Black Leaves Club House, Gansbaai | ?/n/n | OT U2 |
| E19 | Kleinmond Inniebos Kunstefees (KliK) | run | "27 - 29" Nov (U2); "27 - 29 Nov" (U1) | Various venues, Kleinmond | ?/n/n | OT U1 U2 |
| E20 | Secret Sunrise, Season/Summer Opener | day | "Saturday 28 November 2026 07:00" (QK); "28 7:00" (U2) | Grotto Beach, Hermanus | y/n/n | OT U2, AE U12, QK U17 |
| E21 | Kintsugi Intermediate Workshop | day | "28 9:00" | Coffee at the Well, Kleinmond | ?/n/n | OT U2 |
| E22 | Rosoberry Harvest Fest 2026 | day | "Sat Nov 28, 10:00 - Sat Nov 28, 17:00" (QK); "27 - 29 Nov 2026" (WG) | Hermanus River Farm, R44, Kleinmond | y/y/n ("Adults R200 \| Kids R70") | OT U2, AE U12, QK U14, WG U19 |
| E23 | Mosaic Workshop | day | "28 12:00 - 16:00" | Stonehouse Cheese Bar, Hermanus | ?/n/n | OT U2 |
| E24 | Stanford Stumble | day | "28 12:00 - 19:00" (U2); "28 Nov 2026" (WG) | Stanford Hills Estate | ?/n/n | OT U2, WG U19 |
| E25 | Tekkies & Bowties Sunset Soiree | day | "28 18:00" | High Season Farm, Hermanus | ?/n/n | OT U2 |
| E26 | Secret Sunrise (evening row) - pd of E20 | day | "28 19:00" | Grotto Beach, Hermanus | ?/n/n | OT U2 |
| E27 | Alan Committie Live (AV-A-LAUGH-TA) | day | "28 19:30" (U2); "Sat Nov 28 2026 at 07:30 pm" (AE) | Road House Cinema (U2) / "Shop G57, Whale Coast Mall" (AE) | ?/n/n | OT U2, AE U12 |
| E28 | The King of Pop Experience | day | "28 20:00" | Sandbaai Saal | ?/n/n | OT U2 |
| E29 | Grip Gymnastics & Dance Concert | run | "28 & 29 10:00" | Road House Cinema, Hermanus | ?/n/n | OT U2 |
| E30 | Overberg Toy Run | day | "29 09:00 - 14:00" (U2); "29 Nov" (U1) | Birkenhead Brewery, Stanford | ?/n/n | OT U1 U2 |
| E31 | The Blending Table: Create your own wine | day | "29 11:00 - 13:30" (U2). BC list has no date, price "R 895.00" | Benguela Cove | y/y/n | OT U2, BC U20 |
| E32 | Singles' Night | day | "29 17:00" | Ficks, Hermanus | ?/n/n | OT U2 |
| E33 | Oysters & Bubbles | day | "29" (no time) | The Parlour, Landskein Wines, Stanford | ?/n/n | OT U2 |
| E34 | Toy Run Overberg - pd of E12 or E30 | day | "28 Nov 2026" | Gansbaai | ?/n/n | WG U19 |
| E35 | Art exhibition | day | "Tue Dec 01 2026 at 12:00 am" | "Protea, Western Cape" loc? | ?/n/n | AE U12 |
| E36 | Jingle Bell Rock with The Family Band | day | "Thu Dec 03 2026 at 06:00 pm" | Hermanus Golf Club | ?/n/n | AE U12 |
| E37 | Creedence - A Clearwater Revival | day | "Friday 4 December 2026 18:00" (QK) | Hermanus Golf Club | y/n/n | AE U12, QK U15 |
| E38 | 4th Annual Most Influential Icons Gala Dinner | day | "Fri Dec 04 2026 at 05:00 pm" | Hermanus Auditorium | ?/n/n | AE U12 |
| E39 | Stanford 100 Miler | day | "5 Dec" | Stanford | ?/n/n | OT U1 |
| E40 | Hawston Sea Festival | day | "5 Dec" (U1); XP has no date, "beginning of December" (paraphrase) | Hawston Campsite | ?/n/n | OT U1, XP U11 |
| E41 | Ubumnandi Summer Picnic | day | "5 Dec" (U1); "Sat Dec 05 2026 at 12:00 pm – Sun Dec 06 2026 at 01:00 am" (AE) | Mount Pleasant Sport Field, Hermanus | ?/n/n | OT U1, AE U12 |
| E42 | Hermanus Pride Party | day | "Sat Dec 05 2026" | Ficks | ?/n/n | AE U12 |
| E43 | Nádine live in Hermanus | day | "Saturday 5 December 2026 19:00" | Curro Hermanus | y/n/n | QK U16 |
| E44 | TITAN Trail Run, Benguela Cove | day | "6 Dec 2026" | Benguela Cove Lagoon Wine Estate, Fisherhaven | ?/n/n | WG U19 |
| E45 | Hermanus Christmas Market | run | "Thu Dec 10 2026 at 10:00 am – Fri Dec 11 2026 at 05:00 pm" | The Overstrand Learning Hub | ?/n/n | AE U12 |
| E46 | Whale Coast Mall: Final 2026 Ladies Night | day | "Thu Dec 10 2026 at 07:45 pm" | Shop G57, Whale Coast Mall | ?/n/n | AE U12 |
| E47 | Rumours of Fleetwood Mac Tribute | day | "Fri Dec 11 2026 at 06:00 pm" | Hermanus Golf Club | ?/n/n | AE U12 |
| E48 | The Gift Market | day | "Fri Dec 11 2026 at 10:00 am" | 1 Curro Road, Sandbaai | ?/n/n | AE U12 |
| E49 | Paddakoor Akademie Christmas Carnival | day | "Sat Dec 12 2026 at 12:00 pm" | Groenberg Jukskei Klub loc? | ?/n/n | AE U12 |
| E50 | Christmas Market | day | "Sun Dec 13 2026 at 09:00 am" | Rivergate Guest Farm loc? | ?/n/n | AE U12 |
| E51 | The Stanford 100 Miler - pd of E39 | day | "14 Dec 2026" | Stanford | ?/n/n | WG U19 |
| E52 | Hermanus Carols 2026 (Rotary) | day | "15 Dec 2026 18:30" (WT); "Tue Dec 15 2026 at 06:00 pm" (AE); "the last Friday before Christmas" (HT) | Attie Bishop Field, opposite Hermanus High School (WT); "Old Harbour arena" (HT) | y/y/n ("R70 - R350") | AE U12, WT U18, HT U4 |
| E53 | Two Cookies - Make one. Give one. | day | "Wed Dec 16 2026 at 09:00 am" | Wonderland Lifestyle Nursery loc? | ?/n/n | AE U12 |
| E54 | sisters. SHOP-UP | run | "Fri Dec 18 2026 at 11:00 am – Sat Dec 19 2026 at 04:00 pm" | Wildekrans Wine Estate loc? | ?/n/n | AE U12 |
| E55 | Onrus Open | day | "Sat Dec 19 2026 at 08:30 am" | Onrus beach | n/y/n (free entry) | AE U12 |
| E56 | Secret Sunrise/Sunset, Solstice | day | "Monday 21 December 2026 18:30" (QK) | Grotto Beach, Hermanus | y/n/n | AE U12, QK U17 |
| E57 | Jeremy Loops in Stanford | day | "Wed Dec 23 2026 at 03:00 pm" | Stanford Hills Estate | ?/n/n | AE U12 |
| E58 | Sixth Cricket | day | "26 Dec" | Stanford | ?/n/n | OT U1 |
| E59 | Trans Agulhas Boat Race | day | "31 Dec" | Gansbaai | ?/n/n | OT U1 |
| E60 | KliK (Wesgro date) - pd of E19 | day | "6 Feb 2027" | Kleinmond | ?/n/n | WG U19 |
| E61 | Great Art On Screen: The Last Supper | day | "Mon Feb 08 2027" | Shop G57, Whale Coast Mall | ?/n/n | AE U13 |
| E62 | Retreat Yourself 2027 | run | "Thu Feb 25 2027 at 02:00 pm – Sun Feb 28 2027 at 02:00 pm" | Elandskloof Farm Cottages loc? | ?/n/n | AE U12 |
| E63 | FynArts Old Harbour Sunset Concert | day | "6 March 2027" (U6); "Sat, 06 Mar" (U7) | Old Harbour, Hermanus | ?/n/n | FA U6 U7 |
| E64 | The Met Opera: Manon (screening) | day | "Mon Apr 12 2027" | Shop G57, Whale Coast Mall | ?/n/n | AE U13 |
| E65 | The Met Opera: Otello (screening) | day | "Mon May 03 2027" | Shop G57, Whale Coast Mall | ?/n/n | AE U13 |
| E66 | Hermanus FynArts Festival 2027 | run | "24 June 2027 – 4 July 2027" (FA). OT and HT show the 2026 dates: "6 - 14 June" | "Location is TBD" | ? (RSVP only)/n/n | FA U6 U7 U8, OT U1, HT U4 |

### 3b. `season` (4)

| ID | Event | Date wording (quote) | Venue | B/P/A | Sources |
|---|---|---|---|---|---|
| E67 | Christmas Lights Festival | "Dec" | Gansbaai | n/n/n | OT U1 |
| E68 | Christmas Lights Campaign | "Dec" | Stanford | n/n/n | OT U1 |
| E69 | Sunset Sessions | "Dec" | Stanford Hills Estate | ?/n/n | OT U1 |
| E70 | Southern right whale season | "The best time for whale watching in Hermanus South Africa is from June to December" | Walker Bay | n/n/n | HT U5 |

### 3c. `recurring` (14)

| ID | Event | Date wording (quote) | Venue | B/P/A | Sources |
|---|---|---|---|---|---|
| E71 | Hermanus parkrun | "every Saturday at 08:00" | Camphill Rd, Hemel-en-Aarde | n/y (free)/n | HT U4, OT U1 |
| E72 | Benguela Cove parkrun | "every Saturday morning at 8:00am"; XP "28/11/2026, 08H00 - 10H00" | Benguela Cove | n/y (free)/n | HT U4, OT U1, XP U11, BC U20 |
| E73 | Groeneweide parkrun | "ParkRun every Saturday at 8:00 at Groeneweide Gansbaai" | Groeneweide, Gansbaai | n/n/n | OT U1 |
| E74 | Hermanus First Friday Artwalk | "On the First Friday of every month" | Old Town galleries | n/n/n | HT U4, OT U1 |
| E75 | Hermanus Art in the Park | "1st Sunday of the month" | Hermanus Country Market venue | n/n/n | OT U1 |
| E76 | Lemm's Corner market | "Every weekend, weather permitting" "8h30 to15h00" | Cnr Main & Harbour Road | n/n/n | HT U4, OT U2 (listed for 15 Nov) |
| E77 | Thursday Morning Market, Stanford | Listed "Thursday 19th November 2026" 9:00–13:00; weekly is inferred from the name | 14 Queen Victoria Street, Stanford | n/n/n | OT U3 |
| E78 | Friday Morning Market, Gansbaai | Listed "Friday 20th November 2026" 9:00–11:30; weekly is inferred from the name | Pretorius Hall, Gansbaai | n/n/n | OT U3 |
| E79 | Onrus Market | "first Saturday of every month" "9h00-12h00" | De Wet Hall, Onrus | n/n/n | HT U4 |
| E80 | Hermanuspietersfontein Food and Wine Market | "Saturdays" "9h00- 13h00" | Hemel-en-Aarde Village | n/n/n | HT U4, XP U11 |
| E81 | Hermanus Country Market | "throughout the year" "9h00 to 14h00" (no day given on HT) | Hermanus Cricket Club | n/n/n | HT U4, XP U11 |
| E82 | Akwaaba Market | "Every Saturday from 09:00 – 14:00" | Next to Windsor Hotel | n/n/n | HT U4 |
| E83 | Sandbaai Market | "Sat Jan 02 2027 – Sat Dec 04 2027" (interval not shown; monthly is my inference) | Sandbaai Hall | n/y (free)/n | AE U12 |
| E84 | Deli Dining at Dal-Italia | "27/11/2026, 18H00 - 21H00" plus 04/12, 11/12, 18/12, 25/12 | Dal-Italia (restaurant; borderline event) | ?/n/n | XP U11 |

### 3d. `annual_no_date` (28). Last held dates, all 2026. No source showed a 2027 date.

"Annual" comes from the menu label "Annual events" on the PDF U1 (title "Events 2026"). It is not proved for each row.

| ID | Event | Last held (quote) | Venue | Sources |
|---|---|---|---|---|
| E85 | Hermanus Whale Festival | "2–4 October 2026" (WF); "02-04 October 2026" (HT) | Hermanus | WF U9, HT U4, OT U1, XP U11 |
| E86 | Kalfiefees | "5-10 AUGUSTUS 2026" (KF); "05-10 August 2026" (HT) | Onrus & Hermanus | KF U10, HT U4, OT U1, XP U11 |
| E87 | Fernkloof Flower Show (HT: "Celebration of Fynbos"; XP: "Flower and Eco Fair") - merged on venue and month, names differ | "25 - 27 Sept" (U1) | Fernkloof Nature Reserve | OT U1, HT U4, XP U11 |
| E88 | Hermanus Wine & Food Festival / Fair - merged, names differ | no date on either page | Hemel-en-Aarde Village (XP) | HT U4, XP U11 |
| E89 | Hermanus Adventure Week | no date; September (paraphrase) | not stated | XP U11 |
| E90 | Stiek Yt Motorbike Rally | "6 - 8 Feb" | Palmiet Caravan Park, Kleinmond | OT U1 |
| E91 | Overberg BMX Club Race | "8 February" | Hermanus | OT U1 |
| E92 | Birkenhead Commemoration | "26 Feb" | Gansbaai | OT U1 |
| E93 | Lighthouse2Lighthouse Walk | "5 - 8 March" | Gansbaai | OT U1 |
| E94 | Cape 1000 Classic Cars | "18 March" | Burgundy Restaurant, Hermanus | OT U1 |
| E95 | Baardskeerdersbos Art Route | "27 - 29 March" | Gansbaai | OT U1 |
| E96 | Greenpop's Reforest Festival | "3 - 6 April" | Gansbaai | OT U1 |
| E97 | Franskraal Art Route | "4 - 6 April" | Gansbaai | OT U1 |
| E98 | False Bay 50km | "2 May" | Kleinmond - Gordon's Bay | OT U1 |
| E99 | Race2Hermanus Triathlon | "3 May" | Hermanus | OT U1 |
| E100 | Stanford River Race | "9 May" | Stanford | OT U1 |
| E101 | SA National BMX Summer Classic | "14 June" | Hermanus | OT U1 |
| E102 | Penguin Plunge | "20 June" | Stanford | OT U1 |
| E103 | Overstrand Fashion Week | "7 & 8 Aug" | The Shed, Kleinmond | OT U1 |
| E104 | Trail Series Super League | "16 Aug" | Kleinmond | OT U1 |
| E105 | Race 2 the Sea | "5 Sept" | Franschhoek to Hermanus | OT U1 |
| E106 | Stanford in Bloom | "12 - 27 Sept" | Queen Victoria Street, Stanford | OT U1 |
| E107 | Chelsea Flowers in Stanford | "12 - 27 Sept" | Queen Victoria Street, Stanford | OT U1 |
| E108 | Rewilding Greater Gansbaai Festival | "24 - 26 Sept" | Gansbaai | OT U1 |
| E109 | Wine & Cheese Festival | "3 Oct" | Walker Bay Estate, Stanford | OT U1 |
| E110 | Pam Golding Hangklip Marathon | "25 Oct" | Kleinmond | OT U1 |
| E111 | Kleinmond Ceramic Festival | "Oct" | Kleinmond | OT U1 |
| E112 | Wines2Whales | "6 Nov - 15 Nov" | Hermanus | OT U1 |

B/P/A for 3d: bookable unknown, no price, no age limit, for each row.

### 3e. Seen but not counted

- Permanent or standing items: 4 (African Market "daily", Craft Markets "daily", Sculpture on the Cliffs, Legacy Walk).
- Benguela Cove items with no date on the page that loaded: 11 leads (Dancing Queen ABBA Experience, New Years Eve 2026, That 80s Show Concert, Swallow Series Wine Tasting Lunches, Cuvée Weekends, Fire on the Lagoon Dinners, Andrew Young Live Concert, Wildlife Sculpture Exhibition, Christmas Eve Dinner 2026, Family Sharing Lunch, Christmas Lunch 2026). Prices were shown (for example "From R 450.00 to R 1,450.00"). Some of these are real dated events.
- Out of scope towns in the Overstrand lists, 22-29 Nov: 6 (Pringle Bay, Betty's Bay, Rooiels) plus the Harold Porter parkrun.
- Not an event: "Enrolment Morning - 28 November" (school, AllEvents).
- Out of area: 5 on SA-Venues, 1 on Wesgro (Caledon), 3 Secret Sunrise events in Cape Town.

## 4. Source by event, and capture-recapture

Only 23 of 112 events are in 2 or more sources. The other 89 are in one source only: OT 58, AE 20, WG 4, HT 3, XP 2, QK 1, FA 1.

Matrix for the 23 multi-source events (x = listed):

| ID | Event | OT | HT | FA | WF | KF | XP | AE | QK | WT | WG | BC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | FynArts Select | x | | x | | | x | | | | | |
| E6 | Atnote showcase | x | | | | | | x | | | | |
| E20 | Secret Sunrise opener | x | | | | | | x | x | | | |
| E22 | Rosoberry | x | | | | | | x | x | | x | |
| E24 | Stanford Stumble | x | | | | | | | | | x | |
| E27 | Alan Committie | x | | | | | | x | | | | |
| E31 | Blending Table | x | | | | | | | | | | x |
| E37 | Creedence | | | | | | | x | x | | | |
| E40 | Hawston Sea Festival | x | | | | | x | | | | | |
| E41 | Ubumnandi | x | | | | | | x | | | | |
| E52 | Hermanus Carols | | x | | | | | x | | x | | |
| E56 | Solstice | | | | | | | x | x | | | |
| E66 | FynArts Festival | x | x | x | | | | | | | | |
| E71 | Hermanus parkrun | x | x | | | | | | | | | |
| E72 | Benguela parkrun | x | x | | | | x | | | | | x |
| E74 | First Friday | x | x | | | | | | | | | |
| E76 | Lemm's Corner | x | x | | | | | | | | | |
| E80 | HPF market | | x | | | | x | | | | | |
| E81 | Country Market | | x | | | | x | | | | | |
| E85 | Whale Festival | x | x | | x | | x | | | | | |
| E86 | Kalfiefees | x | x | | | x | x | | | | | |
| E87 | Fernkloof Flower Show | x | x | | | | x | | | | | |
| E88 | Wine & Food Festival | | x | | | | x | | | | | |

Single-source events by source (the rest of the matrix, one x each):
- OT only (58): E2-E5, E7, E8, E10-E19, E21, E23, E25, E26, E28-E30, E32, E33, E39, E58, E59, E67-E69, E73, E75, E77, E78, E90-E112.
- AE only (20): E9, E35, E36, E38, E42, E45-E50, E53-E55, E57, E61, E62, E64, E65, E83.
- WG only (4): E34, E44, E51, E60. HT only (3): E70, E79, E82. XP only (2): E84, E89. QK only (1): E43. FA only (1): E63.

Column totals: OT 75, HT 15, FA 3, WF 1, KF 1, XP 11, AE 28, QK 5, WT 1, WG 6, BC 2.

### Chapman, N = (n1+1)(n2+1)/(m+1) - 1

| Pair | Scope | n1 | n2 | m (IDs) | N | Value |
|---|---|---|---|---|---|---|
| A. OT x AE | all 112 rows | 75 | 28 | 5 (E6, E20, E22, E27, E41) | 76 x 29 / 6 - 1 = **366** | Poor. The two sources cover different times: OT has detail only to 29 Nov plus one annual sheet; AE has December. Low overlap is mostly a coverage difference. |
| B. OT x AE | dated events 22-29 Nov 2026 only | 32 | 5 | 4 (E6, E20, E22, E27) | 33 x 6 / 5 - 1 = **39** | Best pair. A tourism list against an aggregator, same 8 days. Result is per week, not per 18 months. |
| C. OT x AE | December 2026 only | 8 | 18 | 1 (E41) | 9 x 19 / 2 - 1 = **85** | Weak: m = 1, and OT has no monthly December list yet. |
| D. AE x QK | all rows | 28 | 5 | 4 (E20, E22, E37, E56) | 29 x 6 / 5 - 1 = **34** | Too low. See copying below. QK sample is 4 pages, not a full search. |
| E. OT x HT | all rows | 75 | 15 | 8 (E66, E71, E72, E74, E76, E85, E86, E87) | 76 x 16 / 9 - 1 = **134** | Two tourism offices; they share the same well-known events. Too low for small events. |

Copied listings make each estimate too low, because a copied event counts as "recaptured". Signs of copying:
- AllEvents titles agree with Quicket title format word for word ("Hermanus | Season Opener | Secret Sunrise Cape Town"; "Creedence - A Clearwater Revival at Hermanus Golf Club on 4 December"). 4 of 5 Quicket events are in AllEvents. AllEvents is an aggregator of ticketing and social pages.
- The overstrand.gov.za weekend page and the whalecoast.info PDFs are the same office; I merged them into one source (OT).
- Xplorio and Hermanus Tourism describe the same old set of festivals in prose, with the same stale wording (whale festival in September).

Honest reading: no single 18-month N is valid. The sources publish small events weeks ahead, so the population seen today is one month of small events plus the annual list. If pair B (about 39 events per week in the 5-town scope) held for 79 weeks, the total is in the low thousands; this is an extrapolation, not a measurement.

## 5. Observations for a scraper

- **Main tourism data is in PDFs and a PNG, not HTML.** `whalecoast.info/events/` and `/events-calendar/` show "No posts were found." The data is in U1 and U2 (text-extractable PDFs) and a weekly PNG diary (`Overstrand-Tourism-Diary-11-15-Nov-2026.png`, image only, not read).
- PDF file names change with each issue and hold a date code (`...-111126.pdf`, `...-070826-1-1.pdf`), under an old `/2022/06/` path. The link must be found on the page each time.
- U2 rows give day-of-month only ("28"); month and year are only in the header. The 11 Nov issue starts at day 11: earlier days are removed, so it is a rolling sheet.
- U1 gives day and month without year in rows ("5 Dec"); the year is only in the title "EVENTS 2026".
- `overstrand.gov.za/top-things-to-do-this-weekend/` is HTML text with full day headings ("Sunday 22nd November 2026"); it covers 5 days.
- `hermanus-tourism.co.za/events/` has no events. Its festivals page is prose with last year's dates still shown: FynArts "6 – 14 June 2026", Kalfie Fees "05-10 August 2026", Whale Festival "02-04 October 2026".
- Festival sites show the finished 2026 edition and no 2027 date: Whale Festival ("2–4 October 2026", with a heading "TBC"), Kalfiefees ("5-10 AUGUSTUS 2026", Afrikaans, bookings through TIXSA).
- FynArts (Wix): the list page shows "Sat, 06 Mar" and "Thu, 24 Jun" with no year; the year is on the home page, in the title and in the URL slug. "Multiple Dates" label for the festival. No ticket system yet, RSVP only.
- Quicket search and Webtickets search return empty HTML (JavaScript). Quicket event pages and organiser pages are server HTML with full dates. Webtickets event page loaded, with "Loading..." in the ticket panel.
- Benguela Cove events are shop products; the list has names and prices but no dates. The detail page returned HTTP 429 on the first request after the list.
- Stanford Tourism events are images plus a Mailchimp archive.
- AllEvents truncates ("more events omitted"); `?page=2` gave 4 more. Wesgro `?page=2` returned page 1 again (1 of 4), so its pagination is not a plain query parameter.
- HTTP 403 for automated fetch: Bandsintown, gotrail.run, running.life.
- Xplorio dates are text in dd/mm/yyyy with "18H00" time format.

Contradictions between sources for the same event:

| # | Event | Source A | Source B |
|---|---|---|---|
| 1 | FynArts Festival | FA: "24 June 2027 – 4 July 2027" | HT and OT: "6 – 14 June" (2026 edition). A search snippet from winetourism.com gave "6 – 14 June 2027" as expected; I did not open that page. |
| 2 | FynArts Festival length | FA home: "Over ten inspiring days in June" | FA detail: "11 packed days"; the dates end in July |
| 3 | FynArts Select name | "Makers and Masters" | "Masters and Makers" (same page); Xplorio names it "Hermanus FynArts" |
| 4 | Whale Festival month | WF, HT, OT: 2-4 October 2026 | HT text "each September"; Xplorio late September |
| 5 | Hermanus Carols | WT: "15 Dec 2026 18:30", Attie Bishop Field (a Tuesday) | HT: "the last Friday before Christmas", Old Harbour arena. AE: 06:00 pm |
| 6 | Rosoberry | QK, AE, OT: 28 Nov | WG: "27 - 29 Nov 2026". Town: WG "Hermanus", OT "Kleinmond". QK price: "From FREE" and "Adults R200 \| Kids R70" on one page |
| 7 | Stanford 100 Miler | OT: "5 Dec" | WG: "14 Dec 2026" |
| 8 | KliK | OT: "27 - 29 Nov" | WG: "6 Feb 2027" |
| 9 | Toy Run | OT: "Toy Run" 27 Nov Gansbaai and "Overberg Toy Run" 29 Nov Stanford | WG: "Toy Run Overberg", Gansbaai, "28 Nov 2026" |
| 10 | Atnote showcase start | OT PDF: 15:30 | OT web page: 15:00; AE: 03:00 pm |
| 11 | Alan Committie venue | OT: Road House Cinema | AE: Shop G57, Whale Coast Mall (possibly the same place; not checked) |
| 12 | Secret Sunrise | AE, OT: "Season Opener"; AE: "Solstice \| Secret Sunrise" | QK: "Summer Opener"; "Solstice \| Secret Sunset". OT has one more row, "Secret Sunrise 28 19:00" |
| 13 | Kalfiefees site | HT: kalfiefees-hermanus.co.za | OT: www.kalfiefees.co.za (not opened) |
| 14 | Whale season | HT: "June to December" | The brief says June to November. Only one whale page was read. |

## 6. Checks

What I checked and how:
- 39 web calls: 4 searches and 35 page fetches. 2 PDFs were read directly as PDF text and page image (U1, U2); these two are the strongest evidence.
- Each of the 112 rows has a URL and date wording from a page fetched in this session, with these exceptions that are marked in the tables: E88 and E89 have no date on any page; E40 (XP) and E89 are paraphrases; E77 and E78 "weekly" is inferred from the name.
- Counts: 3a 66 rows (55 day + 11 run), 3b 4, 3c 14, 3d 28; total 112. Source totals in section 4 were counted from the ID lists (23 multi-source + 89 single-source = 112).
- Weekdays for 15 Dec 2026 (Tuesday) and 23 Dec 2026 (Wednesday) agree with the page wording.

What I did not check:
- All pages except the 2 PDFs came through a fetch tool that converts the page and answers with a small model. I did not see raw HTML. A "quote" can have small differences from the page. JavaScript claims ("needs JavaScript") come from empty results, not from a browser test.
- Quicket and Webtickets as full sources: search did not load. Quicket coverage is 4 pages reached from search results. Computicket and TIXSA: not checked.
- Wesgro pages 2 to 4. AllEvents beyond the 2 pages. The Overstrand PNG diary. The December monthly PDF (not published yet on 22 Nov).
- Wine estates of Hemel-en-Aarde (only Benguela Cove was opened, and it gave no dates). Theatres, galleries, Hermanus Golf Club's own site, Stanford and Gansbaai tourism event lists, churches/OAK concerts: not checked directly.
- A second whale season source. Trail races (3 sites gave 403; a search snippet named a "Hermanus Trail Run" for 26-28 Feb 2027, not confirmed, not counted).
- Location of 6 AllEvents rows marked "loc?". Price and age limit on the detail pages (only list pages were read for most rows).
- If each "annual" row of U1 does recur in 2027.
- The local `hermanus-events` plugin was not used.

Odd things:
- The official calendar pages of the two tourism offices are empty; the real data is in file links in the menu.
- Only 7 dated events after 31 Dec 2026 and none after 4 July 2027, in an 18-month window. The far part of the window is filled only by `annual_no_date` and `recurring` rows.
- 79 percent of events (89 of 112) are in one source only. More sources will add events; the count has not levelled off.
- OT lists two Secret Sunrise rows on 28 Nov (7:00 and 19:00) and two different Toy Runs (27 and 29 Nov), and Wesgro gives a third date (28 Nov).
- Wesgro dates differ from the organiser or municipal dates in 4 of its 6 rows.
- Hermanus Whale Festival home page shows a heading "TBC" beside the finished 2026 dates.
- Quicket lists Rosoberry as "From FREE" and as R200 / R70 on the same page.
