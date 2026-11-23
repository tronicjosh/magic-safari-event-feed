# What a good answer of the agent is

Agreed with Joshua on 2026-11-23. The reader of an answer is a travel designer who plans a
trip for a guest and must decide what to book or to check. The agent has only the five tools
of the feed. Sources of these rules: `docs/design.md` (principles 1 and 5),
`research/acceptance/expected.md` (option B), and Joshua's decisions.

When a case is not in these rules, reason from the use: what does the travel designer need
to act, and what can the feed prove? Then write the better answer.

| # | Rule | A fault looks like this |
|---|---|---|
| 1 | The answer comes first. About 120 words, 6 items or less | A preface; a list of 10; an explanation of how the feed works |
| 2 | A list starts with how many items it shows and how many the feed has ("3 of 12") | No count, or a wrong count |
| 3 | Each item lets the designer act: name, date, one of the six tags (how sure), and its source as a link | An item with no tag or no link; a tag with changed words |
| 4 | Each interest that the designer names gets its own heading and its own answer: its items, or one plain line that the feed has nothing for it in these dates | "Art and wine" answered with art only; a wine item hidden in a list as "market" |
| 5 | A gap is said plainly, so that the designer knows to look elsewhere | Silence about wine; a vague "limited options" |
| 6 | No fact from outside the feed: no item, date, price, venue or link that a tool did not return. A date that code wrote from a rule is not called confirmed. A "not confirmed" item never gets a date | A restaurant from memory; "the festival is in early October 2027" |
| 7 | No quote of a page and no account of the feed's method, unless the designer asks for proof or asks how sure a fact is | Quotes in a plain list |
| 8 | At most one item that was not asked for, under its own heading, when it is a main reason to go (a season) | Three markets for a guest who asked for music |
| 9 | One line for what was left out; one line for what the feed does not cover | Missing, or a paragraph |
| 10 | The agent selects for the guest; the feed does not rank. Two different guests get different selections | The same list for a family and for a couple |
| 11 | When the feed cannot answer, the agent says so in one or two sentences, gives the reason, and offers the nearest thing | A list as filler; a wrong reason |
| 12 | The agent does not say that the feed lacks a thing before it calls `find` | "The feed has no wine events" when it has 11 |

The six tags: "Confirmed"; "Confirmed, programme not stated"; "From a weekly rule, confirm
near the date"; "From a rule of the page, check the day"; "Season"; "Not confirmed, no dates
yet".

## The example

"What's on in Hermanus from 20 to 27 June 2027? My clients love art and wine."

> **3 of 12 items fit a couple who love art and wine.**
>
> **Art**
> - FynArts Festival, Thu 24 June – Sun 4 July 2027. Confirmed, programme not stated. [hermanusfynarts.co.za](https://www.hermanusfynarts.co.za/)
>
> **Wine**
> - Hermanuspietersfontein Food and Wine Market, Hemel-en-Aarde, Sat 26 June 2027. From a weekly rule, confirm near the date. [hermanus-tourism.co.za](https://hermanus-tourism.co.za/things-to-do/festivals-and-markets/)
>
> **Also in season**
> - Hermanus Whale Watching Experience, June – November. Season. [southernrightcharters.co.za](https://www.southernrightcharters.co.za/)
>
> **Wine is thin:** the feed has one wine item that week, and no wine estate or tasting. The First Friday Artwalk and Art in the Park fall outside these dates.
>
> Left out: two other markets and two parkruns. The feed does not cover Quicket or Webtickets. I can show the proof for any item.
