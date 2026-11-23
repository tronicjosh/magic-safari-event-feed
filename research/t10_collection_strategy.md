# T10 - Collection strategy: access paths and failure detection

Date of the requests: 2026-11-23. Budget used: 41 of 45 (41 direct HTTP requests with `curl`, 0 searches). All results below are from raw responses (status, headers, body), not from a fetch tool that summarises.

## 1. Result in 6 lines

1. A better access path than the HTML page exists for 7 of the 11 event sources. The owner's direction is correct: a registry of targeted sources, each with its own access path, is better than one large scrape.
2. The largest find is Quicket: its site search is a JSON search service that gives a total count (`nbHits`), dates as numbers, and coordinates. A 60 km geo query gave 136 hits; T1 reached 5 Quicket events. The official API needs a key (HTTP 401 without one).
3. The PDF problem is solved: `whalecoast.info/wp-json/wp/v2/media` lists the newest files with upload dates. It showed a PDF (`...-181126.pdf`, uploaded today) that T1 did not have.
4. Three "truncation" problems were tool effects or wrong URLs, not site limits: AllEvents embeds the full list as JSON in the raw page (45 + 4 items); Wesgro paginates by path (`/events/p2`), not by `?page=2`; Benguela Cove is a Shopify shop with `/products.json` (dates and prices in one request, no HTTP 429).
5. No headless browser is necessary for the first 6 sources. It is necessary only for: Webtickets search, live availability in ActivityBridge / Activitar / Dineplan, and sites behind a Cloudflare challenge. Recommendation: do not build it now; register those sources as "not collected" so that the gap is visible.
6. Zero errors is not possible. The design goal is: each loss causes a named signal in the run report. 12 checks in section 4 do this. One decision is for the owner: Quicket through the official API key or through the site search service (section 6).

## 2. Access paths per source, with evidence

Status codes are from this session. "Best path" is the recommended one.

### 2a. Event sources

