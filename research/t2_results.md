# T2 results: quote check and date check on real pages (claude-haiku-5-5)

Written by `research/t2/check.py` from the saved answers in `research/t2/out/`.

| Page | Items | Live (title and each date pass) | Fields passed | Fields failed | Dates passed | Quote match: exact / whitespace / punctuation | Date kinds |
|---|---|---|---|---|---|---|---|
| ht_festivals | 15 | 7 | 33 | 10 | 7 of 10 | 38 / 0 / 0 | months 3, range 3, weekly 4 |
| ht_whale_watching | 0 | 0 | 0 | 0 | 0 of 0 | 0 / 0 / 0 |  |
| kalfiefees | 1 | 1 | 3 | 0 | 1 of 1 | 3 / 0 / 0 | range 1 |
| ot_monthly_pdf | 79 | 77 | 312 | 2 | 82 of 82 | 306 / 8 / 0 | date 71, range 9, weekly 2 |
| ot_yearly_pdf | 41 | 38 | 127 | 3 | 39 of 39 | 127 / 0 / 0 | date 20, months 4, range 14, weekly 1 |
| overstrand_weekend | 41 | 41 | 162 | 0 | 44 of 44 | 162 / 0 / 0 | date 40, range 4 |
| southern_right_charters | 2 | 2 | 6 | 0 | 2 of 2 | 4 / 2 / 0 | months 2 |
| wesgro_events_p1 | 24 | 24 | 72 | 0 | 24 of 24 | 72 / 0 / 0 | date 19, range 5 |
| whale_festival | 1 | 1 | 3 | 0 | 1 of 1 | 3 / 0 / 0 | range 1 |
| white_shark_projects | 1 | 0 | 3 | 1 | 0 of 0 | 3 / 0 / 0 |  |
| x_african_horse_company | 3 | 0 | 5 | 3 | 0 of 0 | 5 / 0 / 0 |  |
| x_bouchard_finlayson | 0 | 0 | 0 | 0 | 0 of 0 | 0 / 0 / 0 |  |
| x_creation_wines | 4 | 0 | 5 | 4 | 0 of 0 | 5 / 0 / 0 |  |
| x_dyer_island_cruises | 2 | 2 | 5 | 0 | 2 of 2 | 5 / 0 / 0 | months 2 |
| x_grootbos | 15 | 1 | 16 | 14 | 1 of 1 | 16 / 0 / 0 | months 1 |
| x_hamilton_russell | 0 | 0 | 0 | 0 | 0 of 0 | 0 / 0 / 0 |  |
| x_heart_of_abalone | 1 | 0 | 3 | 1 | 0 of 0 | 3 / 0 / 0 |  |
| x_hermanus_whale_cruises | 4 | 0 | 5 | 4 | 0 of 0 | 5 / 0 / 0 |  |
| x_ht_southern_right_whales | 1 | 1 | 2 | 0 | 1 of 1 | 2 / 0 / 0 | months 1 |
| x_ht_whale_and_shark_viewing | 14 | 2 | 16 | 12 | 2 of 2 | 16 / 0 / 0 | months 2 |
| x_marine_dynamics | 1 | 0 | 3 | 1 | 0 of 0 | 3 / 0 / 0 |  |
| x_walker_bay_kayaking | 1 | 1 | 5 | 0 | 2 of 2 | 5 / 0 / 0 | months 2 |
| xplorio_events | 8 | 7 | 26 | 2 | 15 of 15 | 27 / 0 / 0 | date 10, months 5 |

- Items: 259. Live: 205.
- Fields passed: 812. Fields failed: 57.
- Dates passed: 223 of 226.
- Date entries where a date quote also holds the title: 132 of 226.
- Tokens: 94933 in, 102305 out. Cost: 0.060645 US dollars (measured tokens times the list price).

## Failures by cause

- no date or availability extracted: 49
- start month 1: 3
- value: 5

## Each failure, in short form

**ht_festivals: Hermanus First Friday Artwalk** (when[0]: start month 1 not in quotes; end month 12 not in quotes)

- entry: `{"kind": "months", "start": {"day": 0, "month": 1, "year": 0}, "end": {"day": 0, "month": 12, "year": 0}, "weekday": ""}`
- quote: `On the First Friday of every month`
- page: ` Out Conferences / Functions / Weddings Country/Wine Farms Art Village Art Amble Hermanus First Friday Hermanus FynArts Getting There About Hermanus Hermanus the seaside village History Southe`

**ht_festivals: Carols by Candlelight** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ht_festivals: Celebration of Fynbos** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ht_festivals: Wine & Food Festival** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ht_festivals: African Market** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ht_festivals: De Wet Hall Onrus** (when[0]: start month 1 not in quotes; end month 12 not in quotes)

- entry: `{"kind": "months", "start": {"day": 0, "month": 1, "year": 0}, "end": {"day": 0, "month": 12, "year": 0}, "weekday": ""}`
- quote: `on the first Saturday of every month`
- page: `rican traders sell their goods. De Wet Hall Onrus Meander through the Onrus Market on the first Saturday of every month at the De Wet Hall from 9h00-12h00. https://www.facebook.com/OnrusMarkie/ `

