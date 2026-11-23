# Pass 2: diagnosis

12 new questions (`pass2_questions.json`), answers in `pass2_answers.json`, judged in
`pass2_eval_a.json` and `pass2_eval_b.json`. Cost 0.767801 US dollars.

Verdicts: 1 good, 9 minor, 2 fault (pass 1: 3 good, 10 minor, 3 fault of 16). No item, date,
price, venue or link from outside the feed on an item line. Each tag exact; each count from
one response; each "the feed has nothing" true and after `find`. The agent refused to answer
from memory, corrected two wrong facts of a designer, and refused a whale percentage.
Not seen again: D2, D4 (as a written date), D5 (Quicket), D7, D8.

## The length fault came back: the approach was wrong

D3 was repaired in pass 1 with a limit (60 words outside the item lines). In pass 2, 9 of 12
answers are over it, and the judges found most of those answers good to act on. Two rounds
with the same type of fault: the limit is the wrong tool. The cause is that rules 12 and 13
demand three closing lines (left out, not covered, an offer) after each answer, also after a
check of an itinerary, a yes or no, or a request for one sentence. The repair is to ask for
less text, not to count it: closing lines only after a list for a trip; the shape that the
designer asks for (one sentence, a table, an email, "all of them") wins over the default.

| # | Fault (answers) | Cause | Repair |
|---|---|---|---|
| E1 | 74 to 109 words outside the items (0, 1, 2, 3, 4, 6, 7, 8, 11); 7 sentences for "one sentence" (4); "I can show six per answer" for "give me all" (11) | Instructions: fixed closing lines for each answer; a cap that the designer cannot lift | Instructions: the designer's shape wins; closing lines only after a list for a trip; "all" gives all, as compact lines |
| E2 | "The only 2027 event with a stated date is FynArts": false, a dated concert on 6 March 2027 exists (4). The window 13 to 27 May 2028 shows two Saturdays and no word that code wrote dates only to 20 May (3) | Tool text: `when_to_go` does not say that it leaves out one-off events; the horizon note is written only when the whole window is after the last rule date | `feed/read.py`: a note in `when_to_go` (seasons, weekly and yearly items only; for dated events call `what_is_on` or `find`); the horizon note also when the window crosses the last rule date |
| E3 | "I can't tell you what is free": the feed holds the page quote "Join us for a free, timed 5km run/walk" for a parkrun, but only on the full card; `find` "free" gives 0 (9) | Tool text: `find` does not search the quotes | `feed/read.py`: `find` also matches a whole word in a stored quote of the item, and the card shows that quote |
| E4 | "Where does the data come from, how fresh is it?": the agent named 5 of 8 sources, gave site roots that no tool returned, and guessed the age of a PDF from its file name (8) | Tool text: no tool gives the sources and the date of the collection | `feed/read.py`: one line in each list response: the sources, with the date of the last collection |
| E5 | One exhibition on two lines from two cards with like titles (1); a business dinner under "Golf" because of its venue (5) | Instructions: rule 10, the letter against the purpose | Instructions: interest from title or category only; two cards with the same dates and town and like titles get one line with both sources, as "listed two times" |
| E6 | Words that no card holds, in free text: "boat-based", "a food and wine evening", "the new date", "may be from August" (1, 2, 6, 8) | Instructions: rule 2 names items and facts, not describing words | Instructions: also a describing word must be on a card, in a list, in free text and in an email |
| E7 | Offers that a tool cannot fill: "wording about early June", a search for "massage" (2, 5) | Instructions: D9 was too weak | Instructions: offer only the proof of an item, or a thing that a response of this conversation showed |
| E8 | "The feed doesn't rank anything", then a selection (4); "4 of 46" above 5 lines (0) | Instructions and a slip | Instructions: asked for the best, select and give the reason in a few words; no lecture about the feed |

The runner now measures each turn, not only the last one.