| Source | URL tried | Status | What came back | Best path |
|---|---|---|---|---|
| Overstrand Tourism PDFs (OT) | `https://whalecoast.info/wp-json/wp/v2/media?search=Events&mime_type=application/pdf&per_page=10&orderby=date&order=desc&_fields=id,date,source_url` | 200 JSON | 10 rows, newest first: `2026-11-23T10:52:40 Tourism-November-Events-181126.pdf`, then `...-111126.pdf`, `...-031126.pdf`. Header `X-WP-Total: 158` | **Media API, then PDF text.** Stable URL; the file name is data, not a guess |
| OT annual PDF | `.../wp-json/wp/v2/media?search=Cape-Whale-Coast-Events&per_page=5&orderby=date&order=desc` | 200 JSON | Newest: `OM-Cape-Whale-Coast-Events-070826-1-1.pdf` (2026-08-08); older issues 2025-08, 2025-04 | Media API, then PDF text |
| OT PNG diary | `.../wp-json/wp/v2/media?per_page=20&orderby=date&order=desc` | 200 JSON | `image/png`, title "Overstrand Tourism Diary 11 – 15 Nov 2026" | Not needed: the same office publishes the text in the weekend page (next row). OCR not tested |
| OT events calendar | `https://whalecoast.info/wp-json/tribe/events/v1/events` | 404 | `rest_no_route`. The page `/events/` redirects to `/events-calendar/`: "No posts were found." | None. Use the media API |
| Overstrand weekend page | `https://www.overstrand.gov.za/wp-json/wp/v2/pages/33987?_fields=id,modified,title,content` | 200 | JSON with `modified: 2026-11-20T16:36:22` and the full list ("Wednesday 18th November 2026 ... Bring & Braai 17:30 Hangklip Hotel Pringle Bay"). **3,346 bytes of `<style>` come before the JSON**; a plain JSON parse fails | **Page API** (strip the text before the first `{"id"`). Full dates with year; `modified` gives freshness. HTML page has no `Event` JSON-LD |
| Hermanus Tourism (HT) | `https://hermanus-tourism.co.za/wp-json/wp/v2/types`; `.../tribe/events/v1/events`; `.../wp/v2/pages?slug=festivals-and-markets&_fields=id,modified,link` | 200; 404; 200 | No event post type (post, page, product, popup...). Festivals page `modified: 2026-08-08` | HTML or page API. Low value: prose, last changed in August. Use `modified` as a staleness signal |
| Quicket search page | `https://www.quicket.co.za/events/?q=hermanus` | 200 | 27,780 bytes, an Angular shell (`<app-browse-events>`), no events | Not usable |
| Quicket official API | `https://api.quicket.co.za/api/events?pageSize=5&page=1` | 401 | "You need an API key to use this API. Please register at http://developer.quicket.co.za" | Needs a key. Portal page (200) says to register; terms page not read |
| Quicket site search service | `POST https://QAUIPDMSEL-dsn.algolia.net/1/indexes/products/query` body `{"query":"hermanus","hitsPerPage":100}` | 200 JSON | `nbHits: 28, nbPages: 1`. Fields: `ProductName, ProductUrl, DateFrom, DateTo, Dates[]` (Unix seconds), `VenueName, City, Region, _geoloc{lat,lng}, Organiser, LastModified, Indefinite, Type` | **Best event path found.** Uses the app id and the search-only key that the site sends to each browser (in `/app-elements/main.*.js`; the key is not copied here). Owner decision, section 6 |
| Quicket geo query | same endpoint, `{"query":"","aroundLatLng":"-34.4187,19.2345","aroundRadius":60000,"numericFilters":["DateTo>now"]}` | 200 JSON | `nbHits: 136, nbPages: 2`. First 100: Cape Town 36, Kleinmond 15, Hermanus 15, Pringle Bay 11, Stanford 5, Gansbaai 3, others. Keyword and geo sets: 19 in both, 9 keyword only | Use **both** queries (geo + town keywords), union on `objectID` |
| Quicket event page | `https://www.quicket.co.za/events/395886-rosoberry-harvest-fest-2026/` | 200 | JSON-LD `Event`: `startDate 2026-11-28T08:00:00Z`, `eventStatus`, 3 `Offer` (200.0, 70.0, 0.0 ZAR, `InStock`) | JSON-LD for price and status of each hit |
| AllEvents (AE) list | `https://allevents.in/hermanus/all` | 200 | Raw HTML embeds `_this.events_data = [{...}]`: 45 objects with `event_id, eventname, start_time` (Unix), `start_time_display, venue{city, latitude, longitude, full_address}`. No `Event` JSON-LD | **Embedded JSON.** "more events omitted" was the fetch tool, not the site |
| AE page 2 | `https://allevents.in/hermanus/all?page=2` | 200 | `current_page=2`, 4 objects in `events_data`; the page also links 6 events of page 1 | `?page=N`; count only `events_data`, stop when it has 0 new `event_id` |
| AE internal API | `POST https://allevents.in/api/events/list` (city, country, page, rows) | 200 | `{"message":"invalid_request","error":1,"data":[]}`. The page sends a header `X-Client-State` from a script variable | Not usable without a browser token. Not needed |
| Wesgro (WG) | `https://www.wesgro.co.za/travel/events?q=hermanus` then `https://www.wesgro.co.za/travel/events/p2?q=hermanus` | 200; 200 | 24 event links on each page, **0 overlap**. Page 2 links to `p3`, `p4`. `q=hermanus` does not limit the list to Hermanus (page 1 has "taste-of-cape-town") | **Path pagination `/events/pN`**. Filter by place in code. Detail page: no `Event` JSON-LD, date as text ("5 Dec 2026") |
| Webtickets search | `https://www.webtickets.co.za/v2/search.aspx?searchterm=hermanus` | 200 | 50 KB ASP.NET WebForms page (`__VIEWSTATE`, Queue-Fair script), no results in the HTML. `js/webtickets.js` (200) has no search endpoint (`/api/basket/` only) | **No path found.** Browser necessary, or use known event URLs |
| Webtickets event page | `https://webtickets.co.za/Hermanusrotary` | 200 | Redirects to `/v2/event.aspx?itemid=1604981085`. No JSON-LD | HTML text of known URLs only |
| FynArts (Wix) | `https://www.hermanusfynarts.co.za/event-list` | 200 | No JSON-LD. Script `wix-warmup-data` has `"startDate":"2027-03-06T16:30:00.000Z"`, `"2027-06-24T07:00:00.000Z"`, titles and slugs | **Warmup JSON**: ISO dates with year (solves "no year on the list") |
| Benguela Cove (BC) | `https://benguelacove.co.za/products.json?limit=250` | 200 JSON | Shopify. 138 products; `product_type` Event 13, Experience 17. Variants hold dates and prices: "The Blending Table": `('Sun, 29 Nov 2026', '895.00', available)`, `('Sun, 27 Dec 2026', ...)`. Some variants have no year ("5 December") or no date ("Default Title", 0.00) | **`/products.json`**: one request, no detail pages, no 429 |
| Xplorio (XP) | `https://xplorio.com/hermanus/en/things-to-do/events` | 200 | No JSON-LD, no microdata, no API seen. Dates as text `27/11/2026` | HTML text |
| Stanford Tourism | `https://stanfordinfo.co.za/wp-json/wp/v2/media?per_page=15&orderby=date&order=desc` | 200 JSON | `X-WP-Total: 2512`. Newest: opening-hours PNG, restaurant list PDF, "Stanford-in-Bloom festival guide" PDF (2026-09-03). No weekly event file | Media API as a change detector only. Stanford events come through OT |
| Whale Festival, Kalfiefees | `https://hermanuswhalefestival.co.za/`, `https://kalfiefees-hermanus.co.za/` | 200; 200 | WordPress. JSON-LD has WebSite / Organization / Place, no `Event`. Kalfiefees title: "5-10 Augustus 2026" | HTML text, one page each, once a week |
| gotrail.run | `https://gotrail.run/trail-running-calendar/south-africa/western-cape/hermanus` | 403 | `Cf-Mitigated: challenge`, "Just a moment... Enable JavaScript and cookies" | Blocked. Browser necessary. Do not collect |