**ht_festivals: Lemm's Corner** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ht_festivals: Hermanus Country Market** (when[0]: start month 1 not in quotes; end month 12 not in quotes)

- entry: `{"kind": "months", "start": {"day": 0, "month": 1, "year": 0}, "end": {"day": 0, "month": 12, "year": 0}, "weekday": ""}`
- quote: `is open from 9h00 to 14h00 throughout the year`
- page: `ket days with the Hermanuspietersfontein Boeremark in the Hemel-en-Aarde village which is open from 9h00- 13h00 Lemm's Corner Every weekend, weather permitting, a bustling market can be found at`

**ht_festivals: Benguela Cove Parkrun** (price: value not in quote)

- entry: `{"value": "Nothing – it’s free!"}`
- quote: `Nothing – it’s free!`
- page: `ounded by breathtaking vineyards and stunning views. What does it cost to join? Nothing – it’s free! but please register before you first come along https://www.parkrun.co.za/benguelacove/ .`

**ht_festivals: Hermanus Park Run** (price: value not in quote)

- entry: `{"value": "free"}`
- quote: `Join us for a free, timed 5km run/walk`
- page: `al beauty. Please note the Park Run is weather dependant. Hermanus Park Run Join us for a free, timed 5km run/walk at 08:00 every Saturday. Find us at Forest Adventures, Camphill Rd, Hemel & `

**ot_monthly_pdf: The Stream That Divided a Town: Talk by Dr Sheraine van Wyk** (title: value not in quote)

- entry: `{"value": "The Stream That Divided a Town: Talk by Dr Sheraine van Wyk"}`
- quote: `The Stream That Divided a Town: 19 17:30 The Green House Vermont Talk by Dr Sheraine van Wyk`
- page: `17:00 Searles Eatery, Bar & Theatre Stanford The Stream That Divided a Town: 19 17:30 The Green House Vermont Talk by Dr Sheraine van Wyk Music Trivia with Allen Barnley 19 18:30 La Cantina Stanford Decis`

**ot_monthly_pdf: Aligned Living Women’s Silent Retreat with Kathleen Booyse** (title: value not in quote)

- entry: `{"value": "Aligned Living Women’s Silent Retreat with Kathleen Booyse"}`
- quote: `Aligned Living Women’s Silent Retreat 19 -22 Bodhi Khaya Gansbaai with Kathleen Booyse`
- page: ` with Jono 19 19:00 Harbour on Deck Gansbaai Aligned Living Women’s Silent Retreat 19 -22 Bodhi Khaya Gansbaai with Kathleen Booyse Annual Art Exhibition 2026 19 - 25 18:00 Enlighten Education Trust Hermanus Paint & Decor`

**ot_yearly_pdf: Hermanus First Friday Artwalk** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ot_yearly_pdf: Hermanus Art in the Park** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**ot_yearly_pdf: Farmers, Saturday and Night Markets** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**white_shark_projects: Shark Cage Diving** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_african_horse_company: Mountain** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_african_horse_company: Beach** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_african_horse_company: Multi day trails** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_creation_wines: WINE TASTING** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_creation_wines: SEASONAL PAIRING** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_creation_wines: A LA CARTE** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_creation_wines: BREAKFAST** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Botanical 4x4 Tour** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Shark Cage Diving** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Horse Riding** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Whale Watching** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Lady Stanford River Cruise** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Walks and Hikes** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Marine Safari** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Fatbike Tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Wellness Spas** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Bird Watching** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Living the Future Tour** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Southern Tip of Africa Tour** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Coastal Safari** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_grootbos: Immersive Wellbeing** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_heart_of_abalone: Heart of Abalone** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_hermanus_whale_cruises: The Boat Trip** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_hermanus_whale_cruises: Eco-Tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_hermanus_whale_cruises: Cultural Tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_hermanus_whale_cruises: Township tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Hermanus Whale Cruises** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Southern Right Charters** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Ivanhoe Sea Safaris** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Marine Dynamics Whale Tours offers Marine Big 5 Whale Watching trips** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Marine Big Five Tours with Dyer Island Cruises (Copy)** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: SharkLady Adventures** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: White Shark Projects** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: White Shark Diving Company** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Great White Shark Tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Marine Dynamics Shark Tours** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Dave de Beer** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_ht_whale_and_shark_viewing: Blade Charters** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**x_marine_dynamics: Shark cage diving adventure** (when: no date or availability extracted)

- entry: `{}`
- page: ``

**xplorio_events: Benguela Cove Parkrun** (price: value not in quote)

- entry: `{"value": "free"}`
- quote: `A free, fun, and friendly weekly 5km community event`
- page: `ec-12 10:00 Sat, Dec-19 08:00 - Sat, Dec-19 10:00 Sat, Dec-26 08:00 - Sat, Dec-26 10:00 A free, fun, and friendly weekly 5km community event. Benguela Cove Parkrun Primary: 076 322 9844 i c `

**xplorio_events: Hermanus Wine and Food Fair** (when: no date or availability extracted)

- entry: `{}`
- page: ``

