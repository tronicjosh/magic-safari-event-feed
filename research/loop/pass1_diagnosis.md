# Pass 1: diagnosis

16 new questions (`pass1_questions.json`), answers in `pass1_answers.json`, judged in
`pass1_eval_a.json` and `pass1_eval_b.json`. Cost 1.005900 US dollars.

Verdicts: 3 good, 10 minor, 3 fault. No link, price or item from outside the feed. Each
"the feed has nothing" came after `find` and was true. Each tag had the exact words. The
headings for each interest were used.

| # | Fault (answers) | Cause | Repair |
|---|---|---|---|
| D1 | The short card has no venue and no time. The designer cannot act on "no night driving", "wheelchair", "is it at Fernkloof"; the agent guessed "running race", "food" (5, 11, 12, 13, 14) | Tool text: venue and time are only in `tell_me_more`, which rule 10 limits to proof | `feed/read.py`: the short card gives the venue and the time when the feed has them |
| D2 | A rule by month ("first Friday of every month") is listed in each window, with no word on its day. The agent does the calendar work in silence (0, 2, 5, 7, 11, 15) | Tool text, and rule 4 forbids what the designer needs | Instructions: the agent can say which day the rule gives in the trip, marked "by the rule", or that the day is outside the trip. The tag does not change |
| D3 | 130 to 165 words in 9 answers | Instructions conflict: 6 item lines with links do not fit in 120 words | Instructions: 6 item lines or less; the text outside the item lines is 60 words or less. The runner measures that |
| D4 | The agent wrote proposal text "Expected 1-3 October 2027" for a "not confirmed" item when the designer pushed (4) | Instructions: "never give it a date" did not cover a draft or an estimate | Instructions: no date in any form, also not as an estimate or as text for a proposal; give "dates to be confirmed" and the last real dates |
| D5 | Guesses about Quicket and Webtickets: "may list the dates", "might list the price" (3, 4, 6) | Instructions: no rule | Instructions: say only that the feed does not cover them |
| D6 | Items put under an interest that their card does not show: two general markets under "food" (2); flower fairs under "wild flowers"; "a separate event" with no proof (13) | Instructions: no rule | Instructions: an item goes under an interest only if its card shows it (title, category, venue). Do not say that two cards are one event or two events unless a card says so |
| D7 | A past item has no tag, or the tag "Confirmed" (13, 14) | Instructions 2 and 9 conflict | Instructions: a seventh tag, "Past, not known if held again" |
| D8 | "5 of 18" from two tool results joined (13); "nothing in these dates" when the feed has nothing at all (2) | Instructions: no rule | Instructions: the count comes from one response; say if the feed has nothing at all, or nothing in these dates |
| D9 | An offer that the feed cannot fill: "other shows that have a stated price" (6); a filler paragraph after a refusal (11) | Instructions | Instructions: offer only what a tool can return |

Not repaired, and why:
- Two cards for one event with different titles (ids 7 and 147; 2 and 116; 34 and 149): open
  decision O1 of the design, kept by Joshua. D1 helps: the venue now shows on both cards.
- "last year's" for September 2026 (13): a slip of the agent, one time.