### 2b. Experience sources

| Source | URL tried | Status | What came back | Best path |
|---|---|---|---|---|
| Activitar (Marine Dynamics) list | `https://marinedynamics.activitar.com/products` | 200 | Server HTML. 24 service links with stable ids (`/services/986?adults=1&children=0&date=2026-11-26`), names ("Shark Cage Diving", "Marine Big 5 Tour - Hermanus Return"). No price in the text except a promotion ("R1500 p/p") | HTML list: names and ids, as a check that the product still exists |
| Activitar service page | `https://marinedynamics.activitar.com/services/986?adults=1&children=0&date=2026-11-26` | 200 | Description text ("All trips are weather and tide dependant..."). **No price, no time slots in the static HTML**, no JSON endpoint seen | Price and availability: widget only. Take the price from the operator page |
| ActivityBridge | `https://secure.activitybridge.com/book?action=book&activityid=372` | 200 | 90 KB, 220 characters of visible text ("Step 1 ... Busy"). Data loads after `Booking.init()` | Widget only. Keep as booking link |
| Dineplan | `https://account.dineplan.com/widgetframe/9BDzvyr6` | 200 | 20 KB script shell, no slots as text | Widget only. Keep as booking link |
| Benguela Cove experiences | `products.json` (row above) | 200 | 17 products of type Experience with prices | `/products.json` |
| Bouchard Finlayson | `https://bouchardfinlayson.co.za/` | 200 | Loads with browser-type headers (T9 had 403 through the fetch tool) | HTML text |
| Southern Right Charters | `https://www.southernrightcharters.co.za/` | 200 | HTML; booking link `activityid=372` found in the page | HTML text + booking link |

Not tested in this session: Computicket, TIXSA, Q2B, SA-Venues, hermanus.co.za, Bandsintown, running.life, the Mailchimp archive of Stanford, sitemaps, iCal and RSS feeds, PDF text extraction of the 18 Nov PDF (T1 proved it for 2 PDFs), OCR of the PNG.

## 3. Strategy

### 3a. Registry, not open web discovery

Use one registry file (one row for each source: id, town, type, access path, URL template, pagination rule, expected minimum count, trust level, status). Reasons from the evidence:

- The reliable path is different for each site (media API, page API, search JSON, embedded JSON, Shopify JSON, Wix JSON). A general crawler cannot find these.
- A completeness check needs a known list: "source X gave 0" is only an error if X is registered and had items before.
- T1: 89 of 112 events are in one source only. Coverage comes from more registered sources, not from a wider query to one source.

Open web search is not a collection layer. It is a separate, slow discovery step (L6): new organisers and venues from Quicket (`Organiser`, `VenueName`) and AllEvents go to a candidates list, and a person approves each new registry row.

### 3b. Diagram

