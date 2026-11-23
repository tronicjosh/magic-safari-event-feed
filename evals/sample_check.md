# Sample check: 20 stored items against their pages

Made by `research/sample/make_sample.py` from `feed.db` (the real run of 2026-11-23).
For each item: open the source link, and mark each fact. A fact is **false** when the
page does not say it. Write `x` in one box of each line. The count of false facts is
acceptance line A1 (target 0).

| Result | Count |
|---|---|
| Items checked | |
| False facts | |

## 1. FynArts Festival (id 151)

Source: https://www.hermanusfynarts.co.za/

- kind `event` · category `festival` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `yes` · below the traveller bar `no`
- when: `2027-06-24` to `2027-07-04` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | FynArts Festival | ...oughout the Year Save the Dates: FynArts Select: Masters and Makers: 20 – 22 November 2026 FynArts Old Harbour Sunset Concert: 6 March 2027 **FynArts Festival:** 24 June 2027 – 4 July 2027 Since 2013, Hermanus FynArts has been celebrating the best of South African creativity in one of the country’s m... | [ ] | [ ] |
| town | Hermanus | ...l coastal settings. FynArts lives throughout the year through events, the Sculpture on the Cliffs exhibition and the Sculpture Legacy Walk. **Over ten inspiring days in June, Hermanus becomes a meeting place** for music, art, performance, literature and cuisine - bringing together celebrated artists, emerging talent and audiences who appreciate th... | [ ] | [ ] |
| yearly | yes | ...ct: Masters and Makers: 20 – 22 November 2026 FynArts Old Harbour Sunset Concert: 6 March 2027 FynArts Festival: 24 June 2027 – 4 July 2027 **Since 2013, Hermanus FynArts has been celebrating** the best of South African creativity in one of the country’s most beautiful coastal settings. FynArts lives throughout the year through eve... | [ ] | [ ] |
| when | 2027-06-24/2027-07-04 | ...ave the Dates: FynArts Select: Masters and Makers: 20 – 22 November 2026 FynArts Old Harbour Sunset Concert: 6 March 2027 FynArts Festival: **24 June 2027 – 4 July 2027** Since 2013, Hermanus FynArts has been celebrating the best of South African creativity in one of the country’s most beautiful coastal setti... | [ ] | [ ] |
| category | festival | (the model's choice from the list; no quote) | [ ] | [ ] |

## 2. Southern Right Whales (id 11)

Source: https://hermanus-tourism.co.za/about-hermanus/southern-right-whales/

- kind `season` · category `nature and wildlife` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `yes` · below the traveller bar `no`
- when: `2026-06-01` to `2028-11-30` (month; 3 rows; written by code from a season with no year)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Southern Right Whales | ...y/Wine Farms Art Village Art Amble Hermanus First Friday Hermanus FynArts Getting There About Hermanus Hermanus the seaside village History **Southern Right Whales** Whale Crier Flora and Fauna Events/Calendar Map of Hermanus Hermanus Vintage map Market Contacts Blue Flag Beaches Other Whalecoast Towns B... | [ ] | [ ] |
| town | Hermanus | ...on period of 12 months and within a year, the calf is weaned and independent. SOUTHERN RIGHT WHALES: Some facts about the whales that visit **Walker Bay** annually Why do Southern Rights calve here in Walker Bay? As is the case for the Southern Cape Coast, the Walker Bay water is warm enough t... | [ ] | [ ] |
| yearly | yes | ...estation period of 12 months and within a year, the calf is weaned and independent. SOUTHERN RIGHT WHALES: Some facts about the whales that **visit Walker Bay annually** Why do Southern Rights calve here in Walker Bay? As is the case for the Southern Cape Coast, the Walker Bay water is warm enough to sustain... | [ ] | [ ] |
| when | months 06 to 11 | ... to 5 years Growth curve for the Southern Right Whale population is set at 6,3% per year. Southern Right Whales visits the Cape South Coast **from June till end November mostly**. Question: If the migration is not complete where do the whales go? We simply don’t know! The plume of mist whales released when they breat... | [ ] | [ ] |
| category | nature and wildlife | (the model's choice from the list; no quote) | [ ] | [ ] |

## 3. Hermanus Whale Festival (id 127)

Source: https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf

- kind `event` · category `festival` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-10-02` to `2026-10-04` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Hermanus Whale Festival | ...aai Festival Gansbaai Groeneweide Farm I 082 301 9041 25 - 27 Sept Fernkloof Flower Show Fernkloof, Hermanus www.fernkloof.org.za 2 - 4 Oct **Hermanus Whale Festival** Hermanus www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 25 Oct Pam Golding Hangklip... | [ ] | [ ] |
| town | Hermanus | ...ater Gansbaai Festival Gansbaai Groeneweide Farm I 082 301 9041 25 - 27 Sept Fernkloof Flower Show Fernkloof, Hermanus www.fernkloof.org.za **2 - 4 Oct Hermanus Whale Festival Hermanus** www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 25 Oct Pam Golding Hangklip Marathon... | [ ] | [ ] |
| when | 2026-10-02/2026-10-04 | ...ater Gansbaai Festival Gansbaai Groeneweide Farm I 082 301 9041 25 - 27 Sept Fernkloof Flower Show Fernkloof, Hermanus www.fernkloof.org.za **2 - 4 Oct Hermanus Whale Festival Hermanus** www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 25 Oct Pam Golding Hangklip Marathon... | [ ] | [ ] |
| category | festival | (the model's choice from the list; no quote) | [ ] | [ ] |

## 4. Benguela Cove Parkrun (id 8)

Source: https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/

- kind `event` · category `sport to take part` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `no` · below the traveller bar `yes`
- when: `2026-11-28` to `2028-05-20` (day; 78 rows; written by code from a weekly rule)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Benguela Cove Parkrun | ...ountry Market is held at the Hermanus Cricket Club and is open from 9h00 to 14h00 throughout the year. https://hermanuscountrymarket.co.za/ **Benguela Cove Parkrun** Join us every Saturday morning at 8:00am for the Benguela Cove Park Run 5km. This is the ultimate way to start your weekend surrounded by b... | [ ] | [ ] |
| town | Hermanus | (no quote: registry default) | [ ] | [ ] |
| traveller | no | ...at the Hermanus Cricket Club and is open from 9h00 to 14h00 throughout the year. https://hermanuscountrymarket.co.za/ Benguela Cove Parkrun **Join us every Saturday morning at 8:00am** for the Benguela Cove Park Run 5km. This is the ultimate way to start your weekend surrounded by breathtaking vineyards and stunning views.... | [ ] | [ ] |
| when | weekly saturday | ...ermanus Cricket Club and is open from 9h00 to 14h00 throughout the year. https://hermanuscountrymarket.co.za/ Benguela Cove Parkrun Join us **every Saturday morning at 8:00am** for the Benguela Cove Park Run 5km. This is the ultimate way to start your weekend surrounded by breathtaking vineyards and stunning views.... | [ ] | [ ] |
| category | sport to take part | (the model's choice from the list; no quote) | [ ] | [ ] |

## 5. Kus + Kuier Mummy’s Night (id 15)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `community` · town `Kleinmond` · venue `43 Nemesia Ave, Proteadorp` · price `not stated` · held each year `no` · below the traveller bar `yes`
- when: `2026-11-18` to `2026-11-18` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Kus + Kuier Mummy’s Night | ...ttoria Stanford • Book Launch: Treasured Islands 18:00 Hermanus Library • Agteros Pop Up Heritage Table 18:30 The Station Bistro Hermanus • **Kus + Kuier Mummy’s Night** 18:30 – 21:00 43 Nemesia Ave, Proteadorp Kleinmond • Come & listen to Jacob Ka’laari & Badprop 18:30 Birkenhead Bootklub Gansbaai • Music Q... | [ ] | [ ] |
| town | Kleinmond | ... Islands 18:00 Hermanus Library • Agteros Pop Up Heritage Table 18:30 The Station Bistro Hermanus • Kus + Kuier Mummy’s Night 18:30 – 21:00 **43 Nemesia Ave, Proteadorp Kleinmond** • Come & listen to Jacob Ka’laari & Badprop 18:30 Birkenhead Bootklub Gansbaai • Music Quiz with Allen 19:00 Harbour on Deck Gansbaai • Ope... | [ ] | [ ] |
| venue | 43 Nemesia Ave, Proteadorp | ... Islands 18:00 Hermanus Library • Agteros Pop Up Heritage Table 18:30 The Station Bistro Hermanus • Kus + Kuier Mummy’s Night 18:30 – 21:00 **43 Nemesia Ave, Proteadorp Kleinmond** • Come & listen to Jacob Ka’laari & Badprop 18:30 Birkenhead Bootklub Gansbaai • Music Quiz with Allen 19:00 Harbour on Deck Gansbaai • Ope... | [ ] | [ ] |
| traveller | no | ...ttoria Stanford • Book Launch: Treasured Islands 18:00 Hermanus Library • Agteros Pop Up Heritage Table 18:30 The Station Bistro Hermanus • **Kus + Kuier Mummy’s Night 18:30 – 21:00 43 Nemesia Ave, Proteadorp Kleinmond** • Come & listen to Jacob Ka’laari & Badprop 18:30 Birkenhead Bootklub Gansbaai • Music Quiz with Allen 19:00 Harbour on Deck Gansbaai • Ope... | [ ] | [ ] |
| when | 2026-11-18 | ...o This Weekend Here is the latest Tourism Diary for the towns of Hermanus, Gansbaai, Stanford, and Kleinmond Annual Tourism Events Calendar **Wednesday 18th November 2026** • Bring & Braai 17:30 Hangklip Hotel Pringle Bay • 5-Course Dinner Fundraiser 18:00 La Trattoria Stanford • Book Launch: Treasured Islands ... | [ ] | [ ] |
| category | community | (the model's choice from the list; no quote) | [ ] | [ ] |

## 6. Thursday Community Walks (id 20)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `community` · town `Onrus` · venue `23 Molteno Str` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-19` to `2026-11-19` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Thursday Community Walks | ...Pearly Beach Hengel Klub Gansbaai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai Thursday 19th November 2026 • **Thursday Community Walks 07:30 23 Molteno Str Onrus** • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hacking 9:00 Fynbos Centre Pearly Beach • ChatGPT Mastery ... | [ ] | [ ] |
| town | Onrus | ...ai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai Thursday 19th November 2026 • Thursday Community Walks 07:30 **23 Molteno Str Onrus** • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hacking 9:00 Fynbos Centre Pearly Beach • ChatGPT Mastery ... | [ ] | [ ] |
| venue | 23 Molteno Str | ...ai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai Thursday 19th November 2026 • Thursday Community Walks 07:30 **23 Molteno Str Onrus** • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hacking 9:00 Fynbos Centre Pearly Beach • ChatGPT Mastery ... | [ ] | [ ] |
| when | 2026-11-19 | ...ingle Bay • Bingo Night 19:00 Pearly Beach Hengel Klub Gansbaai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai **Thursday 19th November 2026** • Thursday Community Walks 07:30 23 Molteno Str Onrus • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hack... | [ ] | [ ] |
| category | community | (the model's choice from the list; no quote) | [ ] | [ ] |

## 7. The Stream That Divided a Town: Talk by Dr Sheraine van Wyk (id 24)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `talks and workshops` · town `Vermont` · venue `The Green House` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-19` to `2026-11-19` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | The Stream That Divided a Town: Talk by Dr Sheraine van Wyk | ...from Earth to Art 10:00 – 16:00 Harold Porter Botanical Gardens Betty’s Bay • Members Mingle 17:00 Searles Eatery, Bar & Theatre Stanford • **The Stream That Divided a Town: Talk by Dr Sheraine van Wyk** 17:30 The Green House Vermont • Music Trivia with Allen Barnley 18:30 La Cantina Stanford • Karaoke Night with Jono 19:00 Harbour on Deck G... | [ ] | [ ] |
| town | Vermont | ...tty’s Bay • Members Mingle 17:00 Searles Eatery, Bar & Theatre Stanford • The Stream That Divided a Town: Talk by Dr Sheraine van Wyk 17:30 **The Green House Vermont** • Music Trivia with Allen Barnley 18:30 La Cantina Stanford • Karaoke Night with Jono 19:00 Harbour on Deck Gansbaai • Aligned Living Women... | [ ] | [ ] |
| venue | The Green House | ...tty’s Bay • Members Mingle 17:00 Searles Eatery, Bar & Theatre Stanford • The Stream That Divided a Town: Talk by Dr Sheraine van Wyk 17:30 **The Green House Vermont** • Music Trivia with Allen Barnley 18:30 La Cantina Stanford • Karaoke Night with Jono 19:00 Harbour on Deck Gansbaai • Aligned Living Women... | [ ] | [ ] |
| when | 2026-11-19 | ...ingle Bay • Bingo Night 19:00 Pearly Beach Hengel Klub Gansbaai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai **Thursday 19th November 2026** • Thursday Community Walks 07:30 23 Molteno Str Onrus • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hack... | [ ] | [ ] |
| category | talks and workshops | (the model's choice from the list; no quote) | [ ] | [ ] |

## 8. Aligned Living Women’s Silent Retreat with Kathleen Booyse (id 27)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `other` · town `Gansbaai` · venue `Bodhi Khaya` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-19` to `2026-11-22` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Aligned Living Women’s Silent Retreat with Kathleen Booyse | ... Green House Vermont • Music Trivia with Allen Barnley 18:30 La Cantina Stanford • Karaoke Night with Jono 19:00 Harbour on Deck Gansbaai • **Aligned Living Women’s Silent Retreat with Kathleen Booyse** 19 -22 Nov Bodhi Khaya Gansbaai • Annual Art Exhibition 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday M... | [ ] | [ ] |
| town | Gansbaai | ...a Stanford • Karaoke Night with Jono 19:00 Harbour on Deck Gansbaai • Aligned Living Women’s Silent Retreat with Kathleen Booyse 19 -22 Nov **Bodhi Khaya Gansbaai** • Annual Art Exhibition 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Preto... | [ ] | [ ] |
| venue | Bodhi Khaya | ...a Stanford • Karaoke Night with Jono 19:00 Harbour on Deck Gansbaai • Aligned Living Women’s Silent Retreat with Kathleen Booyse 19 -22 Nov **Bodhi Khaya Gansbaai** • Annual Art Exhibition 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Preto... | [ ] | [ ] |
| when | 2026-11-19/2026-11-22 | ...ingle Bay • Bingo Night 19:00 Pearly Beach Hengel Klub Gansbaai • Christmas Stalletjies 18 – 24 Nov All Day Uilenkraalsmond Resort Gansbaai **Thursday 19th November 2026** • Thursday Community Walks 07:30 23 Molteno Str Onrus • Thursday Morning Market 9:00 – 13:00 14 Queen Victoria Street Stanford • Alien Hack... | [ ] | [ ] |
| category | other | (the model's choice from the list; no quote) | [ ] | [ ] |

## 9. Bhuki Café (id 30)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `community` · town `Hermanus` · venue `Hermanus Library` · price `not stated` · held each year `no` · below the traveller bar `yes`
- when: `2026-11-20` to `2026-11-20` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Bhuki Café | ...ion 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Pretorius Hall Gansbaai • **Bhuki Café 9:00 – 12:00 Hermanus Library** • Paint & Decorate a Bird Feeder 9:00 – 12:00 Colour Box Gansbaai • Ceramic Exhibition Rooted from Earth to Art 10:00 – 16:00 Harold Porter... | [ ] | [ ] |
| town | Hermanus | ...ion 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Pretorius Hall Gansbaai • **Bhuki Café 9:00 – 12:00 Hermanus Library** • Paint & Decorate a Bird Feeder 9:00 – 12:00 Colour Box Gansbaai • Ceramic Exhibition Rooted from Earth to Art 10:00 – 16:00 Harold Porter... | [ ] | [ ] |
| venue | Hermanus Library | ...ion 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Pretorius Hall Gansbaai • **Bhuki Café 9:00 – 12:00 Hermanus Library** • Paint & Decorate a Bird Feeder 9:00 – 12:00 Colour Box Gansbaai • Ceramic Exhibition Rooted from Earth to Art 10:00 – 16:00 Harold Porter... | [ ] | [ ] |
| traveller | no | ...ion 19 – 25 Nov Enlighten Education Trust Hermanus Friday 20th November 2026 • Friday Morning Market 9:00 – 11:30 Pretorius Hall Gansbaai • **Bhuki Café 9:00 – 12:00 Hermanus Library** • Paint & Decorate a Bird Feeder 9:00 – 12:00 Colour Box Gansbaai • Ceramic Exhibition Rooted from Earth to Art 10:00 – 16:00 Harold Porter... | [ ] | [ ] |
| when | 2026-11-20 | ... Silent Retreat with Kathleen Booyse 19 -22 Nov Bodhi Khaya Gansbaai • Annual Art Exhibition 19 – 25 Nov Enlighten Education Trust Hermanus **Friday 20th November 2026** • Friday Morning Market 9:00 – 11:30 Pretorius Hall Gansbaai • Bhuki Café 9:00 – 12:00 Hermanus Library • Paint & Decorate a Bird Feeder 9:... | [ ] | [ ] |
| category | community | (the model's choice from the list; no quote) | [ ] | [ ] |

## 10. Kalahari Christmas Carol Service (id 42)

Source: https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content

- kind `event` · category `music and shows` · town `Gansbaai` · venue `NG Kerk` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-22` to `2026-11-22` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Kalahari Christmas Carol Service | ...ls • Atnote Music Coastal Band Showcase 15:00 – 18:30 Hawston Primary School Hall • Soulful Sunday ft. Mario Live 16:00 Mozambik Hermanus • **Kalahari Christmas Carol Service 18:00 NG Kerk Gansbaai**... | [ ] | [ ] |
| town | Gansbaai | ... 15:00 – 18:30 Hawston Primary School Hall • Soulful Sunday ft. Mario Live 16:00 Mozambik Hermanus • Kalahari Christmas Carol Service 18:00 **NG Kerk Gansbaai**... | [ ] | [ ] |
| venue | NG Kerk | ... 15:00 – 18:30 Hawston Primary School Hall • Soulful Sunday ft. Mario Live 16:00 Mozambik Hermanus • Kalahari Christmas Carol Service 18:00 **NG Kerk Gansbaai**... | [ ] | [ ] |
| when | 2026-11-22 | ...s Betty’s Bay • Year-end Function 18:30 Birkenhead Bootklub Gansbaai • Live Rugby: Ireland vs Springboks 18:40 Various Venues in Overstrand **Sunday 22nd November 2026** • Ceramic Exhibition Rooted from Earth to Art 10:00 – 16:00 Harold Porter Botanical Gardens Betty’s Bay • Louna Stofberg Organ Recital 11:3... | [ ] | [ ] |
| category | music and shows | (the model's choice from the list; no quote) | [ ] | [ ] |

## 11. Come & listen to Jacob Ka’laari & Badprop (id 46)

Source: https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf

- kind `event` · category `music and shows` · town `Gansbaai` · venue `Birkenhead Bootklub` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-18` to `2026-11-18` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Come & listen to Jacob Ka’laari & Badprop | ...anford Book Launch: Treasured Islands 18 18:00 Hermanus Library Hermanus Agteros Pop Up Heritage Table 18 18:30 The Station Bistro Hermanus **Come & listen to Jacob Ka’laari & Badprop** 18 18:30 Birkenhead Bootklub Gansbaai Kus + Kuier Mummy’s Night 18 18:30 - 21:00 43 Nemesia Avenue, Proteadorp Kleinmond Music Quiz with Al... | [ ] | [ ] |
| town | Gansbaai | ...anus Library Hermanus Agteros Pop Up Heritage Table 18 18:30 The Station Bistro Hermanus Come & listen to Jacob Ka’laari & Badprop 18 18:30 **Birkenhead Bootklub Gansbaai** Kus + Kuier Mummy’s Night 18 18:30 - 21:00 43 Nemesia Avenue, Proteadorp Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck Gansbaai ... | [ ] | [ ] |
| venue | Birkenhead Bootklub | ...anus Library Hermanus Agteros Pop Up Heritage Table 18 18:30 The Station Bistro Hermanus Come & listen to Jacob Ka’laari & Badprop 18 18:30 **Birkenhead Bootklub** Gansbaai Kus + Kuier Mummy’s Night 18 18:30 - 21:00 43 Nemesia Avenue, Proteadorp Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck ... | [ ] | [ ] |
| when | 2026-11-18 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| category | music and shows | (the model's choice from the list; no quote) | [ ] | [ ] |

## 12. Bingo Night (id 49)

Source: https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf

- kind `event` · category `community` · town `Gansbaai` · venue `Pearly Beach Hengel Klub` · price `not stated` · held each year `no` · below the traveller bar `yes`
- when: `2026-11-18` to `2026-11-18` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Bingo Night | ...sia Avenue, Proteadorp Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck Gansbaai Open Mic Night 18 19:00 Hangklip Hotel Pringle Bay **Bingo Night** 18 19:00 Pearly Beach Hengel Klub Gansbaai Christmas Stalletjies 18 - 24 All Day Uilenkraalsmond Resort Gansbaai Alien Hacking 19 9:00 Fynb... | [ ] | [ ] |
| town | Gansbaai | ...p Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck Gansbaai Open Mic Night 18 19:00 Hangklip Hotel Pringle Bay Bingo Night 18 19:00 **Pearly Beach Hengel Klub Gansbaai** Christmas Stalletjies 18 - 24 All Day Uilenkraalsmond Resort Gansbaai Alien Hacking 19 9:00 Fynbos Centre, Pearly Beach Gansbaai ChatGPT Ma... | [ ] | [ ] |
| venue | Pearly Beach Hengel Klub | ...p Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck Gansbaai Open Mic Night 18 19:00 Hangklip Hotel Pringle Bay Bingo Night 18 19:00 **Pearly Beach Hengel Klub** Gansbaai Christmas Stalletjies 18 - 24 All Day Uilenkraalsmond Resort Gansbaai Alien Hacking 19 9:00 Fynbos Centre, Pearly Beach Gansbaai C... | [ ] | [ ] |
| traveller | no | ...sia Avenue, Proteadorp Kleinmond Music Quiz with Allen 18 19:00 Harbour on Deck Gansbaai Open Mic Night 18 19:00 Hangklip Hotel Pringle Bay **Bingo Night** 18 19:00 Pearly Beach Hengel Klub Gansbaai Christmas Stalletjies 18 - 24 All Day Uilenkraalsmond Resort Gansbaai Alien Hacking 19 9:00 Fynb... | [ ] | [ ] |
| when | 2026-11-18 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| category | community | (the model's choice from the list; no quote) | [ ] | [ ] |

## 13. Christof van der Berg: Stories & Sterre (id 71)

Source: https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf

- kind `event` · category `talks and workshops` · town `Kleinmond` · venue `NG Kerksaal, 1ste laan` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-25` to `2026-11-25` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Christof van der Berg: Stories & Sterre | ...sbaai Foraging Experience & Feast 24 9:00 - 14:00 Edible Shores Pringle Bay Full Moon Cycle & Walk 24 19:00 422 Crescent Street Pringle Bay **Christof van der Berg: Stories & Sterre** 25 19:00 NG Kerksaal, 1ste laan Kleinmond Alien Hacking 26 9:00 Fynbos Centre, Pearly Beach Gansbaai Nativity Play 26 10:00 Camphill School... | [ ] | [ ] |
| town | Kleinmond | ... Edible Shores Pringle Bay Full Moon Cycle & Walk 24 19:00 422 Crescent Street Pringle Bay Christof van der Berg: Stories & Sterre 25 19:00 **NG Kerksaal, 1ste laan Kleinmond** Alien Hacking 26 9:00 Fynbos Centre, Pearly Beach Gansbaai Nativity Play 26 10:00 Camphill School Hall Hermanus [page 2] For a more detaile... | [ ] | [ ] |
| venue | NG Kerksaal, 1ste laan | ... Edible Shores Pringle Bay Full Moon Cycle & Walk 24 19:00 422 Crescent Street Pringle Bay Christof van der Berg: Stories & Sterre 25 19:00 **NG Kerksaal, 1ste laan** Kleinmond Alien Hacking 26 9:00 Fynbos Centre, Pearly Beach Gansbaai Nativity Play 26 10:00 Camphill School Hall Hermanus [page 2] For a mo... | [ ] | [ ] |
| when | 2026-11-25 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| category | talks and workshops | (the model's choice from the list; no quote) | [ ] | [ ] |

## 14. Grip Gymnastics and Dance Concert (id 98)

Source: https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf

- kind `event` · category `music and shows` · town `Hermanus` · venue `Road House Cinema` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-28` to `2026-11-29` (day; 2 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Grip Gymnastics and Dance Concert | ...ma: Raiders of the Lost Ark 28 19:30 The Amphitheatre @ Landskein Wines Stanford The King of Pop Experience 28 20:00 Sandbaai Saal Hermanus **Grip Gymnastics and Dance Concert** 28 & 29 10:00 Road House Cinema Hermanus Practice Walk 29 7:00 Voelklip Hermanus Overberg Toy Run 29 09:00 - 14:00 Birkenhead Brewery Stanf... | [ ] | [ ] |
| town | Hermanus | ...unset Soiree 28 18:00 High Season Farm Hermanus Secret Sunrise 28 19:00 Grotto Beach Hermanus Stand up Comedy: Alan Committie Live 28 19:30 **Road House Cinema Hermanus** Open Air Cinema: Raiders of the Lost Ark 28 19:30 The Amphitheatre @ Landskein Wines Stanford The King of Pop Experience 28 20:00 Sandbaai ... | [ ] | [ ] |
| venue | Road House Cinema | ...unset Soiree 28 18:00 High Season Farm Hermanus Secret Sunrise 28 19:00 Grotto Beach Hermanus Stand up Comedy: Alan Committie Live 28 19:30 **Road House Cinema** Hermanus Open Air Cinema: Raiders of the Lost Ark 28 19:30 The Amphitheatre @ Landskein Wines Stanford The King of Pop Experience 28 20:00 ... | [ ] | [ ] |
| when | 2026-11-28 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| when | 2026-11-29 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| category | music and shows | (the model's choice from the list; no quote) | [ ] | [ ] |

## 15. The Blending Table: Create your own wine (id 101)

Source: https://whalecoast.info/wp-content/uploads/2022/06/Tourism-November-Events-181126.pdf

- kind `event` · category `food and wine` · town `Hermanus` · venue `Benguela Cove` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-11-29` to `2026-11-29` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | The Blending Table: Create your own wine | ...& 29 10:00 Road House Cinema Hermanus Practice Walk 29 7:00 Voelklip Hermanus Overberg Toy Run 29 09:00 - 14:00 Birkenhead Brewery Stanford **The Blending Table: Create your own wine** 29 11:00 - 13:30 Benguela Cove Hermanus Oysters & Bubbles 29 12:00 The Parlour Landskein Wines Stanford Singles’ Night 29 17:00 Ficks Herma... | [ ] | [ ] |
| town | Hermanus | ...0 Voelklip Hermanus Overberg Toy Run 29 09:00 - 14:00 Birkenhead Brewery Stanford The Blending Table: Create your own wine 29 11:00 - 13:30 **Benguela Cove Hermanus** Oysters & Bubbles 29 12:00 The Parlour Landskein Wines Stanford Singles’ Night 29 17:00 Ficks Hermanus Youth Christmas Carol Festival 29 17... | [ ] | [ ] |
| venue | Benguela Cove | ...0 Voelklip Hermanus Overberg Toy Run 29 09:00 - 14:00 Birkenhead Brewery Stanford The Blending Table: Create your own wine 29 11:00 - 13:30 **Benguela Cove** Hermanus Oysters & Bubbles 29 12:00 The Parlour Landskein Wines Stanford Singles’ Night 29 17:00 Ficks Hermanus Youth Christmas Carol Festi... | [ ] | [ ] |
| when | 2026-11-29 | ...November For a more detailed calendar please visit https://whalecoast.info/events-calendar/ * Saturdays: ParkRun at 8:00; Markets from 9:00 **Events 2026** tourism@overstrand.gov.za \| www.whalecoast.info Events November Dates Time Venue Town Ceramic Exhibition Rooted from Earth to Art 14 - 22 1... | [ ] | [ ] |
| category | food and wine | (the model's choice from the list; no quote) | [ ] | [ ] |

## 16. Baardskeerdersbos Art Route (id 110)

Source: https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf

- kind `event` · category `art and exhibitions` · town `Gansbaai` · venue `not stated` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-03-27` to `2026-03-29` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Baardskeerdersbos Art Route | ....co.za to Danger Point Lighthouse 18 March Cape 1000 Classic Cars Burgundy Restaurant, Hermanus Hermanus Peter I 082 443 3425 27 - 29 March **Baardskeerdersbos Art Route** Gansbaai www.baardskeerdersbosartroute.co.za 3 - 6 April Greenpop’s Reforest Festival Gansbaai www.greenpop.org 4 - 6 April Franskraal Art ... | [ ] | [ ] |
| town | Gansbaai | ...use2lighthouse.co.za to Danger Point Lighthouse 18 March Cape 1000 Classic Cars Burgundy Restaurant, Hermanus Hermanus Peter I 082 443 3425 **27 - 29 March Baardskeerdersbos Art Route Gansbaai** www.baardskeerdersbosartroute.co.za 3 - 6 April Greenpop’s Reforest Festival Gansbaai www.greenpop.org 4 - 6 April Franskraal Art Route Gan... | [ ] | [ ] |
| when | 2026-03-27/2026-03-29 | ...use2lighthouse.co.za to Danger Point Lighthouse 18 March Cape 1000 Classic Cars Burgundy Restaurant, Hermanus Hermanus Peter I 082 443 3425 **27 - 29 March Baardskeerdersbos Art Route Gansbaai** www.baardskeerdersbosartroute.co.za 3 - 6 April Greenpop’s Reforest Festival Gansbaai www.greenpop.org 4 - 6 April Franskraal Art Route Gan... | [ ] | [ ] |
| category | art and exhibitions | (the model's choice from the list; no quote) | [ ] | [ ] |

## 17. Pam Golding Hangklip Marathon (id 129)

Source: https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf

- kind `event` · category `sport to take part` · town `Kleinmond` · venue `not stated` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-10-25` to `2026-10-25` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Pam Golding Hangklip Marathon | ...manus Whale Festival Hermanus www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 25 Oct **Pam Golding Hangklip Marathon** Kleinmond www.hangklipmarathon.co.za Oct Kleinmond Ceramic Festival Kleinmond kleinmondceramicfestival@gmail.com 6 Nov - 15 Nov Wines2Whale... | [ ] | [ ] |
| town | Kleinmond | ...Oct Hermanus Whale Festival Hermanus www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 **25 Oct Pam Golding Hangklip Marathon Kleinmond** www.hangklipmarathon.co.za Oct Kleinmond Ceramic Festival Kleinmond kleinmondceramicfestival@gmail.com 6 Nov - 15 Nov Wines2Whales Hermanus... | [ ] | [ ] |
| when | 2026-10-25 | ...Oct Hermanus Whale Festival Hermanus www.hermanuswhalefestival.co.za 3 Oct Wine & Cheese Festival Stanford Walker Bay Estate I 028 341 0183 **25 Oct Pam Golding Hangklip Marathon Kleinmond** www.hangklipmarathon.co.za Oct Kleinmond Ceramic Festival Kleinmond kleinmondceramicfestival@gmail.com 6 Nov - 15 Nov Wines2Whales Hermanus... | [ ] | [ ] |
| category | sport to take part | (the model's choice from the list; no quote) | [ ] | [ ] |

## 18. Hermanus Art in the Park (id 141)

Source: https://whalecoast.info/wp-content/uploads/2022/06/OM-Cape-Whale-Coast-Events-070826-1-1.pdf

- kind `season` · category `market` · town `Hermanus` · venue `Hermanus Country Market` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2026-01-01` to `2028-12-31` (month; 3 rows; written by code from a season with no year)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Hermanus Art in the Park | ...ansbaai, Harold Porter Betty’s Bay, Hemel-en-Aarde and Benguela Cove Hermanus. * Hermanus First Friday Artwalk – 1st Friday of the month. * **Hermanus Art in the Park** at Hermanus Country Market venue 1st Sunday of the month. * Farmers, Saturday and Night Markets held at various locations. * Link to www.wh... | [ ] | [ ] |
| town | Hermanus | ...ansbaai, Harold Porter Betty’s Bay, Hemel-en-Aarde and Benguela Cove Hermanus. * Hermanus First Friday Artwalk – 1st Friday of the month. * **Hermanus Art in the Park at Hermanus Country Market venue** 1st Sunday of the month. * Farmers, Saturday and Night Markets held at various locations. * Link to www.whalecoast.info/events-calendar/ fo... | [ ] | [ ] |
| venue | Hermanus Country Market | ...ansbaai, Harold Porter Betty’s Bay, Hemel-en-Aarde and Benguela Cove Hermanus. * Hermanus First Friday Artwalk – 1st Friday of the month. * **Hermanus Art in the Park at Hermanus Country Market venue** 1st Sunday of the month. * Farmers, Saturday and Night Markets held at various locations. * Link to www.whalecoast.info/events-calendar/ fo... | [ ] | [ ] |
| when | months 01 to 12 | ...guela Cove Hermanus. * Hermanus First Friday Artwalk – 1st Friday of the month. * Hermanus Art in the Park at Hermanus Country Market venue **1st Sunday of the month**. * Farmers, Saturday and Night Markets held at various locations. * Link to www.whalecoast.info/events-calendar/ for updated info on events... | [ ] | [ ] |
| category | market | (the model's choice from the list; no quote) | [ ] | [ ] |

## 19. Hermanus Adventure Week (id 146)

Source: https://xplorio.com/hermanus/en/things-to-do/events

- kind `season` · category `festival` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `yes` · below the traveller bar `no`
- when: `2027-09-01` to `2028-09-30` (month; 2 rows; written by code from a season with no year)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | Hermanus Adventure Week | ...d this is one time you can feast on it all at a most affordable price. Entertainment, music and craft stalls add to the festive atmosphere. **The Hermanus Adventure Week** is a new annual addition to the festival calendar and it is held in September. It caters for the active with mountain bike races, night and... | [ ] | [ ] |
| town | Hermanus | ...d this is one time you can feast on it all at a most affordable price. Entertainment, music and craft stalls add to the festive atmosphere. **The Hermanus Adventure Week is a new annual addition** to the festival calendar and it is held in September. It caters for the active with mountain bike races, night and day runs, a triathlon an... | [ ] | [ ] |
| yearly | yes | ...on it all at a most affordable price. Entertainment, music and craft stalls add to the festive atmosphere. The Hermanus Adventure Week is a **new annual addition** to the festival calendar and it is held in September. It caters for the active with mountain bike races, night and day runs, a triathlon an... | [ ] | [ ] |
| when | months 09 to 09 | ...nt, music and craft stalls add to the festive atmosphere. The Hermanus Adventure Week is a new annual addition to the festival calendar and **it is held in September**. It caters for the active with mountain bike races, night and day runs, a triathlon and a harbour swim. There are several calmer events and... | [ ] | [ ] |
| category | festival | (the model's choice from the list; no quote) | [ ] | [ ] |

## 20. FynArts Old Harbour Sunset Concert (id 150)

Source: https://www.hermanusfynarts.co.za/

- kind `event` · category `music and shows` · town `Hermanus` · venue `not stated` · price `not stated` · held each year `no` · below the traveller bar `no`
- when: `2027-03-06` to `2027-03-06` (day; 1 rows; stated on the page)

| Fact | Value | Quote, in the page text | True | False |
|---|---|---|---|---|
| title | FynArts Old Harbour Sunset Concert | ...ul coastal town. events Where Art Comes Alive throughout the Year Save the Dates: FynArts Select: Masters and Makers: 20 – 22 November 2026 **FynArts Old Harbour Sunset Concert:** 6 March 2027 FynArts Festival: 24 June 2027 – 4 July 2027 Since 2013, Hermanus FynArts has been celebrating the best of South African creat... | [ ] | [ ] |
| town | Hermanus | (no quote: registry default) | [ ] | [ ] |
| when | 2027-03-06 | ...mes Alive throughout the Year Save the Dates: FynArts Select: Masters and Makers: 20 – 22 November 2026 FynArts Old Harbour Sunset Concert: **6 March 2027** FynArts Festival: 24 June 2027 – 4 July 2027 Since 2013, Hermanus FynArts has been celebrating the best of South African creativity in one ... | [ ] | [ ] |
| category | music and shows | (the model's choice from the list; no quote) | [ ] | [ ] |