```
 registry.yaml  (one row per source: path, URL, paging rule, min count, status)
      |
      v
 L1 LOCATE      newest file / list of pages          fail: no file, file older than N days
      |         (media API, pN links, nbPages)
      v
 L2 FETCH       1 request per 2 s per site,          fail: status not 200, short body,
      |         3 tries, backoff; raw bytes saved          challenge page, timeout
      v
 L3 PARSE BY PATH (best first, per source)
      |   A structured JSON   Quicket search, Shopify products.json,
      |                       AllEvents events_data, Wix warmup, WP pages API
      |   B JSON-LD Event     Quicket event pages (price, status)
      |   C HTML text         Xplorio, Wesgro, festivals, operator pages
      |   D PDF text          Overstrand monthly + annual PDF
      |   (E browser)         NOT BUILT: Webtickets search, booking widgets,
      |                       Cloudflare sites -> status "not collected"
      v                                               fail: 0 items, schema key missing
 L4 COMPLETENESS GATE   count vs declared total, vs last week,
      |                 repeated page hash, round number, date window
      v                                               fail: named check, source marked
 [fixed pipeline]  visible text -> content hash -> model extracts with quotes -> code verifies
      |
      v
 L5 RUN REPORT   one row per source: OK / WARN / FAIL / NOT COLLECTED + reason + counts
      |          a failed source keeps last week's items, marked "stale since <date>"
      v
 L6 DISCOVERY (monthly, human approves)  new organisers / venues -> candidates -> registry
```

### 3c. Layers

| Layer | What it does | Sources | Failure signal |
|---|---|---|---|
| L1 Locate | Finds the current document: newest PDF from the media API; list of pages from pagination links or `nbPages` | OT PDFs, Wesgro, AllEvents, Quicket | No file matches the pattern; newest file is older than 9 days (weekly sheet) or 400 days (annual); page list is empty |
| L2 Fetch | Polite fetch, raw bytes kept on disk with status and headers | all | Status not 200; body under a per-source minimum size; body has "Just a moment", "Enable JavaScript", "Access Denied"; content type is not the expected one |
| L3-A Structured JSON | Reads fields direct from JSON; model is not necessary for date and place | Quicket search, BC `products.json`, AE `events_data`, FynArts warmup, Overstrand page API | Expected key not found (`hits`, `products`, `events_data`, `startDate`, `content.rendered`); JSON does not parse |
| L3-B JSON-LD | Reads `Event` blocks for price and status | Quicket event pages | Page from a Quicket hit has no `Event` block |
| L3-C HTML text | Visible text to the model | Xplorio, Wesgro, HT, festival sites, operator pages, Activitar list | Visible text shorter than a per-source minimum; 0 items from a source that had items |
| L3-D PDF text | Text of the PDF; year and month come from the header and the file name | OT monthly and annual | Text length under the minimum (image-only PDF); header month/year not found; header month differs from the file-name date code |
| L3-E Browser | Not built | Webtickets search, ActivityBridge, Activitar prices, Dineplan, gotrail | Always reported as NOT COLLECTED, with the count of known items affected |
| L4 Gate | Completeness checks of section 4 | all | Each check has a name; a failed check sets WARN or FAIL |
| L5 Report | One table for each run; exit code is not 0 if a source is FAIL | all | The report itself: a source with no row is an error (registry rows = report rows) |
| L6 Discovery | Candidates for new sources | Quicket, AE | Number of unknown organisers this month; 0 for 3 months is a signal that discovery is broken |

### 3d. Segmentation and pagination rules

- **Segment by geography first, by keyword second.** Quicket: one geo query (centre of the town, radius 60 km) plus one keyword query for each town name (Hermanus, Onrus, Sandbaai, Stanford, Gansbaai, Kleinmond, Hemel-en-Aarde). Union on `objectID`. Evidence: in the first 100 geo hits, 81 were not in the keyword result; 9 keyword hits were not in those 100. I did not read geo hits 101 to 136, so I do not know if the 9 are there. At least 3 of the 9 are out of area (Knysna, Berea, Cape Town).
- The radius is a straight line, not a drive time. 60 km includes Somerset West (54 km, labelled "Cape Town"). The 45-minute filter must be a later step in code, on coordinates.
- **Stop conditions.** With a declared total (Quicket `nbHits`, `nbPages`; WordPress `X-WP-Total`): stop at the last page, then require collected = declared. Without one (AllEvents, Wesgro): stop when a page adds 0 new ids, or when its hash is equal to an earlier page, or at a hard limit (10 pages) which is itself a WARN.
- **Repeated page.** Hash the sorted list of item ids on each page. An equal hash for two different page numbers is a FAIL ("pagination repeats"), not a stop. This is the Wesgro `?page=2` fault.
- **Page URL from the page.** Take the next-page URL from the pagination links in the response (Wesgro `p2`, `p3`, `p4`), not from a guessed parameter. Note: Wesgro also prints a wrong link `p2?q=hermanus?q=hermanus`; use only links that parse.
- **Year rule.** For rows with a day only, the year and month come from the PDF header and must agree with the file-name date code (`181126`) and the upload date from the media API. If they disagree: FAIL for that file.

### 3e. Retries, rate limits, failure report

- One request each 2 seconds for each host; at most about 10 requests for each host in a run (Quicket event pages are the exception: one for each new or changed hit).
- 3 tries with waits of 5, 30 and 120 seconds for timeouts, 429 and 5xx. For 429, obey `Retry-After`. No retry for 401, 403, 404: report at once.
- Send normal browser-type headers. Evidence: Bouchard Finlayson gave 200 with them (403 in T9).
- Use `LastModified` (Quicket), `modified` (WordPress) and the content hash to skip unchanged items.
- A failed source never deletes items. Its items stay, marked "stale since <date>", and the report says: source, layer, check name, status code, counts (this week / last week), and the saved response file.

### 3f. How to add a new town

1. Add the town to the registry: name, coordinates, keyword list.
2. The platform sources need no new code: Quicket (new centre point and keywords), AllEvents (`/<town>/all`), Wesgro (same list, new place filter), SA-wide Shopify / WordPress / Wix path types.
3. Probe each local site with the same fixed list as this test: `/wp-json/wp/v2/types`, `/wp-json/wp/v2/media`, `/products.json`, JSON-LD, `wix-warmup-data`, pagination links. The result selects the path type; a new row uses an existing parser.
4. Run once, set the expected minimum counts from that run, then switch the checks on.

## 4. Completeness checks (how a silent loss becomes visible)

| # | Check | Catches | Level |
|---|---|---|---|
| 1 | Collected count = declared total (`nbHits`, `X-WP-Total`, Shopify page not full at 250) | List cut short | FAIL |
| 2 | 0 items from a source that had items last week | Empty page, JavaScript shell, layout change | FAIL |
| 3 | Count less than 50% of the mean of the last 4 runs | Partial list | WARN |
| 4 | Count is exactly a page size or a round number (9, 10, 24, 25, 50, 100, 250) on the last page | Missed next page | WARN |
| 5 | Equal id-list hash on two page numbers | Pagination repeats | FAIL |
| 6 | Hard page limit reached | Loop without end | WARN |
| 7 | Body size or visible-text length under the per-source minimum; block-page words in the body | 403/429 pages that return 200, challenge pages | FAIL |
| 8 | Newest file older than the limit; `modified` older than the limit | Stale PDF, cached API answer, dead page | WARN |
| 9 | Header month/year, file-name date code and upload date disagree | Wrong year on day-only rows | FAIL for the file |
| 10 | Latest event date in a source is before today + 7 days | Source shows only old editions (HT, festival sites) | WARN |
| 11 | Canary: 3 known standing items for each source (for example Hermanus parkrun in OT, The Blending Table in BC) must be found | A parser that returns rows but the wrong ones | FAIL |
| 12 | Cross-source: an in-scope Quicket hit that is in AllEvents but not in the Quicket result, or the reverse for copied titles | Loss in one of the two | WARN |

Each check writes one line to the run report. Registry rows with status "not collected" are printed each week, so the known gaps stay in view.

Errors that stay possible, and their signal: an event that no registered source lists (signal: none; only L6 and the cross-source rate reduce it); a wrong date on the source itself (signal: source contradiction, already seen for Wesgro); a site that changes its JSON shape (signal: check 2 or the missing-key error); a cached API answer (signal: check 8).

## 5. Order of work

Estimated yield is from T1, T9 and this session. "Work" is the parser effort.

| # | Source and path | Evidence of yield | Work |
|---|---|---|---|
| 1 | Quicket search JSON (geo + keywords), then JSON-LD on event pages | 136 hits in 60 km; 42 of the first 100 are in Hermanus, Onrus, Kleinmond, Stanford, Gansbaai or Franskraal; dates, place, coordinates and price are structured; declared total | Low. Blocked only by the owner decision in section 6 |
| 2 | Overstrand monthly PDF through the media API | Largest single source in T1 (75 events, 58 in no other source) | Medium: day-only rows, year from header |
| 3 | Overstrand weekend page through the page API | Same office, full dates with year, 5 days; cross-check for #2 | Low |
| 4 | AllEvents embedded `events_data` | 49 items, 20 in no other source in T1; December coverage | Low. No declared total, so checks 2 to 5 only |
| 5 | Benguela Cove `/products.json` | 13 events + 17 experiences with prices; removes the 429 problem | Low. Dates are in variant titles, some without year |
| 6 | Operator pages for experiences (HTML text) + Activitar list as a canary | 15 pages read in T9; price as text on 7 | Medium: one page each, prices need a quote check |

Later, lower value: Wesgro `p1..pN` (dates disagreed with organisers in 4 of 6 rows in T1), FynArts warmup JSON (2 events), Xplorio HTML, festival sites, Hermanus Tourism.

## 6. Checks, limits and odd results

What I checked and how:
- 41 direct requests with `curl` and browser-type headers. For each row in section 2, I saw the status code and the raw body. Counts (45, 4, 24, 28, 136, 138) come from parsing the saved bodies.
- Pagination: AllEvents pages 1 and 2 and Wesgro pages 1 and 2 were compared by id sets.
- Quicket geo radius: the ranking info gave a largest distance of 59,940 m, so the radius filter works.

What I did not check:
- Quicket API terms of use and the key procedure (only the portal home page was read). Page 2 of the Quicket geo result (hits 101 to 136). If `DateTo>now` removes past events (the count was 136 with and without it).
- AllEvents pages 3 and later; Wesgro pages 3 and 4.
- PDF text of the 18 Nov file; OCR of the PNG; if the PNG has rows that the weekend page does not.
- iCal, RSS and sitemap paths on any site. Computicket, TIXSA, Q2B, SA-Venues, hermanus.co.za.
- A real browser test of Webtickets, ActivityBridge, Activitar and Dineplan. "Widget only" means: not in the static HTML and no endpoint seen in the page scripts that I read.
- Stability over time: each path was seen once, on one day.
- No pipeline code was written. The thresholds in section 4 (50%, 9 days, 10 pages) are proposals, not measured values.

Decision for the owner:
- **Quicket path.** Recommendation: register for the official API key now, and use the site search service until the key and its terms are known, because it is the only tested path that gives a declared total. Alternative: official API only (not tested, needs a key). Alternative: known organiser pages only (T1: 5 events, no completeness check). The site search service uses a search-only key that the site sends to each visitor; it is not a documented public API.

Odd results:
- The first media request (no filter) showed the 16 Nov files as newest. A later filtered request showed `Tourism-November-Events-181126.pdf` uploaded `2026-11-23T10:52:40`. Either the file was uploaded between the two requests, or the first answer was cached. Check 8 covers the second case. Not resolved.
- The Overstrand page API returns `<style>` text before the JSON with content type `application/json`.
- Quicket geo result has an event with `DateFrom` in 2021 (probably a long-running listing). `City` is "Cape Town" for a Somerset West venue. "Sand Bay" and "Onrusrivier" are used for Sandbaai and Onrus: town names need an alias list.
- Wesgro `?q=hermanus` returns province-wide events. Its detail page for the Stanford 100 Miler shows "5 Dec 2026"; T1 recorded "14 Dec 2026" from the list. Not resolved.
- Wesgro prints a broken pagination link (`p2?q=hermanus?q=hermanus`).
- AllEvents page 2 shows 10 event links but only 4 are new list items; the others are repeats in side blocks. Count `events_data`, not links.
- Benguela Cove: several event products have price 0.00 and "Default Title" (no date); `updated_at` is equal for all products (2026-11-23T12:53:43), so it is not a change signal.
- The Activitar list shows "R1500 p/p" in a banner; T9 read "ZAR 1 500.00" as an unlabelled number on the operator page. It is a promotion price, not the standard price.
- Webtickets loads a Queue-Fair script; under load it can send a waiting-room page with status 200. Check 7 must look for it.
